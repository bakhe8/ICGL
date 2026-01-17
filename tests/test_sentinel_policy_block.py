from icgl.api.server import get_icgl
from icgl.hdal.hdal import HDAL
from icgl.agents.registry import SynthesizedResult
from icgl.agents.base import AgentResult, AgentRole
from icgl.kb.schemas import ADR
from icgl.sentinel.rules import Alert, AlertSeverity, AlertCategory


def test_hdal_blocks_on_critical_sentinel():
    icgl = get_icgl()
    hdal = icgl.hdal
    adr = ADR(
        id="TEST-BLOCK",
        title="Test Block",
        status="DRAFT",
        context="",
        decision="",
        consequences=[],
        related_policies=[],
        sentinel_signals=[],
        human_decision_id=None,
    )
    synthesis = SynthesizedResult(
        individual_results=[
            AgentResult(
                agent_id="a1",
                role=AgentRole.ARCHITECT,
                analysis="ok",
                confidence=0.8,
            )
        ],
        consensus_recommendations=[],
        all_concerns=[],
        overall_confidence=0.8,
    )
    sentinel_alerts = [Alert(rule_id="S-CRIT", severity=AlertSeverity.CRITICAL, message="block", category=AlertCategory.AUTHORITY)]
    result = hdal.review_and_sign(adr, synthesis, human_id="tester", policy_report=None, sentinel_alerts=sentinel_alerts)
    assert result is None
