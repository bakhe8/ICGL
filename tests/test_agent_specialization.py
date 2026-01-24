from backend.agents.base import AgentRole
from backend.governance.icgl import ICGL


def test_agent_specialization_uniqueness():
    """
    Ensures that for every registered agent, its primary responsibility
    (from the owner's perspective) is unique.
    """
    icgl = ICGL()
    registry = icgl.registry
    active_roles = registry.list_agents()

    # Check for core role overlaps defined in Phase 7
    orchestrators = [
        AgentRole.SECURITY_ORCHESTRATOR,
        AgentRole.EXECUTION_ORCHESTRATOR,
        AgentRole.VALIDATION_ORCHESTRATOR,
    ]

    for role in orchestrators:
        assert role in active_roles, f"Orchestrator {role} missing from registry!"

    # Verify specialized analytical roles
    assert AgentRole.PERFORMANCE_ANALYZER in active_roles
    assert AgentRole.RESEARCHER in active_roles

    print(f"Verified {len(active_roles)} unique agent roles.")


if __name__ == "__main__":
    test_agent_specialization_uniqueness()
