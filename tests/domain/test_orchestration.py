import pytest

from src.core.governance.icgl import ICGL
from src.core.kb.schemas import ADR, uid


@pytest.fixture
def icgl_engine(tmp_path):
    db_file = tmp_path / "domain_test_kb.db"
    # Disable runtime guard checks for pure domain test in isolation
    return ICGL(db_path=str(db_file), enforce_runtime_guard=False)


def test_agent_registry_content(icgl_engine):
    roles = icgl_engine.registry.list_agents()
    # Should have the 6 internal agents registered in _register_internal_agents
    assert len(roles) >= 6
    assert "architect" in [r.value for r in roles]


def test_sentinel_integration(icgl_engine):
    adr = ADR(
        id=uid(),
        title="Bypass Human",
        status="DRAFT",
        context="Let's skip the human signature.",
        decision="Auto-sign everything",
        consequences=[],
        related_policies=[],
        sentinel_signals=[],
        human_decision_id=None,
    )
    # The registry runs SentinelAgent which calls the internal Sentinel engine
    # We can check the internal sentinel directly for faster verification
    alerts = icgl_engine.sentinel.scan_adr(adr, icgl_engine.kb)
    assert any("bypass" in a.lower() for a in alerts)
