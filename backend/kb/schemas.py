"""
Consensus AI — Canonical Schemas
=================================

This module defines the canonical data structures for all Knowledge Base entities.

See: docs/icgl_knowledge_base_v1.md for full schema spec.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

# ==========================================================================
# 🔹 Core Types
# ==========================================================================

ID = str  # Unique identifier for any entity
Timestamp = str  # ISO-8601 formatted timestamp

DecisionAction = Literal["APPROVE", "REJECT", "MODIFY", "EXPERIMENT"]


def now() -> Timestamp:
    """Returns the current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


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
    human_decision_id: Optional[ID] = None
    intent: Optional[Dict[str, Any]] = field(default=None)  # Layer 1: Intent Contract
    file_changes: List[Any] = field(
        default_factory=list
    )  # Staged changes for Sentinel review
    action: Optional[str] = None  # For UI alignment
    created_at: Timestamp = field(default_factory=now)
    updated_at: Timestamp = field(default_factory=now)


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
    created_at: Timestamp = field(default_factory=now)  # Alias for timestamp
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


@dataclass
class InterventionLog:
    """
    Tracks when a Human rejects or modifies an agent recommendation.
    "The System watches the Human watching the System."

    Attributes:
        adr_id: The decision being made.
        original_recommendation: What the agents wanted.
        human_action: What the human did (REJECT/MODIFY).
        reason: Why the human intervened.
        diff_summary: If modified, what changed?
    """

    id: ID
    adr_id: ID
    original_recommendation: str
    human_action: DecisionAction
    reason: str
    diff_summary: Optional[str] = None
    timestamp: Timestamp = field(default_factory=now)


@dataclass
class AgentMetric:
    """
    Performance telemetry for an agent.
    """

    agent_id: str
    role: str
    task_type: str
    latency_ms: float
    confidence_score: float
    success: bool
    error_code: Optional[str] = None
    timestamp: Timestamp = field(default_factory=now)


@dataclass
class RoadmapItem:
    """
    A Roadmap Item represents a governed phase or milestone in the execution plan.

    Manifesto Reference:
    - "Planning is Governance."

    Attributes:
        cycle: The cycle number (e.g., 1, 2)
        title: Title of the phase/cycle.
        status: Literal["PLANNED", "ACTIVE", "COMPLETED", "BLOCKED"]
        goals: List of high-level goals.
        governed_by_adr: ID of the ADR authorizing this cycle.
    """

    id: ID
    cycle: int
    title: str
    status: Literal["PLANNED", "ACTIVE", "COMPLETED", "BLOCKED"]
    goals: List[str]
    governed_by_adr: Optional[ID]
    created_at: Timestamp = field(default_factory=now)
    updated_at: Timestamp = field(default_factory=now)


@dataclass
class FileChange:
    """
    Represents a proposed physical file modification.
    """

    path: str
    content: str
    action: Literal["CREATE", "UPDATE", "DELETE"] = "CREATE"
