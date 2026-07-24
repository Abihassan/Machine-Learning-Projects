"""
Basic API smoke test — confirms the FastAPI app boots and /health responds
with a well-formed payload, independent of whether Ollama or Docker happen
to be running wherever this test executes (e.g. in CI).
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_shape():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "ollama_reachable" in body
    assert "required_models" in body
    assert "missing_models" in body
    assert "executor_backend" in body
