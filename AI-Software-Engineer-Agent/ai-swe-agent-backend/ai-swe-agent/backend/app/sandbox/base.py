"""
Executor interface. Two implementations exist:

  - DockerExecutor: spins up a throwaway, network-disabled container per
    run. This is the recommended, safety-first default.
  - SubprocessExecutor: runs code directly on the host. Much weaker
    isolation — intended only for getting the agent loop working before
    Docker is installed/running, or for CI where Docker-in-Docker is a
    hassle. See its module docstring for the security caveat.

Both return the same ExecutionResult so agents/nodes.py never needs to know
which one is active — see sandbox/factory.py for how the choice is made.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False


class BaseExecutor(ABC):
    @abstractmethod
    async def run(self, code: str, dependencies: list[str]) -> ExecutionResult:
        """Execute `code` as a standalone script and return captured output."""
        ...
