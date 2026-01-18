import json
from icgl.kb.storage import StorageBackend
from icgl.kb.schemas import Procedure, OperationalRequest


def test_procedure_persistence(tmp_path):
    db = tmp_path / "kb.db"
    storage = StorageBackend(str(db))

    proc = Procedure(
        id="proc-1",
        code="SOP-DEV-01",
        title="Deploy service",
        type="SOP",
        steps=["Step 1", "Step 2"],
        required_tools=["git", "docker"],
    )
    storage.save_procedure(proc)

    loaded = storage.load_all_procedures()
    assert "proc-1" in loaded
    saved = loaded["proc-1"]
    assert saved.title == "Deploy service"
    assert saved.steps == ["Step 1", "Step 2"]


def test_operational_request_persistence(tmp_path):
    db = tmp_path / "kb.db"
    storage = StorageBackend(str(db))

    req = OperationalRequest(
        id="req-1",
        requester_id="agent-1",
        target_department="infra",
        requirement="Provision runner",
        rationale="Needed for CI",
        urgency="HIGH",
        expected_output="Runner ready",
        risk_level="MEDIUM",
    )
    storage.save_operational_request(req)

    loaded = storage.load_all_operational_requests()
    assert "req-1" in loaded
    saved = loaded["req-1"]
    assert saved.status == "PENDING"
    assert saved.target_department == "infra"
