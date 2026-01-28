from unittest.mock import patch

import pytest

from src.core.governance.icgl import ICGL
from src.core.kb.schemas import ADR, HumanDecision, now, uid


@pytest.mark.asyncio
async def test_high_payload_stress(tmp_path):
    """
    Verify system handles ADRs with extremely large context (50KB+)
    without memory exhaustion or DB failures.
    """
    db_file = tmp_path / "stress_kb.db"

    with (
        patch("src.core.agents.infrastructure.registry.OpenAIProvider"),
        patch.dict("os.environ", {"OPENAI_API_KEY": "sk-dummy"}),
    ):
        engine = ICGL(db_path=str(db_file), enforce_runtime_guard=False)

    # 50KB of Junk Context
    large_context = "REPEAT DATA " * 5000

    adr = ADR(
        id="STRESS-001",
        title="Big Payload",
        status="DRAFT",
        context=large_context,
        decision="Accept big data",
        consequences=[],
        related_policies=[],
        sentinel_signals=[],
        human_decision_id=None,
    )

    # Mock HDAL
    engine.hdal.review_and_sign = lambda a, s, h_id, **kwargs: HumanDecision(
        id=uid(),
        adr_id=a.id,
        action="APPROVE",
        rationale="Stress test done",
        signed_by=h_id,
        timestamp=now(),
        signature_hash="stress-sig",
    )

    # Execute Cycle
    decision = await engine.run_governance_cycle(adr, "stress-tester")
    assert decision is not None

    # Verify persistence
    loaded = engine.kb.adrs.get("STRESS-001")
    assert loaded is not None
    assert len(loaded.context) > 50000

    print(f"✅ Stress Test Passed: Processed ADR with {len(large_context)} chars.")
