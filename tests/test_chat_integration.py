from fastapi.testclient import TestClient
from icgl.api.server import app


def test_chat_analysis_flow():
    client = TestClient(app)
    resp = client.post("/chat", json={"message": "Analyze migration to TypeScript", "session_id": "sess-analysis"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["messages"]
    assert data["state"].get("waiting_for_human") is not None
    assert data["state"].get("mode") in {"explore", "experiment"}


def test_chat_websocket_broadcast():
    client = TestClient(app)
    with client.websocket_connect("/ws/chat") as ws:
        resp = client.post("/chat", json={"message": "Analyze broadcast", "session_id": "sess-ws"})
        assert resp.status_code == 200
        msg = ws.receive_json()
        assert "messages" in msg
        assert msg.get("state") is not None
