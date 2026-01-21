"""ICGL Knowledge Base package.

Exports canonical schema types and the `KnowledgeBase` implementation.
"""

from .knowledge_base import KnowledgeBase
from .schemas import (
    ADR,
    Concept,
    Policy,
    Procedure,
    SentinelSignal,
    HumanDecision,
    LearningLog,
    RoadmapItem,
    FastTrackADR,
    OperationalRequest,
    Proposal,
    uid,
    now,
)

# Legacy alias for CLI compatibility
PersistentKnowledgeBase = KnowledgeBase

__all__ = [
    "KnowledgeBase",
    "PersistentKnowledgeBase",
    "ADR",
    "FastTrackADR",
    "Concept",
    "Policy",
    "Procedure",
    "SentinelSignal",
    "HumanDecision",
    "LearningLog",
    "RoadmapItem",
    "OperationalRequest",
    "Proposal",
    "uid",
    "now",
]
