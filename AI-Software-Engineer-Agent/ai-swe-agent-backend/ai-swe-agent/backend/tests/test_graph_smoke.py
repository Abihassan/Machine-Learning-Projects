"""
Smoke test for the full LangGraph loop:

    Plan -> Code -> Execute -> Evaluate -> Debug -> Code -> Execute -> Success

This test replaces the LLM calls with scripted fake responses and swaps in
the (Docker-free) SubprocessExecutor, so it runs anywhere with just
`pip install -r requirements-dev.txt && pytest` — no Ollama and no Docker
required. It exists to prove the *graph wiring and retry logic* are
correct; it is not a test of real model output quality (there's no
substitute for trying real prompts against real models for that).
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import app.agents.nodes as nodes_mod
from app.agents.graph import build_graph
from app.sandbox.subprocess_executor import SubprocessExecutor


class ScriptedLLM:
    """Fake chat model: returns the next string in `script` on each .ainvoke()."""

    def __init__(self, script: list[str]):
        self.script = script
        self.calls = 0

    async def ainvoke(self, _messages):
        content = self.script[min(self.calls, len(self.script) - 1)]
        self.calls += 1
        return SimpleNamespace(content=content)


PLAN_JSON = '{"plan": "1. Add two numbers and print the result.", "dependencies": []}'
BAD_CODE = "print(1 / 0)"  # first attempt: deliberately broken
GOOD_CODE = "print(1 + 1)"  # second attempt: fixed
REVIEW_JSON = (
    '{"diagnosis": "ZeroDivisionError: the script divides by zero.", '
    '"fix_instructions": "Do not divide by zero; use addition instead."}'
)

_FAKE_LLMS = {
    "planner": ScriptedLLM([PLAN_JSON]),
    "coder": ScriptedLLM([BAD_CODE, GOOD_CODE]),
    "reviewer": ScriptedLLM([REVIEW_JSON]),
}


def _fake_get_llm(role: str):
    return _FAKE_LLMS[role]


def _fake_get_executor():
    return SubprocessExecutor()


def _initial_state():
    return {
        "task": "Write a script that divides two numbers.",
        "max_iterations": 4,
        "plan": "",
        "dependencies": [],
        "code": "",
        "stdout": "",
        "stderr": "",
        "exit_code": 0,
        "success": False,
        "review_notes": "",
        "iteration": 0,
        "status": "running",
        "events": [],
    }


def test_agent_loop_recovers_from_a_runtime_error():
    with (
        patch.object(nodes_mod, "get_llm", _fake_get_llm),
        patch.object(nodes_mod, "get_executor", _fake_get_executor),
    ):
        graph = build_graph()

        async def _run():
            events = []
            async for step in graph.astream(_initial_state(), stream_mode="updates"):
                for _node, update in step.items():
                    events.extend(update.get("events", []))
            return events

        events = asyncio.run(_run())

    kinds = [(e["agent"], e["type"]) for e in events]

    # The loop must touch every stage, hit exactly one debug cycle triggered
    # by the deliberately-broken first attempt, and end on success rather
    # than giving up.
    assert ("planner", "plan") in kinds
    assert kinds.count(("coder", "code")) == 2  # initial attempt + one fix
    assert ("reviewer", "review") in kinds
    assert ("system", "success") in kinds
    assert ("system", "failure") not in kinds


def test_agent_loop_gives_up_after_max_iterations():
    """If every attempt keeps failing, the loop must terminate (not hang) and report failure."""
    always_broken = {
        "planner": ScriptedLLM([PLAN_JSON]),
        "coder": ScriptedLLM([BAD_CODE]),  # same broken script every time
        "reviewer": ScriptedLLM([REVIEW_JSON]),
    }

    with (
        patch.object(nodes_mod, "get_llm", lambda role: always_broken[role]),
        patch.object(nodes_mod, "get_executor", _fake_get_executor),
    ):
        graph = build_graph()
        state = _initial_state()
        state["max_iterations"] = 2  # keep the test fast

        async def _run():
            events = []
            async for step in graph.astream(state, stream_mode="updates"):
                for _node, update in step.items():
                    events.extend(update.get("events", []))
            return events

        events = asyncio.run(_run())

    kinds = [(e["agent"], e["type"]) for e in events]
    assert ("system", "failure") in kinds
    assert ("system", "success") not in kinds
    # initial attempt + 2 fixes = 3 coder calls before giving up
    assert kinds.count(("coder", "code")) == 3
