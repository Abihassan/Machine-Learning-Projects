"""
Model router: maps an agent *role* ("planner" | "coder" | "reviewer") to a
configured `ChatOllama` instance pointed at your local Ollama server.

Centralizing this mapping (rather than constructing ChatOllama inline in
each node) means "use a bigger model for the Reviewer" is a one-line .env
change, not a grep through agent code. It also lets the Planner and Reviewer
opt into Ollama's JSON-constrained output mode (`format="json"`) since they
both return structured data, while the Coder — which must emit raw Python,
not JSON — does not.
"""

from functools import lru_cache

from langchain_ollama import ChatOllama

from app.config import settings

AgentRole = str  # "planner" | "coder" | "reviewer"

_ROLE_TO_MODEL = {
    "planner": settings.planner_model,
    "coder": settings.coder_model,
    "reviewer": settings.reviewer_model,
}

_ROLE_TO_TEMPERATURE = {
    "planner": settings.planner_temperature,
    "coder": settings.coder_temperature,
    "reviewer": settings.reviewer_temperature,
}

# Only roles whose prompts ask for a JSON object get Ollama's JSON-mode
# decoding constraint. Forcing it on the Coder would fight against emitting
# plain Python source.
_ROLES_USING_JSON_MODE = {"planner", "reviewer"}


@lru_cache(maxsize=None)
def get_llm(role: AgentRole) -> ChatOllama:
    """
    Returns a cached ChatOllama client for the given role. Cached (not
    reconstructed per call) so repeated debug-loop iterations reuse the same
    client rather than opening a fresh one every turn.
    """
    if role not in _ROLE_TO_MODEL:
        raise ValueError(f"Unknown agent role '{role}'. Expected one of {list(_ROLE_TO_MODEL)}")

    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=_ROLE_TO_MODEL[role],
        temperature=_ROLE_TO_TEMPERATURE[role],
        format="json" if role in _ROLES_USING_JSON_MODE else None,
    )


def model_for(role: AgentRole) -> str:
    """Expose which model name is bound to a role — used for logging/UI display."""
    return _ROLE_TO_MODEL[role]
