"""
agents.py
==========
Defines the four interdependent agents. Communication between them is
handled implicitly by CrewAI: each Task's output becomes part of the
*context* available to the next Task's agent (wired explicitly in tasks.py
via `context=[...]`). This file only defines WHO each agent is and WHAT
tools it has access to.

Interdependency at a glance:
  ProductManager --> (architecture + task list) --> Frontend & Backend
  Frontend       --> (UI code)          --\
  Backend        --> (API/server code)  ---> DevOpsQA (dockerizes + runs + tests)
  DevOpsQA       --> (pass/fail + logs) --> back to Frontend/Backend for iteration
"""

import os
import json
from crewai import Agent
from crewai.tools import tool

from llm_config import get_manager_llm, get_frontend_llm, get_backend_llm, get_qa_llm
from sandbox_manager import SandboxManager

OUTPUT_DIR = os.getenv("MAS_OUTPUT_DIR", "./output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Tools — these are what let agents actually DO things beyond generating text
# ---------------------------------------------------------------------------
@tool("Write Project File")
def write_file_tool(relative_path: str, content: str) -> str:
    """
    Writes `content` to a file at `relative_path` inside the shared project
    output directory. Use this to persist any code you generate (e.g.
    'frontend/src/App.jsx', 'backend/main.py', 'backend/Dockerfile').
    Creates parent directories as needed. Returns a confirmation message.
    """
    safe_path = os.path.normpath(relative_path).lstrip("/.")
    full_path = os.path.join(OUTPUT_DIR, safe_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} chars to {full_path}"
    except OSError as e:
        return f"ERROR writing file {full_path}: {e}"


@tool("Read Project File")
def read_file_tool(relative_path: str) -> str:
    """Reads back a previously written project file, for cross-agent review."""
    safe_path = os.path.normpath(relative_path).lstrip("/.")
    full_path = os.path.join(OUTPUT_DIR, safe_path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"ERROR: {full_path} does not exist yet."


@tool("Run Code In Docker Sandbox")
def run_sandbox_tool(subdirectory: str, run_command: str, base_image: str = "python:3.11-slim") -> str:
    """
    Executes `run_command` inside an ephemeral, network-isolated Docker
    container containing the contents of output/<subdirectory>.
    Use `base_image="node:20-slim"` for JS/React projects.
    Returns a JSON string with success, exit_code, stdout, and stderr —
    analyze this output to decide whether the code needs another iteration.
    """
    project_path = os.path.join(OUTPUT_DIR, subdirectory)
    try:
        manager = SandboxManager()
        result = manager.run_project(project_path, run_command, image=base_image)
        return json.dumps({
            "success": result.success,
            "exit_code": result.exit_code,
            "stdout": result.stdout[-4000:],   # keep prompt-context bounded
            "stderr": result.stderr[-4000:],
            "error": result.error,
        }, indent=2)
    except RuntimeError as e:
        # e.g. Docker daemon not running — surface this clearly to the QA agent
        return json.dumps({"success": False, "error": str(e)})


# ---------------------------------------------------------------------------
# Agent Definitions
# ---------------------------------------------------------------------------
def build_product_manager_agent() -> Agent:
    return Agent(
        role="Product Manager & Solutions Architect",
        goal=(
            "Translate the user's plain-language app idea into a precise technical "
            "specification: a system architecture, a chosen tech stack (frontend + "
            "backend + storage), and a JSON task list that unambiguously tells the "
            "Frontend and Backend developers exactly what to build, including API "
            "contract (endpoints, request/response shapes) so both sides agree on "
            "the interface before writing code."
        ),
        backstory=(
            "A former staff engineer turned PM who has shipped dozens of full-stack "
            "products. Obsessive about writing specs so clear that two developers "
            "working in isolation would still produce compatible code."
        ),
        llm=get_manager_llm(),
        tools=[write_file_tool, read_file_tool],
        allow_delegation=False,
        verbose=True,
    )


def build_frontend_agent() -> Agent:
    return Agent(
        role="Senior Frontend Developer",
        goal=(
            "Implement a clean, working client-side application (React or plain "
            "HTML/CSS/JS as specified by the architecture) that consumes exactly "
            "the API contract defined by the Product Manager. Write all files using "
            "the Write Project File tool under the 'frontend/' path."
        ),
        backstory=(
            "A pragmatic frontend engineer who prioritizes working code over "
            "cleverness, writes semantic HTML, and never invents API endpoints "
            "that weren't in the spec."
        ),
        llm=get_frontend_llm(),
        tools=[write_file_tool, read_file_tool],
        allow_delegation=False,
        verbose=True,
    )


def build_backend_agent() -> Agent:
    return Agent(
        role="Senior Backend Developer",
        goal=(
            "Implement the server, API routes, and data layer exactly matching the "
            "API contract from the Product Manager's spec, using the tech stack "
            "specified (e.g. FastAPI + SQLite). Include a requirements.txt/package.json "
            "and a minimal test or health-check endpoint. Write all files via the "
            "Write Project File tool under the 'backend/' path."
        ),
        backstory=(
            "A backend engineer who writes defensive, well-structured API code and "
            "always includes dependency manifests so the QA agent can actually run it."
        ),
        llm=get_backend_llm(),
        tools=[write_file_tool, read_file_tool],
        allow_delegation=False,
        verbose=True,
    )


def build_devops_qa_agent() -> Agent:
    return Agent(
        role="DevOps & QA Engineer",
        goal=(
            "Write Dockerfiles/run scripts for both frontend and backend, execute "
            "them in the isolated sandbox using the Run Code In Docker Sandbox tool, "
            "capture stdout/stderr, and produce a clear pass/fail QA report "
            "(output/qa_report.md) describing any errors and exactly what the "
            "responsible developer agent needs to fix. This report is the feedback "
            "loop that drives the next iteration."
        ),
        backstory=(
            "A meticulous QA/DevOps engineer who never rubber-stamps code — every "
            "claim of 'it works' is backed by an actual sandboxed execution log."
        ),
        llm=get_qa_llm(),
        tools=[write_file_tool, read_file_tool, run_sandbox_tool],
        allow_delegation=False,
        verbose=True,
    )
