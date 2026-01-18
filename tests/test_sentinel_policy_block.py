from icgl.api.server import get_icgl
from icgl.hdal.hdal import HDAL
from icgl.agents.registry import SynthesizedResult
from icgl.agents.base import AgentResult, AgentRole
from icgl.kb.schemas import ADR
from icgl.sentinel.rules import Alert, AlertSeverity, AlertCategory
from icgl.sentinel.sentinel import Sentinel
import asyncio


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


class _StubLLM:
    """LLM stub to keep sentinel online-only while avoiding network in this test."""
    mock_mode = True

    async def generate_json(self, system_prompt, user_prompt, config=None):
        return {}


def test_sentinel_s05_strategic_lock_detected():
    async def _run():
        sentinel = Sentinel(llm_client=_StubLLM())
        adr = ADR(
            id="ADR-S05",
            title="Irreversible decision",
            status="DRAFT",
            context="Plan describes an irreversible migration path.",
            decision="This is a one-way cutover with no rollback.",
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )
        alerts = await sentinel.scan_adr_detailed_async(adr, kb=None)
        assert any(a.rule_id == "S-05" or ("strategic optionality" in a.message.lower()) for a in alerts)

    asyncio.run(_run())
