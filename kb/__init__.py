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

from kb.schemas import (
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
from kb.knowledge_base import KnowledgeBase
from kb.storage import StorageBackend
from kb.persistent import PersistentKnowledgeBase

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
