"""
Operational helpers for Ollama that LangChain's ChatOllama intentionally
doesn't provide: "is the server even running?" and "is this model actually
pulled?".

We check both at FastAPI startup (see main.py's /health route) so a
misconfigured local setup fails with a clear, actionable message instead of
a confusing httpx timeout three LangGraph nodes deep into a run.

This talks to Ollama's raw REST API directly with httpx rather than through
any LangChain wrapper, since none of this is "call the model" — it's
infrastructure plumbing around it.
"""

import httpx

from app.config import settings


async def ping_ollama() -> bool:
    """Is the Ollama server reachable at all?"""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            return resp.status_code == 200
    except httpx.HTTPError:
        return False


async def list_local_models() -> list[str]:
    """Every model tag currently pulled (e.g. ['llama3:8b', 'qwen2.5-coder:7b'])."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(f"{settings.ollama_base_url}/api/tags")
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]


async def missing_models(required: list[str]) -> list[str]:
    """
    Which of `required` aren't present locally yet. Matches on the base name
    before ':' too, so if you've pulled `qwen2.5-coder:14b` instead of the
    default `:7b`, we don't nag you to re-pull a redundant tag — mismatched
    *sizes* are your call, missing *models* are what we actually warn about.
    """
    local = await list_local_models()
    local_bases = {m.split(":")[0] for m in local}
    return [model for model in required if model not in local and model.split(":")[0] not in local_bases]


async def pull_model(model: str) -> None:
    """
    Streams `ollama pull <model>` progress to the server console. Sends both
    `model` and `name` in the payload since Ollama's API has used both field
    names across versions — harmless to include both, and it means this
    works regardless of which your installed daemon expects.
    """
    print(f"[ollama] Pulling '{model}' — this can take a while on first run...")
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            f"{settings.ollama_base_url}/api/pull",
            json={"model": model, "name": model, "stream": True},
        ) as resp:
            async for line in resp.aiter_lines():
                if line:
                    print(f"[ollama:pull:{model}] {line}")
