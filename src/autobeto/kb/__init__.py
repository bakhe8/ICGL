"""
Consensus AI — Knowledge Base Package
======================================

This package contains the core schemas and Knowledge Base implementation.

Modules:
- schemas: Dataclass definitions for all canonical entities.
- knowledge_base: In-memory Knowledge Base with validation.
"""

from .schemas import (
    ID,
    Timestamp,
    DecisionAction,
    Concept,
    Policy,
    SentinelSignal,
    ADR,
    HumanDecision,
    LearningLog,
    now,
    uid,
)
from .knowledge_base import KnowledgeBase

__all__ = [
    "ID",
    "Timestamp",
    "DecisionAction",
    "Concept",
    "Policy",
    "SentinelSignal",
    "ADR",
    "HumanDecision",
    "LearningLog",
    "KnowledgeBase",
    "now",
    "uid",
]
