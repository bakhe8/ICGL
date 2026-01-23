import asyncio
from unittest.mock import AsyncMock

import pytest

from backend.agents.base import AgentRole, IntentContract, Problem
from backend.agents.mediator import MediatorAgent


@pytest.mark.asyncio
async def test_mediator_reconciliation():
    """Tests that Mediator can reconcile conflicting agent results."""
    # 1. Setup
    mediator = MediatorAgent()
    # Mock LLM Client
    mediator.llm_client.generate_json = AsyncMock(
        return_value={
            "consensus_reached": True,
            "analysis": "Reconciled interpretation.",
            "recommendations": ["Follow plan A"],
        }
    )

    intent = IntentContract(goal="Test Goal", risk_level="medium")
    problem = Problem(
        title="Test Conflict",
        context="Context",
        intent=intent,
        metadata={
            "agent_results": [
                {
                    "agent_id": "agent-failure",
                    "confidence": 0.5,
                    "understanding": {"interpretation": "High risk"},
                },
                {
                    "agent_id": "agent-guardian",
                    "confidence": 0.9,
                    "understanding": {"interpretation": "Low risk"},
                },
            ]
        },
    )

    # 2. Execute
    result = await mediator._analyze(problem, None)

    # 3. Verify
    assert result.role == AgentRole.MEDIATOR
    assert "Reconciled" in result.analysis
    assert result.confidence == 0.9
    assert result.clarity_needed is False


@pytest.mark.asyncio
async def test_mediator_escalation():
    """Tests that Mediator escalates when consensus is not reached."""
    mediator = MediatorAgent()
    mediator.llm_client.generate_json = AsyncMock(
        return_value={
            "consensus_reached": False,
            "analysis": "Fundamental conflict detected.",
            "recommendations": [],
        }
    )

    problem = Problem(
        title="Conflict",
        context="...",
        metadata={"agent_results": [{"agent_id": "a", "confidence": 0.1}]},
    )

    result = await mediator._analyze(problem, None)

    assert result.clarity_needed is True
    assert "conflict" in result.clarity_question.lower()


if __name__ == "__main__":
    # Small helper to run async tests if executed as script
    async def run_all():
        try:
            await test_mediator_reconciliation()
            print("✅ test_mediator_reconciliation passed")
            await test_mediator_escalation()
            print("✅ test_mediator_escalation passed")
        except Exception as e:
            print(f"❌ Tests failed: {e}")
            import traceback

            traceback.print_exc()

    asyncio.run(run_all())
