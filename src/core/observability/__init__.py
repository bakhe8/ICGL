"""
ICGL Observability Subsystem
=============================

Complete visibility into agent interactions for supervised coordination.

Phase 1: Foundation for future direct channel routing.
"""

from .events import (
    EventType,
    ObservabilityEvent,
)
from .ledger import ObservabilityLedger
from .instrumentation import observe, init_observability, get_ledger

__all__ = [
    "EventType",
    "ObservabilityEvent",
    "ObservabilityLedger",
    "observe",
    "init_observability",
    "get_ledger",
]
