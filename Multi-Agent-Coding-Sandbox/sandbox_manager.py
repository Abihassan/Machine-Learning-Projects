"""
sandbox_manager.py
====================
Spins up ephemeral, resource-capped Docker containers to execute and test
the code produced by the Frontend/Backend agents, then tears them down.

This is the safety boundary of the whole system: generated code is NEVER
executed on the host. It only ever runs inside a disposable container with:
  - no network access by default (network_disabled=True)
  - CPU / memory limits
  - a read-only view of the host, with only the target project dir mounted
  - auto-removal on exit (or explicit cleanup in `finally`)

The QA Agent calls `run_in_sandbox()` (via a CrewAI tool wrapper in agents.py)
and receives back structured stdout/stderr/exit_code, which it then reasons
about and feeds back to the dev agents for another iteration.
"""

import io
import os
import tarfile
import uuid
import docker
from docker.errors import DockerException, ImageNotFound, APIError
from dataclasses import dataclass, field


@dataclass
class SandboxResult:
    success: bool
    exit_code: int | None
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    container_id: str = ""


class SandboxManager:
    """
    Wraps the Docker SDK to provide a single-call `run_project()` method.
    One instance can be reused across multiple runs; each run gets its own
    freshly created, freshly destroyed container.
    """

    def __init__(self, network_enabled: bool = False, mem_limit: str = "512m",
                 cpu_quota: int = 50000, timeout_seconds: int = 90):
        try:
            self.client = docker.from_env()
            self.client.ping()
        except DockerException as e:
            raise RuntimeError(
                "Could not connect to the Docker daemon. Ensure Docker Desktop "
                f"/ dockerd is running and accessible. Original error: {e}"
            )
        self.network_enabled = network_enabled
        self.mem_limit = mem_limit
        self.cpu_quota = cpu_quota  # 50000 == ~50% of one core (period=100000)
        self.timeout_seconds = timeout_seconds

    # ------------------------------------------------------------------
    def _ensure_image(self, image: str) -> None:
        """Pull the base image if not already present locally."""
        try:
            self.client.images.get(image)
        except ImageNotFound:
            try:
                self.client.images.pull(image)
            except APIError as e:
                raise RuntimeError(f"Failed to pull sandbox base image '{image}': {e}")

    # ------------------------------------------------------------------
    def _copy_dir_into_container(self, container, host_path: str, dest_path: str):
        """Stream a local directory into the container as a tarball (no bind-mount needed)."""
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w") as tar:
            tar.add(host_path, arcname=os.path.basename(dest_path))
        stream.seek(0)
        container.put_archive(os.path.dirname(dest_path) or "/", stream)

    # ------------------------------------------------------------------
    def run_project(self, project_dir: str, run_command: str,
                     image: str = "python:3.11-slim") -> SandboxResult:
        """
        Execute `run_command` inside a disposable container that has
        `project_dir` copied in at /app.

        Args:
            project_dir: host path to the generated code (e.g. output/backend)
            run_command: shell command to run inside the container
                         e.g. "pip install -r requirements.txt && pytest"
            image: base image (swap to `node:20-slim` for a JS backend/frontend build)
        """
        if not os.path.isdir(project_dir):
            return SandboxResult(success=False, exit_code=None,
                                  error=f"project_dir '{project_dir}' does not exist")

        self._ensure_image(image)

        container_name = f"mas-sandbox-{uuid.uuid4().hex[:10]}"
        container = None
        try:
            container = self.client.containers.create(
                image=image,
                name=container_name,
                command="sleep infinity",   # keep alive; we exec commands into it
                working_dir="/app",
                mem_limit=self.mem_limit,
                cpu_period=100000,
                cpu_quota=self.cpu_quota,
                network_disabled=not self.network_enabled,
                security_opt=["no-new-privileges"],
                read_only=False,          # generated code may need to write build artifacts
                detach=True,
            )
            container.start()

            # Ensure /app exists then copy code in
            container.exec_run("mkdir -p /app")
            self._copy_dir_into_container(container, project_dir, "/app")

            exec_result = container.exec_run(
                cmd=["/bin/sh", "-c", run_command],
                workdir="/app",
                demux=True,
            )
            stdout_bytes, stderr_bytes = exec_result.output
            stdout = (stdout_bytes or b"").decode("utf-8", errors="replace")
            stderr = (stderr_bytes or b"").decode("utf-8", errors="replace")

            return SandboxResult(
                success=(exec_result.exit_code == 0),
                exit_code=exec_result.exit_code,
                stdout=stdout,
                stderr=stderr,
                container_id=container.id[:12],
            )

        except APIError as e:
            return SandboxResult(success=False, exit_code=None, error=f"Docker API error: {e}")
        except Exception as e:
            return SandboxResult(success=False, exit_code=None, error=f"Unexpected sandbox error: {e}")
        finally:
            # Always clean up — ephemeral by design, even on failure.
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass  # best-effort cleanup; don't mask the real result


if __name__ == "__main__":
    # Smoke test: run a trivial command in an ephemeral container
    mgr = SandboxManager()
    os.makedirs("/tmp/sandbox_smoketest", exist_ok=True)
    with open("/tmp/sandbox_smoketest/hello.py", "w") as f:
        f.write("print('sandbox is alive')")
    result = mgr.run_project("/tmp/sandbox_smoketest", "python hello.py")
    print(result)

