"""
Centralized configuration for the AI Software Engineer Agent backend.

Every tunable lives here and can be overridden via environment variables
(see .env.example) without touching agent logic. That matters a lot for a
local-model system: the whole point is "swap models freely" — someone on an
8GB laptop wants small quantized models everywhere, someone with a 4090 wants
qwen2.5-coder:32b for the Coder. That should be a one-line .env change.
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# Load a .env file if present. Explicit call (rather than relying solely on
# `uvicorn --env-file`) so this works no matter how the app is started —
# uvicorn, pytest, a plain `python -m app.main`, etc.
load_dotenv()


def _env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _env_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


def _env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    # --- Ollama connection ---------------------------------------------------
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # --- Model routing: one model per agent role ------------------------------
    # Defaults match the brief's table. Override via env if you've pulled
    # something else — see README "Swapping models" for 2026-era alternatives
    # (qwen3-coder, devstral, gpt-oss, etc.) if your hardware can take them.
    planner_model: str = os.getenv("PLANNER_MODEL", "llama3:8b")
    coder_model: str = os.getenv("CODER_MODEL", "qwen2.5-coder:7b")
    reviewer_model: str = os.getenv("REVIEWER_MODEL", "codellama:13b-instruct")

    # --- Agent loop behaviour -------------------------------------------------
    max_debug_iterations: int = _env_int("MAX_DEBUG_ITERATIONS", 4)
    planner_temperature: float = _env_float("PLANNER_TEMPERATURE", 0.2)
    coder_temperature: float = _env_float("CODER_TEMPERATURE", 0.1)
    reviewer_temperature: float = _env_float("REVIEWER_TEMPERATURE", 0.1)

    # --- Sandbox execution ------------------------------------------------------
    executor_backend: str = os.getenv("EXECUTOR_BACKEND", "docker")  # "docker" | "subprocess"
    sandbox_image: str = os.getenv("SANDBOX_IMAGE", "agent-sandbox:latest")
    sandbox_timeout_seconds: int = _env_int("SANDBOX_TIMEOUT_SECONDS", 20)
    sandbox_memory_limit: str = os.getenv("SANDBOX_MEMORY_LIMIT", "512m")
    sandbox_nano_cpus: int = _env_int("SANDBOX_NANO_CPUS", 1_000_000_000)  # 1 vCPU
    sandbox_network_disabled: bool = _env_bool("SANDBOX_NETWORK_DISABLED", True)
    workspace_filename: str = os.getenv("WORKSPACE_FILENAME", "solution.py")

    # --- CORS (comma-separated origins) ----------------------------------------
    allowed_origins: list[str] = field(
        default_factory=lambda: [
            o.strip()
            for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
            if o.strip()
        ]
    )


settings = Settings()
