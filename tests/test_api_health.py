from fastapi.testclient import TestClient
from icgl.api.server import app  # noqa: E402


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("api") in {"healthy", "degraded"}
    assert "env_loaded" in data
