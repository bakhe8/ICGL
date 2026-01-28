import asyncio
from unittest.mock import patch

import pytest

from src.core.governance.icgl import ICGL
from src.core.kb.schemas import ADR, HumanDecision, now, uid


@pytest.mark.asyncio
async def test_concurrent_governance_cycles(tmp_path):
    """
    Simulate multiple concurrent ADR proposals to verify:
    1. SQLite concurrency handling (locking/retries).
    2. Merkle ledger chain integrity under parallel load.
    """
    db_file = tmp_path / "concurrent_kb.db"

    with (
        patch("src.core.agents.infrastructure.registry.OpenAIProvider"),
        patch.dict("os.environ", {"OPENAI_API_KEY": "sk-dummy"}),
    ):
        engine = ICGL(db_path=str(db_file), enforce_runtime_guard=False)

    # Mock HDAL to always approve
    engine.hdal.review_and_sign = lambda a, s, h_id, **kwargs: HumanDecision(
        id=uid(),
        adr_id=a.id,
        action="APPROVE",
        rationale="Concurrent Test Approval",
        signed_by=h_id,
        timestamp=now(),
        signature_hash=f"sig-{a.id}",
    )

    # Create 5 parallel ADR tasks
    num_tasks = 5
    adrs = [
        ADR(
            id=f"ADR-CONC-{i}",
            title=f"Parallel Decision {i}",
            status="DRAFT",
            context="Testing concurrency",
            decision="Scale the system",
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )
        for i in range(num_tasks)
    ]

    # Run them concurrently
    tasks = [engine.run_governance_cycle(adr, "tester") for adr in adrs]
    results = await asyncio.gather(*tasks)

    # Verify all decisions were recorded
    assert all(r is not None for r in results)
    # 2 seed ADRs + 5 concurrently added = 7
    assert len(engine.kb.adrs) == num_tasks + 2

    # Verify Merkle Chain Integrity
    is_valid, broken_at = engine.observer.verify_merkle_chain()
    assert is_valid, f"Merkle chain broken at index {broken_at} during concurrency test"

    # Verify Ledger length (should be equal to num_tasks)
    ledger = engine.kb.get_merkle_ledger()
    if len(ledger) != num_tasks:
        print("\nDEBUG: Merkle Ledger Content:")
        for node in ledger:
            print(f"Index: {node['node_index']}, Hash: {node['node_hash'][:10]}..., Payload: {node['payload'][:50]}...")

    assert len(ledger) == num_tasks

    print(f"✅ Concurrency Test Passed: {num_tasks} decisions processed in parallel.")
