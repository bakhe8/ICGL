def _register_internal_agents(self):
    """Register the internal set of agents used by the governance engine.

    This function builds and returns a list of instantiated agent objects.
    """
    from shared.python.agents.architect import ArchitectAgent
    from shared.python.agents.builder import BuilderAgent
    from shared.python.agents.failure import FailureAgent
    from shared.python.agents.guardian import ConceptGuardian
    from shared.python.agents.policy import PolicyAgent
    from shared.python.agents.sentinel_agent import SentinelAgent
    from shared.python.agents.specialists import CodeSpecialist
    from shared.python.agents.testing import TestingAgent
    from shared.python.agents.verification import VerificationAgent

    agents = [
        ArchitectAgent(),
        BuilderAgent(),
        FailureAgent(),
        PolicyAgent(),
        ConceptGuardian(),
        SentinelAgent(self.sentinel),
        CodeSpecialist(),
        VerificationAgent(),
        TestingAgent(),
    ]
    return agents
