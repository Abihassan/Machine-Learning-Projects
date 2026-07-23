"""
tasks.py
=========
Defines the Task pipeline and wires up interdependency via CrewAI's
`context=[...]` mechanism: each downstream Task explicitly receives the
prior Task objects, so CrewAI automatically injects their outputs into
the agent's prompt context. This is how the Manager's spec reaches both
developers, and how both developers' code reaches QA, and how QA's
findings can loop back for a fix pass.
"""

from crewai import Task
from agents import (
    build_product_manager_agent,
    build_frontend_agent,
    build_backend_agent,
    build_devops_qa_agent,
)


def build_pipeline(user_prompt: str):
    """
    Returns (agents_list, tasks_list) fully wired for a single pass of:
    PM -> [Frontend, Backend] -> QA

    A second QA-driven fix pass is added as explicit follow-up tasks that
    depend on the QA report, giving one automatic iteration loop.
    """
    pm_agent = build_product_manager_agent()
    frontend_agent = build_frontend_agent()
    backend_agent = build_backend_agent()
    qa_agent = build_devops_qa_agent()

    # -- 1. Product Manager: requirements + architecture + JSON task list --
    spec_task = Task(
        description=(
            f"The user wants: \"{user_prompt}\"\n\n"
            "Produce a technical specification containing:\n"
            "1. A short architecture overview (chosen frontend stack, backend stack, "
            "data storage).\n"
            "2. A precise REST API contract: list every endpoint with method, path, "
            "request body schema, and response schema.\n"
            "3. A JSON task list array, each item with fields: "
            "{id, owner ('frontend'|'backend'), title, description}.\n\n"
            "Save this full specification using the Write Project File tool as "
            "'spec/architecture.md' (human-readable) AND 'spec/tasks.json' "
            "(machine-readable JSON task list + API contract embedded as a field)."
        ),
        expected_output=(
            "Confirmation that spec/architecture.md and spec/tasks.json were written, "
            "plus the full spec content inline in your final answer so downstream "
            "agents have it directly in context."
        ),
        agent=pm_agent,
    )

    # -- 2. Frontend Developer: depends on spec_task's output --
    frontend_task = Task(
        description=(
            "Using the architecture and API contract produced by the Product Manager "
            "(available in your context), implement the complete frontend application. "
            "Write every file via the Write Project File tool under 'frontend/'. "
            "Include a package.json (or plain index.html if no build step) so the "
            "QA agent can install/run it. Do not invent endpoints not in the spec."
        ),
        expected_output=(
            "A list of every frontend file written, plus a one-line run command "
            "(e.g. 'npm install && npm run build' or 'python -m http.server') that "
            "QA should use to verify it."
        ),
        agent=frontend_agent,
        context=[spec_task],
    )

    # -- 3. Backend Developer: depends on spec_task's output --
    backend_task = Task(
        description=(
            "Using the architecture and API contract produced by the Product Manager "
            "(available in your context), implement the complete backend application "
            "exactly matching the API contract. Write every file via the Write Project "
            "File tool under 'backend/', including requirements.txt or package.json, "
            "and a health-check route ('/health')."
        ),
        expected_output=(
            "A list of every backend file written, plus a one-line run command "
            "(e.g. 'pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0') "
            "that QA should use to verify it."
        ),
        agent=backend_agent,
        context=[spec_task],
    )

    # -- 4. DevOps/QA: depends on BOTH developer outputs --
    qa_task = Task(
        description=(
            "You now have the frontend and backend run commands in your context. "
            "For each of 'frontend' and 'backend': write an appropriate Dockerfile "
            "into that subdirectory, then use the Run Code In Docker Sandbox tool "
            "(subdirectory='frontend' or 'backend', run_command=<their stated command>, "
            "base_image='node:20-slim' for JS or 'python:3.11-slim' for Python) to "
            "actually execute it. Analyze stdout/stderr/exit_code from each run. "
            "Write a final report to 'qa_report.md' with a clear PASS/FAIL per "
            "component and, for any FAIL, the exact error and which agent "
            "(frontend/backend) needs to fix what."
        ),
        expected_output=(
            "The full contents of qa_report.md, including pass/fail status for "
            "frontend and backend and actionable fix instructions for any failures."
        ),
        agent=qa_agent,
        context=[frontend_task, backend_task],
    )

    agents = [pm_agent, frontend_agent, backend_agent, qa_agent]
    tasks = [spec_task, frontend_task, backend_task, qa_task]
    return agents, tasks


def build_fix_pass(qa_task_output: str, target: str):
    """
    Optional second-iteration helper: given the QA report text and a target
    ('frontend' or 'backend'), builds a single corrective Task for that
    developer agent. Call this from main.py if qa_report.md contains FAIL.
    """
    agent = build_frontend_agent() if target == "frontend" else build_backend_agent()
    fix_task = Task(
        description=(
            f"The QA report below identified failures in your '{target}' component:\n\n"
            f"{qa_task_output}\n\n"
            "Fix the specific issues described. Re-write only the files that need "
            "to change, using the Write Project File tool (overwriting the same "
            f"relative paths under '{target}/')."
        ),
        expected_output=f"List of {target} files that were corrected and a summary of each fix.",
        agent=agent,
    )
    return agent, fix_task
