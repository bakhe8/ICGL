"""
Consensus AI — Sentinel Package
================================

The Sentinel is the system's immune layer that detects anomalies and drift.
"""

from src.core.sentinel.rules import (
    Alert,
    AlertCategory,
    AlertSeverity,
    RuleRegistry,
    SentinelRule,
    get_registry,
    sentinel_rule,
)
from src.core.sentinel.sentinel import Sentinel

__all__ = [
    "Sentinel",
    "RuleRegistry",
    "Alert",
    "AlertSeverity",
    "AlertCategory",
    "SentinelRule",
    "sentinel_rule",
    "get_registry",
]
