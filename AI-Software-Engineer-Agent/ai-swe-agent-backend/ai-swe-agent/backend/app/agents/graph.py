"""
Wires the node functions in nodes.py into the closed loop described in the
project brief:

    Receive Task -> Generate Code -> Execute Code -> Evaluate
        -> (If Error) Debug -> back to Generate Code
        -> (If Success) Return Final Code

Graph shape:

                                            ------ success -----> mark_success -> END
                                           |
    START -> planner -> coder -> executor -+
                            ^              |
                            |               ------ debug (retries left) -> reviewer --+
                            |                                                          |
                            +----------------------------------------------------------+
                                           |
                                            ------ give_up (no retries left) -> mark_failure -> END

`coder` is visited once for the first draft (iteration 0) and once more per
debug cycle; `reviewer` is what increments `iteration` and loops back.
"""

from langgraph.graph import END, START, StateGraph

from app.agents.nodes import (
    coder_node,
    executor_node,
    mark_failure_node,
    mark_success_node,
    planner_node,
    reviewer_node,
)
from app.agents.state import AgentState


def _route_after_execution(state: AgentState) -> str:
    """Conditional edge: decide what happens right after the sandbox run."""
    if state["success"]:
        return "success"
    if state.get("iteration", 0) >= state.get("max_iterations", 4):
        return "give_up"
    return "debug"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("coder", coder_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("mark_success", mark_success_node)
    graph.add_node("mark_failure", mark_failure_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "executor")

    graph.add_conditional_edges(
        "executor",
        _route_after_execution,
        {
            "success": "mark_success",
            "debug": "reviewer",
            "give_up": "mark_failure",
        },
    )

    graph.add_edge("reviewer", "coder")  # closes the debug loop
    graph.add_edge("mark_success", END)
    graph.add_edge("mark_failure", END)

    return graph.compile()


# Compiled once at import time — building the graph is pure Python (no
# network calls), so this is safe to do at module load.
agent_graph = build_graph()
