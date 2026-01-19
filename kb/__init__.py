"""
Consensus AI — Knowledge Base Package
======================================

This package contains the core schemas and Knowledge Base implementation.

Modules:
- schemas: Dataclass definitions for all canonical entities.
- knowledge_base: In-memory Knowledge Base with validation.
- storage: SQLite persistence backend.
- persistent: Persistent Knowledge Base with auto-save.
"""

from .schemas import (
    ID,
    Timestamp,
    DecisionAction,
    Concept,
    Policy,
    SentinelSignal,
    ADR,
    FastTrackADR,
    HumanDecision,
    LearningLog,
    now,
    uid,
    Procedure,
    ProcedureType,
    OperationalRequest
)
from .knowledge_base import KnowledgeBase
from .storage import StorageBackend
from .persistent import PersistentKnowledgeBase

__all__ = [
    "ID",
    "Timestamp",
    "DecisionAction",
    "Concept",
    "Policy",
    "SentinelSignal",
    "ADR",
    "FastTrackADR",
    "HumanDecision",
    "LearningLog",
    "InterventionLog",
    "FileChange",
    "KnowledgeBase",
    "StorageBackend",
    "PersistentKnowledgeBase",
    "now",
    "uid",
]
