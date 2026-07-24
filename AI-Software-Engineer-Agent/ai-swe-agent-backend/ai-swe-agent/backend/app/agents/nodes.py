"""
LangGraph node functions. Each node is a plain async function:

    (AgentState) -> dict     # a *partial* state update

LangGraph merges the returned dict into the running state and hands the
result to whichever node the graph's edges point to next (see graph.py).
"""

import json
import re
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.prompts import (
    CODER_FIX_SYSTEM_PROMPT,
    CODER_SYSTEM_PROMPT,
    PLANNER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
)
from app.agents.state import AgentState
from app.llm.router import get_llm
from app.sandbox.factory import get_executor


def _event(agent: str, type_: str, content: str, iteration: int = 0) -> dict:
    return {
        "agent": agent,
        "type": type_,
        "content": content,
        "iteration": iteration,
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def _strip_code_fences(text: str) -> str:
    """
    Local models love to wrap output in ```python fences even when told not
    to. Strip them defensively rather than trusting instruction-following —
    a raw traceback from `exec`-ing a fenced code block is a bad first
    impression of the whole system.
    """
    text = text.strip()
    match = re.match(r"^```(?:python)?\s*\n(.*?)\n```$", text, re.DOTALL)
    return match.group(1) if match else text


def _extract_json(text: str) -> dict:
    """
    Even with Ollama's JSON format mode, small local models occasionally pad
    their output with stray prose. Grab the first {...} block rather than
    failing the whole node on a formatting slip.
    """
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


# ---------------------------------------------------------------------------
# Node: Planner
# ---------------------------------------------------------------------------
async def planner_node(state: AgentState) -> dict:
    llm = get_llm("planner")
    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"User request:\n{state['task']}"),
    ]
    response = await llm.ainvoke(messages)
    parsed = _extract_json(response.content)

    plan = (parsed.get("plan") or "").strip()
    dependencies = parsed.get("dependencies") or []

    return {
        "plan": plan,
        "dependencies": dependencies,
        "status": "running",
        "events": [_event("planner", "plan", plan)],
    }


# ---------------------------------------------------------------------------
# Node: Coder (handles both the first draft and every post-debug rewrite)
# ---------------------------------------------------------------------------
async def coder_node(state: AgentState) -> dict:
    llm = get_llm("coder")
    iteration = state.get("iteration", 0)

    if iteration == 0:
        messages = [
            SystemMessage(content=CODER_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Task: {state['task']}\n\n"
                    f"Plan:\n{state['plan']}\n\n"
                    "Allowed dependencies: "
                    f"{', '.join(state.get('dependencies') or []) or 'standard library only'}"
                )
            ),
        ]
    else:
        messages = [
            SystemMessage(content=CODER_FIX_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Task: {state['task']}\n\n"
                    f"Previous code:\n```python\n{state['code']}\n```\n\n"
                    f"stdout:\n{state.get('stdout', '')}\n\n"
                    f"stderr:\n{state.get('stderr', '')}\n\n"
                    f"Reviewer notes:\n{state.get('review_notes', '')}"
                )
            ),
        ]

    response = await llm.ainvoke(messages)
    code = _strip_code_fences(response.content)

    return {
        "code": code,
        "events": [_event("coder", "code", code, iteration)],
    }


# ---------------------------------------------------------------------------
# Node: Executor (runs the sandboxed code)
# ---------------------------------------------------------------------------
async def executor_node(state: AgentState) -> dict:
    executor = get_executor()
    result = await executor.run(code=state["code"], dependencies=state.get("dependencies") or [])
    iteration = state.get("iteration", 0)

    # Simple but effective success heuristic: clean exit code and no visible
    # Python traceback. This can be extended with an actual pytest run for
    # tasks that include test cases — see README "Extending".
    looks_clean = result.exit_code == 0 and "Traceback (most recent call last)" not in result.stderr

    events = [_event("executor", "stdout", result.stdout or "(no stdout)", iteration)]
    if result.stderr:
        events.append(_event("executor", "stderr", result.stderr, iteration))

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
        "success": looks_clean,
        "events": events,
    }


# ---------------------------------------------------------------------------
# Node: Reviewer / Debugger
# ---------------------------------------------------------------------------
async def reviewer_node(state: AgentState) -> dict:
    llm = get_llm("reviewer")
    iteration = state.get("iteration", 0)
    messages = [
        SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Task: {state['task']}\n\n"
                f"Code:\n```python\n{state['code']}\n```\n\n"
                f"Exit code: {state['exit_code']}\n\n"
                f"stdout:\n{state.get('stdout', '')}\n\n"
                f"stderr:\n{state.get('stderr', '')}"
            )
        ),
    ]
    response = await llm.ainvoke(messages)
    parsed = _extract_json(response.content)

    diagnosis = (parsed.get("diagnosis") or "").strip()
    fix_instructions = (parsed.get("fix_instructions") or "").strip()
    combined = f"Diagnosis: {diagnosis}\nFix instructions: {fix_instructions}"

    return {
        "review_notes": combined,
        "iteration": iteration + 1,
        "events": [_event("reviewer", "review", combined, iteration)],
    }


# ---------------------------------------------------------------------------
# Terminal bookkeeping nodes — give the final state an unambiguous `status`
# ---------------------------------------------------------------------------
async def mark_success_node(state: AgentState) -> dict:
    iteration = state.get("iteration", 0)
    return {
        "status": "success",
        "events": [_event("system", "success", "Code executed successfully.", iteration)],
    }


async def mark_failure_node(state: AgentState) -> dict:
    iteration = state.get("iteration", 0)
    return {
        "status": "failed",
        "events": [
            _event(
                "system",
                "failure",
                f"Gave up after {iteration} debug iteration(s). Last stderr:\n{state.get('stderr', '')}",
                iteration,
            )
        ],
    }
