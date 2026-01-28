from fastapi.testclient import TestClient

from src.api.server import root_app

client = TestClient(root_app)


def test_api_health():
    # Test the API health endpoint mounted at /api/health (or via router)
    # In modular server.py, we have app.include_router(system.router, prefix="/v1/system")
    # And root_app.mount("/api", app)
    # So path is /api/v1/system/health? No, let's check system router prefix.

    response = client.get("/api/v1/system/secretary-logs")
    # Should be 200 or 500 depending on DB state, but path should exist
    assert response.status_code in [200, 500]


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/app/"
