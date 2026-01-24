import pytest

from backend.agents.base import AgentResult, AgentRole, Problem
from backend.governance import ICGL


@pytest.mark.asyncio
async def test_agent_contract_compliance():
    """
    Verify that all registered agents return a standardized AgentResult
    with the 'metadata' field (Phase 5 Hardening).
    """
    icgl = ICGL()
    registry = icgl.registry

    # Test a few core agents
    test_roles = [
        AgentRole.ARCHITECT,
        AgentRole.POLICY,
        AgentRole.DEVOPS,
        AgentRole.CHAOS,
    ]

    problem = Problem(title="Contract Test", context="Checking schema consistency.")

    for role in test_roles:
        agent = registry.get_agent(role)
        if not agent:
            continue

        result = await agent.analyze(problem, None)
        assert isinstance(result, AgentResult)
        assert hasattr(result, "metadata")
        assert isinstance(result.metadata, dict)
        assert result.agent_id is not None
        assert result.role == role
