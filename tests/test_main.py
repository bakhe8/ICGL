from fastapi.testclient import TestClient

from api.server import app

client = TestClient(app)


def test_read_test_endpoint():
    response = client.get("/test-endpoint")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a test endpoint"}
