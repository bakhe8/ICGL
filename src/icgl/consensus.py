"""
Consensus AI — Core Governance Foundation
==========================================

🏛️ **SYSTEM IDENTITY**
-----------------------
Consensus AI is not a chatbot, copilot, or automation tool.
It is a **Governed Reasoning System** that transforms complex decisions into 
auditable, traceable, and human-sovereign outcomes.

See: docs/manifesto.md for full philosophy.

🧭 **PHILOSOPHY** (from Manifesto)
----------------------------------
1. Intelligence without governance is dangerous.
2. The real enemy is silent drift.
3. Unknown risks must be contained, not eliminated.
4. Humans remain sovereign over meaning and authority.
5. Strategic optionality must be preserved.

🧩 **CORE ARCHITECTURE** (The Kernel)
-------------------------------------
This module implements the six foundational components:

1. **Knowledge Base**: Canonical source of truth.
   - Concepts, Policies, ADRs, Signals, Human Decisions, Learning Logs.
   
2. **ICGL (Iterative Co-Governance Loop)**: The evolution engine.
   - Every decision flows through governance before execution.
   
3. **Sentinel**: System immune layer.
   - Detects drift, unknown risks, violations, and instability.
   
4. **Concept Guardian** (TODO): Protects conceptual integrity.
   - Prevents implicit redefinition of meaning.
   
5. **HDAL (Human Decision Authority Layer)**: Final human authority.
   - All sovereign decisions must be signed by a human.
   
6. **Policies**: Hard constraints that cannot be overridden.

🔁 **LIFECYCLE** (How It Operates)
----------------------------------
1. Proposal submitted
2. ADR drafted
3. Policy gate enforced
4. Sentinel scanning
5. Agent analysis & synthesis
6. Human sovereign decision
7. Knowledge base update
8. Next iteration

📖 **REFERENCES**
-----------------
- README.md: System overview and quick start.
- docs/manifesto.md: Full identity, philosophy, and goals.
- docs/consensus_ai_knowledge_base_v_0.md: Canonical schemas and seed data.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from datetime import datetime, timezone
import uuid

# ==========================================================================
# 🔹 Core Types
# --------------------------------------------------------------------------
# These are the fundamental type aliases used throughout the system.
# ==========================================================================

ID = str  # Unique identifier for any entity
Timestamp = str  # ISO-8601 formatted timestamp

# Manifesto Reference: "Humans remain sovereign over meaning and authority"
# All decisions must have an explicit action taken by a human.
DecisionAction = Literal["APPROVE", "REJECT", "MODIFY", "EXPERIMENT"]


def now() -> Timestamp:
    """Returns the current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def uid() -> ID:
    """Generates a unique identifier (UUID v4)."""
    return str(uuid.uuid4())


# ==========================================================================
# 🧠 Knowledge Base Schemas (Canonical)
# --------------------------------------------------------------------------
# These dataclasses define the canonical structure of all knowledge entities.
# See: docs/consensus_ai_knowledge_base_v_0.md for the full schema spec.
# ==========================================================================

@dataclass
class Concept:
    """
    A Concept is a foundational definition that must remain stable.
    
    Manifesto Reference:
    - "Concept Guardian protects conceptual integrity."
    - "No concept may change without explicit human approval."
    
    Attributes:
        invariants: Rules that must ALWAYS hold for this concept.
        anti_patterns: Common mistakes to avoid when using this concept.
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
    
    Manifesto Reference:
    - "Policies are hard constraints that cannot be overridden by optimization or voting."
    
    Attributes:
        severity: LOW | MEDIUM | HIGH | CRITICAL
        enforced_by: Components responsible for enforcing this policy.
    """
    id: ID
    code: str  # e.g., "P-ARCH-04"
    title: str
    rule: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    enforced_by: List[str]  # e.g., ["Sentinel", "Orchestrator"]
    created_at: Timestamp = field(default_factory=now)


@dataclass
class SentinelSignal:
    """
    A Sentinel Signal represents a detectable risk or anomaly.
    
    Manifesto Reference:
    - "Sentinel: System immune layer. Detects drift, unknown risks, violations."
    
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
    
    Lifecycle Reference:
    1. Proposal → 2. ADR drafted → 3. Policy gate → 4. Sentinel → 5. Human decision
    
    Attributes:
        status: DRAFT | CONDITIONAL | ACCEPTED | REJECTED | EXPERIMENTAL
        consequences: Expected outcomes of this decision.
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
    
    Manifesto Reference:
    - "HDAL: All sovereign decisions must be signed by a human."
    - "No core rule may change without explicit human approval."
    
    Attributes:
        signature_hash: Placeholder for cryptographic signature (future: HSM).
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
    
    Manifesto Reference:
    - "Unknown risks cannot be eliminated — only contained and learned from."
    
    Attributes:
        cycle: The ICGL cycle number.
        summary: What was learned or decided in this cycle.
    """
    cycle: int
    summary: str
    new_policies: List[ID]
    new_signals: List[ID]
    new_concepts: List[ID]
    notes: str


# ==========================================================================
# 📚 In-Memory Knowledge Base (v0)
# --------------------------------------------------------------------------
# The Knowledge Base is the canonical source of truth for all knowledge.
# 
# Manifesto Reference:
# - "Knowledge Base: Concepts, Policies, Sentinel Signals, ADRs, Human Decisions."
# 
# TODO: Replace with persistent storage + validation layer.
# ==========================================================================

class KnowledgeBase:
    """
    Source of Truth for all canonical knowledge.
    
    This class manages:
    - Concepts (foundational definitions)
    - Policies (hard constraints)
    - Sentinel Signals (risk indicators)
    - ADRs (architectural decisions)
    - Human Decisions (sovereign signatures)
    - Learning Logs (evolution history)
    
    All entities are validated before registration using SchemaValidator.
    
    See: docs/consensus_ai_knowledge_base_v_0.md
    """

    def __init__(self, validate: bool = True):
        """
        Args:
            validate: If True, validates all entities before registration.
        """
        self._validate = validate
        self._validator = None
        if validate:
            from .validator import SchemaValidator
            self._validator = SchemaValidator()
        
        self.concepts: Dict[ID, Concept] = {}
        self.policies: Dict[ID, Policy] = {}
        self.signals: Dict[ID, SentinelSignal] = {}
        self.adrs: Dict[ID, ADR] = {}
        self.human_decisions: Dict[ID, HumanDecision] = {}
        self.learning_log: List[LearningLog] = []
        self.concepts: Dict[ID, Concept] = {}
        self.policies: Dict[ID, Policy] = {}
        self.signals: Dict[ID, SentinelSignal] = {}
        self.adrs: Dict[ID, ADR] = {}
        self.human_decisions: Dict[ID, HumanDecision] = {}
        self.learning_log: List[LearningLog] = []
        
        # 🌱 Bootstrap with Seed Data from Knowledge Base v0
        self._bootstrap_seed_data()

    def _bootstrap_seed_data(self):
        """
        Loads the initial seed data defined in the Knowledge Base v0.
        
        See: docs/consensus_ai_knowledge_base_v_0.md § "Seed Data — Concrete Instances"
        """
        # 🧠 Concept: Authority
        # Philosophy: "Humans remain sovereign over meaning and authority"
        self.add_concept(Concept(
            id="concept-authority",
            name="Authority",
            definition="الجهة الوحيدة المخولة باتخاذ أو تعديل قرار ضمن نطاق محدد، ولا يجوز تعددها أو تجاوزها أو استنتاجها ضمنيًا.",
            invariants=[
                "Single authority per domain",
                "No implicit authority derivation",
                "No bypass paths"
            ],
            anti_patterns=[
                "Multiple writers",
                "Hidden side effects",
                "Context-driven decisions"
            ],
            created_at="2026-01-16T00:00:00Z",
            updated_at="2026-01-16T00:00:00Z"
        ))

        # ⚖️ Policy: P-ARCH-04
        # Philosophy: "The real enemy is silent drift"
        self.add_policy(Policy(
            id="policy-context-not-authority",
            code="P-ARCH-04",
            title="Context Is Not Authority",
            rule="أي كيان سياقي (Context, Batch, Occurrence) لا يجوز استخدامه لاتخاذ قرار أو اشتقاق حالة أو تنفيذ إجراء.",
            severity="CRITICAL",
            enforced_by=["Sentinel", "Orchestrator"],
            created_at="2026-01-16T00:00:00Z"
        ))

        # 📜 ADR: ADR-001
        # Lifecycle: Proposal → ADR → Policy Gate → Sentinel → Human Decision
        self.add_adr(ADR(
            id="ADR-001",
            title="Batch as Context (Occurrence Model)",
            status="CONDITIONAL",
            context="النظام الحالي يربط الضمان بBatch واحد (Ownership) مما يمنع التتبع التاريخي وإعادة المعالجة متعددة السياقات.",
            decision="تحويل Batch إلى كيان سياقي فقط، وربط الضمان عبر Occurrence غير قابل للتعديل.",
            consequences=[
                "فصل الهوية عن السياق",
                "تحسين قابلية التتبع",
                "زيادة تعقيد الاستعلامات",
                "الحاجة لسياسات عزل صارمة"
            ],
            related_policies=["policy-context-not-authority"],
            sentinel_signals=["S-05", "S-08"],
            human_decision_id="human-decision-001",
            created_at="2026-01-16T00:00:00Z"
        ))

    def add_concept(self, concept: Concept):
        """Registers a new Concept in the Knowledge Base (validated)."""
        if self._validator:
            self._validator.validate(concept)
        self.concepts[concept.id] = concept

    def add_policy(self, policy: Policy):
        """Registers a new Policy in the Knowledge Base (validated)."""
        if self._validator:
            self._validator.validate(policy)
        self.policies[policy.id] = policy

    def add_signal(self, signal: SentinelSignal):
        """Registers a new Sentinel Signal in the Knowledge Base (validated)."""
        if self._validator:
            self._validator.validate(signal)
        self.signals[signal.id] = signal

    def add_adr(self, adr: ADR):
        """Registers a new ADR in the Knowledge Base (validated)."""
        if self._validator:
            self._validator.validate(adr)
        self.adrs[adr.id] = adr

    def add_human_decision(self, decision: HumanDecision):
        """Registers a Human Decision (sovereign signature, validated)."""
        if self._validator:
            self._validator.validate(decision)
        self.human_decisions[decision.id] = decision

    def add_learning_log(self, log: LearningLog):
        """Appends a new Learning Log entry."""
        self.learning_log.append(log)


# ==========================================================================
# 🛡️ Sentinel
# --------------------------------------------------------------------------
# The Sentinel is the system's immune layer.
# 
# Manifesto Reference:
# - "Sentinel: Detects drift, unknown risks, violations, and instability."
# - "Unknown risks cannot be eliminated — only contained and learned from."
# 
# TODO: Implement real detection logic (drift analysis, policy violation checks).
# ==========================================================================

class Sentinel:
    """
    System immune layer that detects anomalies, drift, and policy violations.
    
    Current implementation is a stub. Future versions will include:
    - Semantic drift detection
    - Policy boundary enforcement
    - Cost anomaly detection
    - Stability analysis
    """

    def scan_adr(self, adr: ADR, kb: KnowledgeBase) -> List[str]:
        """
        Scans an ADR for potential risks before human review.
        
        Returns:
            A list of alert messages (empty if no issues found).
        """
        alerts: List[str] = []

        # Philosophy: "The real enemy is silent drift"
        # Rule: All ADRs should reference at least one policy.
        if adr.status == "DRAFT" and not adr.related_policies:
            alerts.append("⚠️ ADR has no related policies (potential drift risk)")

        return alerts


# ==========================================================================
# 🏛️ Human Decision Authority Layer (HDAL)
# --------------------------------------------------------------------------
# The HDAL ensures that ALL sovereign decisions are signed by a human.
# 
# Manifesto Reference:
# - "HDAL: Final human authority. All sovereign decisions must be signed."
# - "No concept, policy, or core rule may change without explicit human approval."
# 
# TODO: Replace placeholder signature with cryptographic proof (HSM/PKI).
# ==========================================================================

class HDAL:
    """
    Human Decision Authority Layer.
    
    This component ensures:
    - All critical decisions require human approval.
    - Every approval is signed and traceable.
    - The human remains the final authority.
    """

    def sign_decision(
        self,
        adr_id: ID,
        action: DecisionAction,
        rationale: str,
        human_id: str,
    ) -> HumanDecision:
        """
        Creates a signed Human Decision for an ADR.
        
        Args:
            adr_id: The ID of the ADR being decided.
            action: APPROVE, REJECT, MODIFY, or EXPERIMENT.
            rationale: Human-provided reasoning.
            human_id: Identifier of the signing human.
        
        Returns:
            A HumanDecision record with a signature hash.
        """
        # Placeholder signature (TODO: replace with crypto/HSM)
        signature = f"signed-by:{human_id}:{adr_id}:{now()}"

        return HumanDecision(
            id=uid(),
            adr_id=adr_id,
            action=action,
            rationale=rationale,
            signed_by=human_id,
            signature_hash=signature,
        )


# ==========================================================================
# 🔁 ICGL — Iterative Co-Governance Loop
# --------------------------------------------------------------------------
# The ICGL is the evolution engine of Consensus AI.
# 
# Manifesto Reference:
# - "ICGL: Every important decision flows through governance before execution."
# 
# Lifecycle:
# 1. Proposal submitted
# 2. ADR drafted
# 3. Policy gate enforced
# 4. Sentinel scanning
# 5. Agent analysis & synthesis
# 6. Human sovereign decision
# 7. Knowledge base update
# 8. Next iteration
# ==========================================================================

class ICGL:
    """
    ICGL: Iterative Co-Governance Loop.
    
    Orchestrates a single governance cycle:
    ADR Registration → Sentinel Scan → Human Decision → Learning Log
    """

    def __init__(self, kb: KnowledgeBase, sentinel: Sentinel, hdal: HDAL):
        self.kb = kb
        self.sentinel = sentinel
        self.hdal = hdal

    def run_cycle(self, adr: ADR, human_id: str):
        """
        Executes one complete ICGL governance cycle.
        
        Args:
            adr: The Architectural Decision Record to process.
            human_id: The human who will sign the decision.
        """
        print(f"[ICGL] 🔁 Starting governance cycle for: {adr.title}")

        # Step 2: ADR drafted (already done by caller)
        # Step 3: Register ADR in Knowledge Base
        self.kb.add_adr(adr)

        # Step 4: Sentinel scanning
        alerts = self.sentinel.scan_adr(adr, self.kb)
        if alerts:
            print("[Sentinel] 🛡️ Alerts detected:")
            for alert in alerts:
                print(f"   - {alert}")

        # Step 6: Human sovereign decision
        decision = self.hdal.sign_decision(
            adr_id=adr.id,
            action="APPROVE",
            rationale="Bootstrap approval",
            human_id=human_id,
        )

        # Step 7: Knowledge base update
        self.kb.add_human_decision(decision)
        adr.human_decision_id = decision.id

        self.kb.add_learning_log(
            LearningLog(
                cycle=len(self.kb.learning_log) + 1,
                summary=f"Processed ADR {adr.id}: {adr.title}",
                new_policies=[],
                new_signals=[],
                new_concepts=[],
                notes="Bootstrap cycle",
            )
        )

        print(f"[ICGL] ✅ Cycle completed. Decision: {decision.action}")


# ==========================================================================
# 🚀 Demo Bootstrap
# --------------------------------------------------------------------------
# This function demonstrates a complete ICGL cycle.
# Run via CLI: `autobeto consensus --human your_name`
# ==========================================================================

def run_demo():
    """
    Demonstrates the ICGL cycle with a sample ADR.
    
    Usage:
        python -m autobeto.consensus
        # or via CLI:
        autobeto consensus --human bakheet
    """
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
        related_policies=[],  # Intentionally empty to trigger Sentinel alert
        sentinel_signals=[],
        human_decision_id=None,
    )

    icgl.run_cycle(adr, human_id="bakheet")

    print("\n📚 Knowledge Base Snapshot:")
    print(f"   Concepts: {len(kb.concepts)}")
    print(f"   Policies: {len(kb.policies)}")
    print(f"   ADRs: {len(kb.adrs)}")
    print(f"   Human Decisions: {len(kb.human_decisions)}")
    print(f"   Learning Logs: {len(kb.learning_log)}")


if __name__ == "__main__":
    run_demo()
