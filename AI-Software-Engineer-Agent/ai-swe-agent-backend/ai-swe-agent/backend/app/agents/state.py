"""
Shared state that flows through every node of the LangGraph loop.

LangGraph passes this dict between nodes; each node returns a *partial*
update and the graph merges it into the running state using each key's
reducer (default: overwrite). TypedDict keeps this explicit instead of a
free-form dict that's only documented in comments scattered across nodes.py.
"""

import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict):
    # --- input ------------------------------------------------------------
    task: str  # the user's original natural-language request
    max_iterations: int

    # --- planner output -----------------------------------------------------
    plan: str  # step-by-step plan, in natural language
    dependencies: list[str]  # extra pip packages the plan calls for

    # --- coder output -------------------------------------------------------
    code: str  # current best version of the generated script

    # --- executor output -----------------------------------------------------
    stdout: str
    stderr: str
    exit_code: int
    success: bool

    # --- reviewer output -----------------------------------------------------
    review_notes: str  # diagnosis + fix instructions for the next coder pass

    # --- control flow --------------------------------------------------------
    iteration: int  # number of completed debug (reviewer -> coder) cycles
    status: str  # "running" | "success" | "failed"

    # --- streaming -----------------------------------------------------------
    # Each node returns only the event(s) *it* produced. Annotated with
    # operator.add so that if anything ever reads the graph's fully merged
    # state (rather than just consuming the per-node stream), it sees the
    # complete transcript rather than only the last node's events.
    events: Annotated[list[dict], operator.add]
