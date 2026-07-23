"""
llm_config.py
==============
Central configuration for connecting CrewAI agents to LOCAL models only.

CrewAI uses LiteLLM under the hood, which natively understands Ollama's
OpenAI-compatible endpoint when the model string is prefixed with "ollama/".
No proprietary API keys (OpenAI, Anthropic, etc.) are used or required anywhere
in this system — everything routes to http://localhost:11434 by default.

If you'd rather use LM Studio (also OpenAI-compatible) or a raw HuggingFace
Transformers pipeline, swap LOCAL_ENDPOINT / use get_hf_llm() below.
"""

import os
from dotenv import load_dotenv
from crewai import LLM

# Load .env if present (silently no-ops if the file doesn't exist), so
# OLLAMA_BASE_URL / *_MODEL overrides in .env.example actually take effect.
load_dotenv()

# ---------------------------------------------------------------------------
# Environment-driven configuration (override via .env or shell export)
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Pick different local models per role if you like — smaller/faster models
# for simple tasks, a stronger coding model for dev agents.
MANAGER_MODEL = os.getenv("MANAGER_MODEL", "ollama/llama3.1:8b")
FRONTEND_MODEL = os.getenv("FRONTEND_MODEL", "ollama/codeqwen:7b")
BACKEND_MODEL = os.getenv("BACKEND_MODEL", "ollama/codeqwen:7b")
QA_MODEL = os.getenv("QA_MODEL", "ollama/mistral:7b")

# Fail loudly rather than silently falling back to a hosted API — this system
# is designed to be fully offline-capable.
if any("gpt-" in m or "claude-" in m for m in
       [MANAGER_MODEL, FRONTEND_MODEL, BACKEND_MODEL, QA_MODEL]):
    raise RuntimeError(
        "Proprietary model detected in config. This sandbox is restricted to "
        "local models only (ollama/..., lm-studio/..., huggingface/...)."
    )


def _build_llm(model_name: str, temperature: float = 0.3) -> LLM:
    """
    Build a CrewAI LLM instance bound to the local Ollama server.
    `base_url` is what makes this local-only — never point this at a
    hosted inference endpoint.
    """
    try:
        return LLM(
            model=model_name,
            base_url=OLLAMA_BASE_URL,
            temperature=temperature,
            # Generous timeout since local inference on consumer hardware
            # can be considerably slower than hosted APIs.
            timeout=600,
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to initialize local LLM '{model_name}' at {OLLAMA_BASE_URL}. "
            f"Is Ollama running? Try `ollama serve` and `ollama pull <model>`. "
            f"Original error: {e}"
        )


# ---------------------------------------------------------------------------
# Public factory functions — one per agent role, so each can be tuned
# independently (e.g. lower temperature for QA/deterministic analysis,
# higher for creative frontend work).
# ---------------------------------------------------------------------------
def get_manager_llm() -> LLM:
    return _build_llm(MANAGER_MODEL, temperature=0.4)


def get_frontend_llm() -> LLM:
    return _build_llm(FRONTEND_MODEL, temperature=0.3)


def get_backend_llm() -> LLM:
    return _build_llm(BACKEND_MODEL, temperature=0.2)


def get_qa_llm() -> LLM:
    return _build_llm(QA_MODEL, temperature=0.0)  # deterministic log analysis


# ---------------------------------------------------------------------------
# Optional: raw HuggingFace Transformers fallback (fully offline, no server)
# Use this if the user has no Ollama/LM Studio installed but has local
# HF weights cached. Not wired into agents.py by default — swap in if needed.
# ---------------------------------------------------------------------------
def get_hf_llm(model_id: str = "Qwen/CodeQwen1.5-7B-Chat"):
    """
    Returns a CrewAI-compatible LLM backed directly by a local HF pipeline.
    Requires `transformers`, `torch`, and (ideally) a GPU.
    """
    from crewai import LLM
    return LLM(
        model=f"huggingface/{model_id}",
        temperature=0.3,
    )


if __name__ == "__main__":
    # Simple connectivity smoke test
    llm = get_manager_llm()
    print(f"Configured manager LLM: {MANAGER_MODEL} @ {OLLAMA_BASE_URL}")
    print("Run `ollama list` to confirm the model is pulled locally.")
