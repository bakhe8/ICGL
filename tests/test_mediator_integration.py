import asyncio
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from backend.agents.base import Agent, AgentResult, AgentRole, Problem
from backend.agents.mediator import MediatorAgent
from backend.agents.registry import AgentRegistry


class LowConfidenceAgent(Agent):
    def __init__(self):
        super().__init__("low-conf", AgentRole.ARCHITECT)

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis="Confusing analysis",
            confidence=0.4,
            concerns=["Major concern 1", "Major concern 2"],
        )


@pytest.mark.asyncio
async def test_mediator_auto_invocation():
    # Setup registry with a low confidence agent and a mediator
    registry = AgentRegistry()

    # We need to mock the LLM provider for the registry or ensure it doesn't fail
    # Since we are testing the logic in run_and_synthesize, we can just register the agents

    # Mock LLM provider to avoid real API calls
    class MockLLM:
        async def generate(self, req):
            class Resp:
                content = "Mediation: We should proceed with caution."

            return Resp()

    registry._llm_provider = MockLLM()

    registry.register(LowConfidenceAgent())
    registry.register(MediatorAgent(llm_provider=registry._llm_provider))

    problem = Problem(title="Test Problem", context="Test Context")
    kb = None  # Not used in these agents

    # Run synthesis
    result = await registry.run_and_synthesize(problem, kb)

    # Verify that overall confidence is low (0.4)
    assert result.overall_confidence < 0.7

    # Verify that mediation was triggered
    assert result.mediation is not None
    assert result.mediation["agent_id"] == "agent-mediator"
    assert "Mediation" in result.mediation["analysis"]

    print("✅ MediatorAgent auto-invocation verified!")


if __name__ == "__main__":
    asyncio.run(test_mediator_auto_invocation())
