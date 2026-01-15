"""
Consensus AI — Skeleton Repository (Python)
-------------------------------------------
This file bootstraps the core architecture as a runnable skeleton.
It intentionally focuses on structure, contracts, and governance hooks
rather than full implementation.

Future direction:
- Split into package modules once validated (kb/, governance/, sentinel/, hdal/, cli/)
- Replace in-memory stores with persistence
- Add schema validation and orchestration
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from datetime import datetime
import uuid

# ==========================================================
# 🔹 Core Types
# ==========================================================

ID = str
Timestamp = str

DecisionAction = Literal["APPROVE", "REJECT", "MODIFY", "EXPERIMENT"]


def now() -> Timestamp:
    return datetime.utcnow().isoformat()


def uid() -> ID:
    return str(uuid.uuid4())


# ==========================================================
# 🧠 Knowledge Base Schemas (Canonical)
# ==========================================================

@dataclass
class Concept:
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
    id: ID
    code: str
    title: str
    rule: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    enforced_by: List[str]
    created_at: Timestamp = field(default_factory=now)


@dataclass
class SentinelSignal:
    id: ID
    name: str
    description: str
    category: Literal["Drift", "Authority", "Cost", "Safety", "Integrity"]
    detection_hint: str
    default_action: Literal["ALLOW", "CONTAIN", "ESCALATE"]
    introduced_in_cycle: int


@dataclass
class ADR:
    id: ID
    title: str
    status: Literal[
        "DRAFT", "CONDITIONAL", "ACCEPTED", "REJECTED", "EXPERIMENTAL"
    ]
    context: str
    decision: str
    consequences: List[str]
    related_policies: List[ID]
    sentinel_signals: List[ID]
    human_decision_id: Optional[ID]
    created_at: Timestamp = field(default_factory=now)


@dataclass
class HumanDecision:
    id: ID
    adr_id: ID
    action: DecisionAction
    rationale: str
    signed_by: str
    signature_hash: str
    timestamp: Timestamp = field(default_factory=now)


@dataclass
class LearningLog:
    cycle: int
    summary: str
    new_policies: List[ID]
    new_signals: List[ID]
    new_concepts: List[ID]
    notes: str


# ==========================================================
# 📚 In-Memory Knowledge Base (v0)
# ==========================================================

class KnowledgeBase:
    """
    Source of Truth for all canonical knowledge.
    Later: replace with persistent storage + validation layer.
    """

    def __init__(self):
        self.concepts: Dict[ID, Concept] = {}
        self.policies: Dict[ID, Policy] = {}
        self.signals: Dict[ID, SentinelSignal] = {}
        self.adrs: Dict[ID, ADR] = {}
        self.human_decisions: Dict[ID, HumanDecision] = {}
        self.learning_log: List[LearningLog] = []

    # ----------------------------
    # Registration APIs
    # ----------------------------

    def add_concept(self, concept: Concept):
        self.concepts[concept.id] = concept

    def add_policy(self, policy: Policy):
        self.policies[policy.id] = policy

    def add_signal(self, signal: SentinelSignal):
        self.signals[signal.id] = signal

    def add_adr(self, adr: ADR):
        self.adrs[adr.id] = adr

    def add_human_decision(self, decision: HumanDecision):
        self.human_decisions[decision.id] = decision

    def add_learning_log(self, log: LearningLog):
        self.learning_log.append(log)


# ==========================================================
# 🛡️ Sentinel (Stub)
# ==========================================================

class Sentinel:
    """
    Detects anomalies, drift, and policy violations.
    This is a stub – real detection logic comes later.
    """

    def scan_adr(self, adr: ADR, kb: KnowledgeBase) -> List[str]:
        alerts: List[str] = []

        # Example placeholder rule
        if adr.status == "DRAFT" and not adr.related_policies:
            alerts.append("ADR has no related policies")

        return alerts


# ==========================================================
# 🏛️ Human Decision Authority Layer (Stub)
# ==========================================================

class HDAL:
    """
    Human Decision Authority Layer.
    All sovereign decisions must pass through here.
    """

    def sign_decision(
        self,
        adr_id: ID,
        action: DecisionAction,
        rationale: str,
        human_id: str,
    ) -> HumanDecision:
        # Placeholder signature (to be replaced with crypto / HSM later)
        signature = f"signed-by:{human_id}:{adr_id}:{now()}"

        return HumanDecision(
            id=uid(),
            adr_id=adr_id,
            action=action,
            rationale=rationale,
            signed_by=human_id,
            signature_hash=signature,
        )


# ==========================================================
# 🔁 ICGL Orchestrator (Minimal)
# ==========================================================

class ICGL:
    """
    Minimal orchestration of one governance cycle.
    """

    def __init__(self, kb: KnowledgeBase, sentinel: Sentinel, hdal: HDAL):
        self.kb = kb
        self.sentinel = sentinel
        self.hdal = hdal

    def run_cycle(self, adr: ADR, human_id: str):
        print(f"[ICGL] Starting cycle for ADR: {adr.title}")

        # 1. Register ADR
        self.kb.add_adr(adr)

        # 2. Sentinel scan
        alerts = self.sentinel.scan_adr(adr, self.kb)
        if alerts:
            print("[Sentinel Alerts]")
            for a in alerts:
                print(" -", a)

        # 3. Human decision (simulated)
        decision = self.hdal.sign_decision(
            adr_id=adr.id,
            action="APPROVE",
            rationale="Bootstrap approval",
            human_id=human_id,
        )

        self.kb.add_human_decision(decision)
        adr.human_decision_id = decision.id

        # 4. Learning log
        self.kb.add_learning_log(
            LearningLog(
                cycle=len(self.kb.learning_log) + 1,
                summary=f"Processed ADR {adr.id}",
                new_policies=[],
                new_signals=[],
                new_concepts=[],
                notes="Bootstrap cycle",
            )
        )

        print("[ICGL] Cycle completed")


# ==========================================================
# 🚀 Demo Bootstrap
# ==========================================================

def run_demo():
    kb = KnowledgeBase()
    sentinel = Sentinel()
    hdal = HDAL()
    icgl = ICGL(kb, sentinel, hdal)

    # Example ADR
    adr = ADR(
        id=uid(),
        title="Bootstrap Example ADR",
        status="DRAFT",
        context="Initial skeleton validation",
        decision="Validate ICGL skeleton",
        consequences=["System structure validated"],
        related_policies=[],
        sentinel_signals=[],
        human_decision_id=None,
    )

    icgl.run_cycle(adr, human_id="bakheet")

    print("\nKnowledge Base Snapshot:")
    print(f"ADRs: {len(kb.adrs)}")
    print(f"Human Decisions: {len(kb.human_decisions)}")
    print(f"Learning Logs: {len(kb.learning_log)}")

if __name__ == "__main__":
    run_demo()
