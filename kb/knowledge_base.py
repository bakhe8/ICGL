"""
Consensus AI — Knowledge Base
==============================

The Knowledge Base is the canonical source of truth for all knowledge.
All entities are validated before registration using SchemaValidator.

See: docs/icgl_knowledge_base_v1.md
"""

from typing import Dict, List
from .schemas import (
    ID, Concept, Policy, SentinelSignal, ADR, HumanDecision, LearningLog, RoadmapItem,
    Procedure
)


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
    """

    def __init__(self, validate: bool = True):
        """
        Args:
            validate: If True, validates all entities before registration.
        """
        self._validate = validate
        self._validator = None
        if validate:
            from validator import SchemaValidator
            self._validator = SchemaValidator()
        
        self.concepts: Dict[ID, Concept] = {}
        self.policies: Dict[ID, Policy] = {}
        self.signals: Dict[ID, SentinelSignal] = {}
        self.adrs: Dict[ID, ADR] = {}
        self.human_decisions: Dict[ID, HumanDecision] = {}

        self.learning_log: List[LearningLog] = []
        self.roadmap_items: List[RoadmapItem] = []
        self.procedures: Dict[ID, Procedure] = {}
        
        # 🌱 Bootstrap with Seed Data
        self._bootstrap_seed_data()

    def _bootstrap_seed_data(self):
        """Loads the initial seed data from Knowledge Base v0."""
        # 🧠 Concept: Authority
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

    # ----------------------------
    # Registration APIs
    # ----------------------------

    def add_concept(self, concept: Concept):
        """Registers a new Concept (validated)."""
        if self._validator:
            self._validator.validate(concept)
        self.concepts[concept.id] = concept

    def add_policy(self, policy: Policy):
        """Registers a new Policy (validated)."""
        if self._validator:
            self._validator.validate(policy)
        self.policies[policy.id] = policy

    def add_signal(self, signal: SentinelSignal):
        """Registers a new Sentinel Signal (validated)."""
        if self._validator:
            self._validator.validate(signal)
        self.signals[signal.id] = signal

    def add_adr(self, adr: ADR):
        """Registers a new ADR (validated)."""
        if self._validator:
            self._validator.validate(adr)
        self.adrs[adr.id] = adr

    def add_human_decision(self, decision: HumanDecision):
        """Registers a Human Decision (validated)."""
        if self._validator:
            self._validator.validate(decision)
        self.human_decisions[decision.id] = decision

    def add_learning_log(self, log: LearningLog):
        """Appends a new Learning Log entry."""
        self.learning_log.append(log)

    def add_roadmap_item(self, item: RoadmapItem):
        """Registers a Roadmap Item (validated)."""
        # TODO: self._validator.validate(item) if needed
        self.roadmap_items.append(item)


    def add_procedure(self, procedure: Procedure):
        """Registers a new Procedure (validated)."""
        if self._validator:
            self._validator.validate(procedure)
        self.procedures[procedure.id] = procedure

    def get_stats(self) -> Dict[str, int]:
        """Returns statistical counts of the knowledge base."""
        return {
            "learning_logs": len(self.learning_log),
            "adrs": len(self.adrs),
            "human_decisions": len(self.human_decisions),
            "concepts": len(self.concepts),
            "policies": len(self.policies),
            "signals": len(self.signals)
        }

