"""
Consensus AI — Canonical Schemas
=================================

This module defines the canonical data structures for all Knowledge Base entities.

See: docs/consensus_ai_knowledge_base_v_0.md for full schema spec.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import datetime
import uuid


# ==========================================================================
# 🔹 Core Types
# ==========================================================================

ID = str  # Unique identifier for any entity
Timestamp = str  # ISO-8601 formatted timestamp

DecisionAction = Literal["APPROVE", "REJECT", "MODIFY", "EXPERIMENT"]


def now() -> Timestamp:
    """Returns the current UTC timestamp in ISO-8601 format."""
    return datetime.utcnow().isoformat()


def uid() -> ID:
    """Generates a unique identifier (UUID v4)."""
    return str(uuid.uuid4())


# ==========================================================================
# 🧠 Entity Schemas
# ==========================================================================

@dataclass
class Concept:
    """
    A Concept is a foundational definition that must remain stable.
    
    Attributes:
        invariants: Rules that must ALWAYS hold for this concept.
        anti_patterns: Common mistakes to avoid.
        owner: Always "HUMAN" — concepts are under human sovereignty.
    """
    id: ID
    name: str
    definition: str
    invariants: List[str]
    anti_patterns: List[str]
    owner: Literal["HUMAN"] = "HUMAN"
    version: str = "1.0.0"
    created_at: Timestamp = field(default_factory=now)
    updated_at: Timestamp = field(default_factory=now)


@dataclass
class Policy:
    """
    A Policy is a hard constraint that cannot be overridden.
    
    Attributes:
        code: Follows pattern P-[AREA]-[NUMBER] (e.g., P-ARCH-04).
        severity: LOW | MEDIUM | HIGH | CRITICAL
        enforced_by: Components responsible for enforcing this policy.
    """
    id: ID
    code: str
    title: str
    rule: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    enforced_by: List[str]
    created_at: Timestamp = field(default_factory=now)


@dataclass
class SentinelSignal:
    """
    A Sentinel Signal represents a detectable risk or anomaly.
    
    Attributes:
        category: Type of risk (Drift, Authority, Cost, Safety, Integrity).
        default_action: What Sentinel should do when this signal fires.
    """
    id: ID
    name: str
    description: str
    category: Literal["Drift", "Authority", "Cost", "Safety", "Integrity"]
    detection_hint: str
    default_action: Literal["ALLOW", "CONTAIN", "ESCALATE"]
    introduced_in_cycle: int


@dataclass
class ADR:
    """
    An ADR (Architectural Decision Record) captures a significant decision.
    
    Attributes:
        status: DRAFT | CONDITIONAL | ACCEPTED | REJECTED | EXPERIMENTAL
        human_decision_id: Links to the human sovereign signature.
    """
    id: ID
    title: str
    status: Literal["DRAFT", "CONDITIONAL", "ACCEPTED", "REJECTED", "EXPERIMENTAL"]
    context: str
    decision: str
    consequences: List[str]
    related_policies: List[ID]
    sentinel_signals: List[ID]
    human_decision_id: Optional[ID]
    created_at: Timestamp = field(default_factory=now)


@dataclass
class HumanDecision:
    """
    A Human Decision is the sovereign signature on an ADR.
    
    Attributes:
        signature_hash: Cryptographic signature (placeholder for HSM).
    """
    id: ID
    adr_id: ID
    action: DecisionAction
    rationale: str
    signed_by: str
    signature_hash: str
    timestamp: Timestamp = field(default_factory=now)


@dataclass
class LearningLog:
    """
    A Learning Log captures the evolution of knowledge after each ICGL cycle.
    """
    cycle: int
    summary: str
    new_policies: List[ID]
    new_signals: List[ID]
    new_concepts: List[ID]
    notes: str
