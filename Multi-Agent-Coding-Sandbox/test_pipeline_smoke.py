"""
tests/test_pipeline_smoke.py
==============================
A dependency-free smoke test: verifies that agents/tasks build correctly and
that the file-write/read tools work, WITHOUT requiring a running Ollama
server or Docker daemon. Useful for CI or for verifying a fresh checkout
before you've pulled any local models.

Run:
    python -m pytest tests/test_pipeline_smoke.py -v
"""

import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_write_and_read_file_tool(monkeypatch, tmp_path):
    """The core file tools must work independent of any LLM/Docker."""
    monkeypatch.setenv("MAS_OUTPUT_DIR", str(tmp_path))
    # Re-import agents fresh so OUTPUT_DIR picks up the env var
    import importlib
    import agents as agents_module
    importlib.reload(agents_module)

    result = agents_module.write_file_tool.func("backend/main.py", "print('hi')")
    assert "Successfully wrote" in result

    content = agents_module.read_file_tool.func("backend/main.py")
    assert content == "print('hi')"

    missing = agents_module.read_file_tool.func("backend/does_not_exist.py")
    assert "ERROR" in missing


def test_pipeline_builds_with_correct_dependencies(monkeypatch):
    """
    Verifies PM -> Frontend/Backend -> QA wiring exists, without calling any
    real model (LLM objects are constructed but never invoked in this test).
    """
    from tasks import build_pipeline

    agents_list, tasks_list = build_pipeline("Build a simple note-taking app")
    assert len(agents_list) == 4
    assert len(tasks_list) == 4

    spec_task, frontend_task, backend_task, qa_task = tasks_list

    # Frontend and backend must both depend on the spec task's output
    assert spec_task in list(frontend_task.context)
    assert spec_task in list(backend_task.context)

    # QA must depend on both developer outputs
    assert frontend_task in list(qa_task.context)
    assert backend_task in list(qa_task.context)

    # Roles are distinct and correctly assigned
    roles = {t.agent.role for t in tasks_list}
    assert len(roles) == 4


def test_sandbox_manager_fails_gracefully_without_docker():
    """
    If no Docker daemon is reachable, SandboxManager must raise a clear,
    actionable RuntimeError rather than crashing obscurely or hanging.
    """
    from sandbox_manager import SandboxManager
    import docker.errors

    try:
        SandboxManager()
        # If this environment DOES have Docker running, that's fine too —
        # just don't fail the test.
    except RuntimeError as e:
        assert "Docker" in str(e)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
