"""
Fallback executor that runs generated code directly on the host via
`subprocess` instead of inside Docker.

*** This is NOT a security sandbox. ***
It shares your host's filesystem, network, and OS permissions with whatever
the LLM wrote. Use it only to get the agent loop running before Docker is
installed, or in CI for the smoke test in tests/test_graph_smoke.py — never
against code you actually intend to trust. Switch to DockerExecutor
(EXECUTOR_BACKEND=docker, the default) for anything real.
"""

import asyncio
import subprocess
import tempfile
import uuid
from pathlib import Path

from app.config import settings
from app.sandbox.base import BaseExecutor, ExecutionResult


class SubprocessExecutor(BaseExecutor):
    async def run(self, code: str, dependencies: list[str]) -> ExecutionResult:
        return await asyncio.to_thread(self._run_sync, code)

    def _run_sync(self, code: str) -> ExecutionResult:
        run_id = uuid.uuid4().hex[:8]
        with tempfile.TemporaryDirectory(prefix=f"agent-run-{run_id}-") as tmp_dir:
            script_path = Path(tmp_dir) / settings.workspace_filename
            script_path.write_text(code)

            try:
                proc = subprocess.run(
                    ["python3", str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=settings.sandbox_timeout_seconds,
                    cwd=tmp_dir,
                )
                return ExecutionResult(stdout=proc.stdout, stderr=proc.stderr, exit_code=proc.returncode)
            except subprocess.TimeoutExpired as exc:
                return ExecutionResult(
                    stdout=exc.stdout or "",
                    stderr=(exc.stderr or "")
                    + f"\n[sandbox] Killed after exceeding {settings.sandbox_timeout_seconds}s.",
                    exit_code=124,
                    timed_out=True,
                )
