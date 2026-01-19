"""
Consensus AI — Sentinel Package
================================

The Sentinel is the system's immune layer that detects anomalies and drift.
"""

from sentinel.sentinel import Sentinel
from sentinel.rules import (
    RuleRegistry,
    Alert,
    AlertSeverity,
    AlertCategory,
    SentinelRule,
    sentinel_rule,
    get_registry,
)

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
