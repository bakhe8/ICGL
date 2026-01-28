from unittest.mock import MagicMock

from src.core.kb.schemas import ADR, uid
from src.core.sentinel.sentinel import Sentinel


def test_sentinel_scan_clean():
    sentinel = Sentinel()
    adr = ADR(
        id=uid(),
        title="Normal",
        status="DRAFT",
        context="Safe content",
        decision="Safe",
        consequences=[],
        related_policies=[],
        sentinel_signals=[],
        human_decision_id=None,
    )
    mock_kb = MagicMock()

    alerts = sentinel.scan_adr(adr, mock_kb)
    assert isinstance(alerts, list)


def test_sentinel_alert_detection():
    sentinel = Sentinel()
    # Content with known threat (e.g. bypass human) if matches rules.py logic
    adr = ADR(
        id=uid(),
        title="Threat",
        status="DRAFT",
        context="bypass human oversight",
        decision="skip signature",
        consequences=[],
        related_policies=[],
        sentinel_signals=[],
        human_decision_id=None,
    )
    mock_kb = MagicMock()

    alerts = sentinel.scan_adr(adr, mock_kb)
    # S-06 should trigger for "bypass human"
    assert len(alerts) > 0
