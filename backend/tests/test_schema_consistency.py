<<<<<<< HEAD
from backend.agents.base import AgentResult, AgentRole
from modules.kb.schemas import ADR, HumanDecision
=======
from shared.python.agents_shared.agents.base import AgentResult, AgentRole
from shared.python.kb_shared.kb.schemas import ADR, HumanDecision
>>>>>>> 1017ee5d6165b6b836bcf8f4a86dd3b8c5d9a8a4


def test_agent_result_schema_completeness():
    result = AgentResult(
        agent_id="test-agent",
        role=AgentRole.ARCHITECT,
        analysis="Test analysis",
        required_agents=["failure"],
        summoning_rationale="Testing rationale",
    )
    assert result.required_agents == ["failure"]
    assert result.summoning_rationale == "Testing rationale"


def test_adr_human_decision_harmony():
    adr = ADR(
        id="adr-1",
        title="Test ADR",
        status="DRAFT",
        context="Context",
        decision="Decision",
        consequences=[],
        related_policies=[],
        sentinel_signals=[],
    )
    # Check new fields
    assert hasattr(adr, "action")
    assert hasattr(adr, "updated_at")

    decision = HumanDecision(
        id="dec-1",
        adr_id="adr-1",
        action="APPROVE",
        rationale="Rationale",
        signed_by="human",
        signature_hash="hash",
    )
    assert decision.created_at is not None
    assert decision.timestamp is not None
