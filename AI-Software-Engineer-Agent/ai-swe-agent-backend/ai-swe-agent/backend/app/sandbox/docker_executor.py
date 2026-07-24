"""
Runs generated code inside a throwaway Docker container.

Safety model
------------
- The container gets NO network access by default (SANDBOX_NETWORK_DISABLED),
  so a generated script can't exfiltrate data or reach out to something
  unexpected. The practical consequence: pip packages must already be baked
  into the sandbox image (see Dockerfile.sandbox) — if the Planner asks for
  something not in that image, execution fails with a clear
  ModuleNotFoundError that flows straight to the Reviewer. Rebuild the image
  to add a package permanently; don't reach for run-time network access as
  the fix.
- CPU and memory are capped (SANDBOX_NANO_CPUS / SANDBOX_MEMORY_LIMIT) so a
  runaway or accidentally-quadratic script can't take down the host.
- The container runs as a non-root user (see Dockerfile.sandbox) with the
  workspace mounted read-write so scripts can write their own output files,
  but nothing else on the host is reachable.
- Every run gets a brand-new container from a read-only image; nothing
  persists between runs, and the container is force-removed in `finally`
  even on timeout or crash.
- A wall-clock timeout (SANDBOX_TIMEOUT_SECONDS) kills the container if the
  generated code hangs — e.g. an accidental infinite loop.

This trades a bit of flexibility (no ad-hoc pip installs at run time) for a
much smaller attack surface, which is the right default for code an LLM
wrote and you haven't read yet.
"""

import asyncio
import tempfile
import uuid
from pathlib import Path

import docker
from docker.errors import APIError, ContainerError, DockerException, ImageNotFound

from app.config import settings
from app.sandbox.base import BaseExecutor, ExecutionResult


class DockerExecutor(BaseExecutor):
    def __init__(self):
        self._client: docker.DockerClient | None = None  # lazy: don't require a running daemon at import time

    @property
    def client(self) -> docker.DockerClient:
        if self._client is None:
            self._client = docker.from_env()
        return self._client

    async def run(self, code: str, dependencies: list[str]) -> ExecutionResult:
        # docker-py is synchronous; run it off the event loop so one slow
        # container doesn't block the WebSocket for every other connection.
        return await asyncio.to_thread(self._run_sync, code)

    def _run_sync(self, code: str) -> ExecutionResult:
        run_id = uuid.uuid4().hex[:8]
        with tempfile.TemporaryDirectory(prefix=f"agent-run-{run_id}-") as tmp_dir:
            workspace = Path(tmp_dir)
            script_path = workspace / settings.workspace_filename
            script_path.write_text(code)

            # Loosen permissions on the throwaway temp dir so the sandbox's
            # non-root container user can read/write it regardless of how
            # the host maps container UIDs (this varies across Docker
            # Desktop on macOS/Windows vs. native Linux). The directory is
            # deleted the moment this `with` block exits either way.
            script_path.chmod(0o644)
            workspace.chmod(0o777)

            container = None
            try:
                try:
                    self.client.images.get(settings.sandbox_image)
                except ImageNotFound:
                    return ExecutionResult(
                        stdout="",
                        stderr=(
                            f"Sandbox image '{settings.sandbox_image}' not found.\n"
                            f"Build it first: docker build -t {settings.sandbox_image} "
                            "-f Dockerfile.sandbox ."
                        ),
                        exit_code=1,
                    )

                container = self.client.containers.run(
                    settings.sandbox_image,
                    command=["python", settings.workspace_filename],
                    working_dir="/workspace",
                    volumes={str(workspace): {"bind": "/workspace", "mode": "rw"}},
                    mem_limit=settings.sandbox_memory_limit,
                    nano_cpus=settings.sandbox_nano_cpus,
                    network_disabled=settings.sandbox_network_disabled,
                    detach=True,
                    stdout=True,
                    stderr=True,
                )

                timed_out = False
                try:
                    wait_result = container.wait(timeout=settings.sandbox_timeout_seconds)
                    exit_code = wait_result.get("StatusCode", 1)
                except Exception:
                    # Different docker-py / Docker Engine API versions raise
                    # slightly different exceptions on a client-side wait
                    # timeout (requests.ReadTimeout, urllib3 timeouts, ...).
                    # Whatever it is, the container is still running — kill
                    # it and report a timeout rather than re-raising.
                    container.kill()
                    exit_code = 124  # conventional shell "timed out" exit code
                    timed_out = True

                stdout = container.logs(stdout=True, stderr=False).decode(errors="replace")
                stderr = container.logs(stdout=False, stderr=True).decode(errors="replace")

                if timed_out:
                    stderr += (
                        f"\n[sandbox] Killed after exceeding "
                        f"{settings.sandbox_timeout_seconds}s wall-clock limit."
                    )

                return ExecutionResult(stdout=stdout, stderr=stderr, exit_code=exit_code, timed_out=timed_out)

            except (ContainerError, APIError) as exc:
                return ExecutionResult(stdout="", stderr=f"[sandbox error] {exc}", exit_code=1)
            except DockerException as exc:
                return ExecutionResult(
                    stdout="",
                    stderr=f"[sandbox error] Could not reach the Docker daemon: {exc}\nIs Docker running?",
                    exit_code=1,
                )
            finally:
                if container is not None:
                    try:
                        container.remove(force=True)
                    except APIError:
                        pass
