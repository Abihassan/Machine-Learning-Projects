"""
Wire-format schemas shared between the backend and the (soon-to-exist)
frontend. Keeping these in one place means the TypeScript types on the
frontend side are a straight transcription of this file, not a guess.
"""

from typing import Literal

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    """Sent by the client over the /ws/agent WebSocket to kick off a run."""

    task: str = Field(..., min_length=1, description="Natural-language description of what to build.")
    max_iterations: int | None = Field(
        default=None, description="Override the default debug-loop retry budget for this run."
    )


class AgentEvent(BaseModel):
    """
    One streamed step of the agent loop. The frontend renders one
    bubble/log-line per event as it arrives over the WebSocket.

    `agent` identifies which part of the system produced the event;
    `type` identifies what kind of content it is. Not every (agent, type)
    combination is meaningful — see agents/nodes.py for which ones actually
    get emitted.
    """

    type: Literal[
        "plan",       # planner's step-by-step plan
        "code",       # coder's current best script (first draft or a fix)
        "stdout",     # sandbox stdout from the last execution
        "stderr",     # sandbox stderr from the last execution
        "review",     # reviewer's diagnosis + fix instructions
        "success",    # terminal: code ran cleanly
        "failure",    # terminal: gave up after max_debug_iterations
        "error",      # terminal: something in the pipeline itself broke
        "done",       # connection-level: this run has finished, one way or another
    ]
    agent: Literal["planner", "coder", "executor", "reviewer", "system"]
    content: str
    iteration: int = 0
    ts: str | None = None
