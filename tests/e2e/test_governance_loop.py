import pytest

from src.core.governance.icgl import ICGL
from src.core.kb.schemas import ADR, uid


@pytest.mark.asyncio
async def test_full_governance_loop(tmp_path):
    # 1. Setup Engine
    db_file = tmp_path / "e2e_governance.db"
    # Ensure OPENAI_API_KEY is available or mock provider if needed.
    # For CI/Harness stability, we'll assume the environment is set.
    engine = ICGL(db_path=str(db_file), enforce_runtime_guard=False)

    # 2. Propose ADR
    adr = ADR(
        id=uid(),
        title="E2E Stability Test",
        status="DRAFT",
        context="We are verifying the full governance loop after layout redesign.",
        decision="Implement comprehensive automated testing.",
        consequences=["Increased stability", "Lower technical debt"],
        related_policies=["P-CORE-01"],
        sentinel_signals=[],
        human_decision_id=None,
    )

    # 3. Save initial ADR to KB (simulating initial proposal)
    engine.kb.add_adr(adr)

    # 4. Run Cycle (Async)
    # Simulator: Human decides to APPROVE
    # We mock HDAL for E2E speed/automation
    from src.core.kb.schemas import HumanDecision, now

    engine.hdal.review_and_sign = lambda a, s, h_id, **kwargs: HumanDecision(
        id=uid(),
        adr_id=a.id,
        action="APPROVE",
        rationale="Verified via E2E test suite.",
        signed_by=h_id,
        timestamp=now(),
        signature_hash="xyz-abc",
    )

    decision = await engine.run_governance_cycle(adr, "admin-user")

    # 5. Verify Results
    assert decision is not None
    assert decision.action == "APPROVE"

    # Check KB state
    updated_adr = engine.kb.adrs.get(adr.id)
    assert updated_adr.status == "ACCEPTED"
    assert updated_adr.human_decision_id == decision.id

    print(f"✅ E2E Loop Passed: ADR {adr.id} is now {updated_adr.status}")
