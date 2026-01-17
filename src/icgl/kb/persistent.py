"""
Consensus AI — Persistent Knowledge Base
=========================================

Knowledge Base with SQLite persistence support.

Usage:
    from icgl.kb import PersistentKnowledgeBase
    
    kb = PersistentKnowledgeBase("data/kb.db")
    kb.add_concept(concept)  # Auto-persisted
"""

from typing import Dict, List, Optional
from .schemas import (
    ID, Concept, Policy, SentinelSignal, ADR, HumanDecision, LearningLog, RoadmapItem
)
from .storage import StorageBackend


class PersistentKnowledgeBase:
    """
    Knowledge Base with automatic SQLite persistence.
    
    All mutations are automatically persisted to the database.
    Data is loaded from the database on initialization.
    """
    
    def __init__(
        self, 
        db_path: str = "data/kb.db",
        validate: bool = True,
        bootstrap: bool = True
    ):
        """
        Args:
            db_path: Path to SQLite database file.
            validate: If True, validates entities before registration.
            bootstrap: If True, loads seed data on first run.
        """
        self._storage = StorageBackend(db_path)
        self._validate = validate
        self._validator = None
        
        if validate:
            from ..validator import SchemaValidator
            self._validator = SchemaValidator()
        
        # Load existing data from storage
        self.concepts: Dict[ID, Concept] = self._storage.load_all_concepts()
        self.policies: Dict[ID, Policy] = self._storage.load_all_policies()
        self.signals: Dict[ID, SentinelSignal] = self._storage.load_all_signals()
        self.adrs: Dict[ID, ADR] = self._storage.load_all_adrs()
        self.human_decisions: Dict[ID, HumanDecision] = self._storage.load_all_human_decisions()
        self.learning_log: List[LearningLog] = self._storage.load_all_learning_logs()
        self.roadmap_items: List[RoadmapItem] = self._storage.load_all_roadmap_items()
        
        # Bootstrap if empty
        if bootstrap and not self.concepts:
            self._bootstrap_seed_data()
    
    def _bootstrap_seed_data(self):
        """Loads initial seed data from Knowledge Base v0 + v2."""
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
        
        # 🧠 Concept: Context
        self.add_concept(Concept(
            id="concept-context",
            name="Context",
            definition="إطار وصفي لعرض أو تجميع الكيانات دون امتلاك أي سلطة تقريرية أو حالة تشغيلية.",
            invariants=[
                "Read-only in operational logic",
                "No authority derivation",
                "No state mutation"
            ],
            anti_patterns=[
                "Using context to drive decisions",
                "Embedding business rules inside context",
                "Implicit coupling with domain entities"
            ],
            created_at="2026-01-16T00:00:00Z",
            updated_at="2026-01-16T00:00:00Z"
        ))
        
        # 🧠 Concept: Occurrence
        self.add_concept(Concept(
            id="concept-occurrence",
            name="Occurrence",
            definition="سجل غير قابل للتعديل يعبّر عن ظهور كيان داخل سياق معين دون أي معنى تشغيلي أو سلطوي.",
            invariants=[
                "Immutable once created",
                "Uniqueness per (entity, context, logical_scope)",
                "Observable only"
            ],
            anti_patterns=[
                "Using occurrence as a state source",
                "Deriving business rules from occurrence",
                "Allowing updates or overwrites"
            ],
            created_at="2026-01-16T00:00:00Z",
            updated_at="2026-01-16T00:00:00Z"
        ))
        
        # 🧠 Concept: Policy
        self.add_concept(Concept(
            id="concept-policy",
            name="Policy",
            definition="قيد جامد غير قابل للتفاوض يحدد ما هو المسموح والممنوع بغض النظر عن نتائج التحسين أو التصويت.",
            invariants=[
                "Evaluated before any optimization",
                "Cannot be overridden by agents",
                "Violation triggers containment"
            ],
            anti_patterns=[
                "Treating policy as recommendation",
                "Softening constraints for convenience",
                "Implicit exceptions"
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
        
        # ⚖️ Policy: P-ARCH-05
        self.add_policy(Policy(
            id="policy-occurrence-immutable",
            code="P-ARCH-05",
            title="Occurrence Must Be Immutable",
            rule="أي سجل Occurrence لا يجوز تعديله أو إعادة كتابته بعد إنشائه، وأي محاولة تعديل تعتبر خرقًا معماريًا حرجًا.",
            severity="CRITICAL",
            enforced_by=["Sentinel", "Orchestrator"],
            created_at="2026-01-16T00:00:00Z"
        ))
        
        # ⚖️ Policy: P-GOV-09
        self.add_policy(Policy(
            id="policy-human-concept-authority",
            code="P-GOV-09",
            title="Human Exclusive Concept Authority",
            rule="لا يجوز تعديل أو إعادة تعريف أي مفهوم أساسي إلا بقرار بشري موثق عبر HDAL.",
            severity="CRITICAL",
            enforced_by=["Sentinel", "HDAL"],
            created_at="2026-01-16T00:00:00Z"
        ))
        
        # ⚖️ Policy: P-CORE-01
        self.add_policy(Policy(
            id="policy-strategic-optionality",
            code="P-CORE-01",
            title="Strategic Optionality Preservation",
            rule="أي قرار معماري يجب ألا يقيد إمكانية توجيه النظام مستقبلًا إلى استخدامات متعددة دون إعادة بناء جوهري.",
            severity="HIGH",
            enforced_by=["Sentinel", "HumanReview"],
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
        
        # 📜 ADR: ADR-002
        self.add_adr(ADR(
            id="ADR-002",
            title="Single Authority Governance Model",
            status="EXPERIMENTAL",
            context="تعدد مصادر القرار والحالة يؤدي إلى تناقضات وأحداث مفقودة وصعوبة في التدقيق.",
            decision="تحديد سلطة واحدة صريحة لكل مفهوم: Decision, Status, Action, Lock.",
            consequences=[
                "وضوح منطقي أعلى",
                "تقليل التناقضات",
                "زيادة الصرامة المعمارية",
                "حاجة لإعادة هيكلة بعض المسارات"
            ],
            related_policies=[
                "policy-context-not-authority",
                "policy-human-concept-authority"
            ],
            sentinel_signals=["S-05", "S-07"],
            human_decision_id="human-decision-002",
            created_at="2026-01-16T00:00:00Z"
        ))
    
    # =========================================================================
    # Registration APIs (with auto-persistence)
    # =========================================================================
    
    def add_concept(self, concept: Concept) -> None:
        """Registers and persists a concept."""
        if self._validator:
            self._validator.validate(concept)
        self.concepts[concept.id] = concept
        self._storage.save_concept(concept)
    
    def add_policy(self, policy: Policy) -> None:
        """Registers and persists a policy."""
        if self._validator:
            self._validator.validate(policy)
        self.policies[policy.id] = policy
        self._storage.save_policy(policy)
    
    def add_signal(self, signal: SentinelSignal) -> None:
        """Registers and persists a sentinel signal."""
        if self._validator:
            self._validator.validate(signal)
        self.signals[signal.id] = signal
        self._storage.save_signal(signal)
    
    def add_adr(self, adr: ADR) -> None:
        """Registers and persists an ADR."""
        if self._validator:
            self._validator.validate(adr)
        self.adrs[adr.id] = adr
        self._storage.save_adr(adr)
    
    def add_human_decision(self, decision: HumanDecision) -> None:
        """Registers and persists a human decision."""
        if self._validator:
            self._validator.validate(decision)
        self.human_decisions[decision.id] = decision
        self._storage.save_human_decision(decision)

    def remove_adr(self, adr_id: ID) -> bool:
        """Removes an ADR and associated human decisions."""
        if adr_id not in self.adrs:
            return False
        self._storage.delete_adr(adr_id)
        # Update in-memory state
        del self.adrs[adr_id]
        self.human_decisions = {
            key: val for key, val in self.human_decisions.items()
            if val.adr_id != adr_id
        }
        return True
    
    def add_learning_log(self, log: LearningLog) -> None:
        """Appends and persists a learning log entry."""
        self.learning_log.append(log)
        self._storage.save_learning_log(log)

    def add_roadmap_item(self, item: RoadmapItem) -> None:
        """Registers and persists a roadmap item."""
        if self._validator:
            # TODO: Add validator for RoadmapItem
            pass
        self.roadmap_items.append(item)
        self._storage.save_roadmap_item(item)
    
    # =========================================================================
    # Query APIs
    # =========================================================================
    
    def get_concept(self, concept_id: ID) -> Optional[Concept]:
        """Gets a concept by ID."""
        return self.concepts.get(concept_id)
    
    def get_policy(self, policy_id: ID) -> Optional[Policy]:
        """Gets a policy by ID."""
        return self.policies.get(policy_id)
    
    def get_policy_by_code(self, code: str) -> Optional[Policy]:
        """Gets a policy by code (e.g., 'P-ARCH-04')."""
        for policy in self.policies.values():
            if policy.code == code:
                return policy
        return None
    
    def get_adr(self, adr_id: ID) -> Optional[ADR]:
        """Gets an ADR by ID."""
        return self.adrs.get(adr_id)
    
    def get_stats(self) -> Dict[str, int]:
        """Returns counts for all entity types."""
        return {
            "concepts": len(self.concepts),
            "policies": len(self.policies),
            "signals": len(self.signals),
            "adrs": len(self.adrs),
            "human_decisions": len(self.human_decisions),
            "learning_logs": len(self.learning_log),
        }
