import time
from fastapi.testclient import TestClient
from icgl.api.server import app  # noqa: E402


def test_propose_and_sign_flow():
    client = TestClient(app)
    # Propose ADR
    resp = client.post("/propose", json={
        "title": "Test ADR Flow",
        "context": "Ensure end-to-end governance works",
        "decision": "Sample decision content",
        "human_id": "tester"
    })
    assert resp.status_code == 200
    adr_id = resp.json()["adr_id"]

    # Poll analysis result
    synthesis = None
    for _ in range(20):
        r = client.get(f"/analysis/{adr_id}")
        if r.status_code == 200 and "synthesis" in r.json():
            synthesis = r.json()["synthesis"]
            break
        time.sleep(0.2)
    assert synthesis is not None

    # Sign decision
    r = client.post(f"/sign/{adr_id}", json={
        "action": "APPROVE",
        "rationale": "Test approval",
        "human_id": "tester"
    })
    assert r.status_code == 200
    assert r.json()["status"] == "Complete"
