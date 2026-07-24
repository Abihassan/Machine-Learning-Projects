"""Picks the configured executor implementation. See config.EXECUTOR_BACKEND."""

from functools import lru_cache

from app.config import settings
from app.sandbox.base import BaseExecutor
from app.sandbox.docker_executor import DockerExecutor
from app.sandbox.subprocess_executor import SubprocessExecutor


@lru_cache(maxsize=1)
def get_executor() -> BaseExecutor:
    if settings.executor_backend == "docker":
        return DockerExecutor()
    if settings.executor_backend == "subprocess":
        return SubprocessExecutor()
    raise ValueError(f"Unknown EXECUTOR_BACKEND '{settings.executor_backend}' (expected 'docker' or 'subprocess')")
