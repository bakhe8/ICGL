"""
Consensus AI — Sentinel Rules
==============================

Declarative rule definitions for Sentinel risk detection.

Usage:
    @sentinel_rule(category="Drift", severity="HIGH")
    def check_concept_drift(adr, kb):
        if concept_changed:
            return Alert("Concept drift detected")
        return None
"""

from typing import Callable, Optional, List, Literal
from dataclasses import dataclass, field
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertCategory(Enum):
    """Categories of Sentinel alerts."""
    DRIFT = "Drift"
    AUTHORITY = "Authority"
    COST = "Cost"
    SAFETY = "Safety"
    INTEGRITY = "Integrity"


@dataclass
class Alert:
    """
    A Sentinel alert indicating a detected risk.
    
    Alerts can be:
    - INFO: Informational, no action needed
    - WARNING: Requires attention, not blocking
    - CRITICAL: Blocks execution until resolved
    """
    message: str
    category: AlertCategory
    severity: AlertSeverity
    rule_id: str = ""
    context: dict = field(default_factory=dict)
    
    def __str__(self) -> str:
        icon = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.CRITICAL: "🚨"
        }.get(self.severity, "❓")
        return f"{icon} [{self.category.value}] {self.message}"


@dataclass
class SentinelRule:
    """A registered Sentinel rule."""
    id: str
    name: str
    description: str
    category: AlertCategory
    default_severity: AlertSeverity
    check_fn: Callable[..., Optional[Alert]]
    enabled: bool = True


class RuleRegistry:
    """
    Registry of Sentinel rules.
    
    Rules are predicate functions that check for risks
    and return Alert objects when risks are detected.
    """
    
    def __init__(self):
        self._rules: List[SentinelRule] = []
        self._register_default_rules()
    
    def register(
        self,
        id: str,
        name: str,
        description: str,
        category: AlertCategory,
        default_severity: AlertSeverity,
        check_fn: Callable[..., Optional[Alert]]
    ) -> None:
        """Registers a new Sentinel rule."""
        rule = SentinelRule(
            id=id,
            name=name,
            description=description,
            category=category,
            default_severity=default_severity,
            check_fn=check_fn
        )
        self._rules.append(rule)
    
    def _register_default_rules(self):
        """Registers built-in detection rules."""
        
        # S-01: No Related Policies
        self.register(
            id="S-01",
            name="Orphan ADR",
            description="ADR has no related policies (potential drift)",
            category=AlertCategory.DRIFT,
            default_severity=AlertSeverity.WARNING,
            check_fn=self._check_orphan_adr
        )
        
        # S-02: Concept Redefinition
        self.register(
            id="S-02",
            name="Concept Redefinition Attempt",
            description="ADR attempts to redefine an existing concept",
            category=AlertCategory.INTEGRITY,
            default_severity=AlertSeverity.CRITICAL,
            check_fn=self._check_concept_redefinition
        )
        
        # S-03: Authority Bypass
        self.register(
            id="S-03",
            name="Authority Bypass Attempt",
            description="Decision derived from context instead of authority",
            category=AlertCategory.AUTHORITY,
            default_severity=AlertSeverity.CRITICAL,
            check_fn=self._check_authority_bypass
        )
        
        # S-04: Missing Human Decision
        self.register(
            id="S-04",
            name="Missing Human Decision",
            description="ACCEPTED ADR without human signature",
            category=AlertCategory.AUTHORITY,
            default_severity=AlertSeverity.CRITICAL,
            check_fn=self._check_missing_human_decision
        )
        
        # S-05: Strategic Lock
        self.register(
            id="S-05",
            name="Strategic Option Lock",
            description="Decision may lock strategic optionality",
            category=AlertCategory.DRIFT,
            default_severity=AlertSeverity.WARNING,
            check_fn=self._check_strategic_lock
        )
        
        # S-06: Human Signature Bypass
        self.register(
            id="S-06",
            name="Governance Circumvention",
            description="Explicit attempt to bypass human signature or HDAL review",
            category=AlertCategory.AUTHORITY,
            default_severity=AlertSeverity.CRITICAL,
            check_fn=self._check_signature_bypass
        )
        
        # S-11: Semantic Drift (requires memory vector scan)
        self.register(
            id="S-11",
            name="Semantic Drift Detected",
            description="High similarity to existing accepted ADR indicating drift/duplication",
            category=AlertCategory.DRIFT,
            default_severity=AlertSeverity.WARNING,
            check_fn=self._check_semantic_drift_stub
        )
        
        # S-12: Intent Violation (LLM-based)
        self.register(
            id="S-12",
            name="Intent Violation",
            description="ADR intent may circumvent governance principles",
            category=AlertCategory.AUTHORITY,
            default_severity=AlertSeverity.WARNING,
            check_fn=self._check_intent_stub
        )
    
    def run_all(self, adr, kb) -> List[Alert]:
        """Runs all enabled rules and returns alerts."""
        alerts = []
        for rule in self._rules:
            if rule.enabled:
                alert = rule.check_fn(adr, kb)
                if alert:
                    alert.rule_id = rule.id
                    alerts.append(alert)
        return alerts
    
    def get_rule(self, rule_id: str) -> Optional[SentinelRule]:
        """Gets a rule by ID."""
        for rule in self._rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def enable_rule(self, rule_id: str) -> None:
        """Enables a rule by ID."""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = True
    
    def disable_rule(self, rule_id: str) -> None:
        """Disables a rule by ID."""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = False
    
    # =========================================================================
    # Built-in Rule Functions
    # =========================================================================
    
    def _check_orphan_adr(self, adr, kb) -> Optional[Alert]:
        """S-01: Check for ADRs without policy references."""
        if adr.status == "DRAFT" and not adr.related_policies:
            return Alert(
                message=f"ADR '{adr.title}' has no related policies",
                category=AlertCategory.DRIFT,
                severity=AlertSeverity.WARNING,
                context={"adr_id": adr.id}
            )
        return None
    
    def _check_concept_redefinition(self, adr, kb) -> Optional[Alert]:
        """S-02: Check for concept redefinition attempts."""
        # Check if ADR decision mentions redefining concepts
        keywords = ["redefine", "change meaning", "new definition", "تعريف جديد", "إعادة تعريف"]
        decision_lower = adr.decision.lower()
        
        for keyword in keywords:
            if keyword in decision_lower:
                return Alert(
                    message=f"ADR may redefine existing concepts",
                    category=AlertCategory.INTEGRITY,
                    severity=AlertSeverity.CRITICAL,
                    context={"adr_id": adr.id, "matched_keyword": keyword}
                )
        return None
    
    def _check_authority_bypass(self, adr, kb) -> Optional[Alert]:
        """S-03: Check for authority derivation from context."""
        bypass_patterns = ["context determines", "batch decides", "derived from context"]
        decision_lower = adr.decision.lower()
        
        for pattern in bypass_patterns:
            if pattern in decision_lower:
                return Alert(
                    message=f"ADR derives authority from context",
                    category=AlertCategory.AUTHORITY,
                    severity=AlertSeverity.CRITICAL,
                    context={"adr_id": adr.id, "matched_pattern": pattern}
                )
        return None
    
    def _check_missing_human_decision(self, adr, kb) -> Optional[Alert]:
        """S-04: Check for accepted ADRs without human signature."""
        if adr.status == "ACCEPTED" and not adr.human_decision_id:
            return Alert(
                message=f"ADR '{adr.title}' is ACCEPTED but has no human signature",
                category=AlertCategory.AUTHORITY,
                severity=AlertSeverity.CRITICAL,
                context={"adr_id": adr.id}
            )
        return None
    
    def _check_strategic_lock(self, adr, kb) -> Optional[Alert]:
        """
        S-05: Detect decisions that lock strategic optionality.
        Looks for irreversible/one-way language in context + decision.
        """
        text = (adr.context + " " + adr.decision).lower()
        lock_keywords = [
            "irreversible",
            "no rollback",
            "one-way",
            "only option",
            "cannot revert",
            "لا رجعة",
            "غير قابل للتراجع",
            "مسار وحيد"
        ]
        if any(kw in text for kw in lock_keywords):
            return Alert(
                message="Decision may lock strategic optionality",
                category=AlertCategory.DRIFT,
                severity=AlertSeverity.WARNING,
                context={"adr_id": adr.id, "matched": "strategic_lock"}
            )
        return None

    def _check_signature_bypass(self, adr, kb) -> Optional[Alert]:
        """S-06: Check for explicit bypass of human oversight."""
        bypass_keywords = [
            "bypass human", "skip signature", "auto-execute", "without review",
            "تجاوز التوقيع", "تخطي المراجعة", "تنفيذ تلقائي", "بدون مراجعة"
        ]
        text_to_check = (adr.context + " " + adr.decision).lower()
        
        for keyword in bypass_keywords:
            if keyword in text_to_check:
                return Alert(
                    message=f"Attempt to bypass human oversight detected (Pattern: {keyword})",
                    category=AlertCategory.AUTHORITY,
                    severity=AlertSeverity.CRITICAL,
                    context={"adr_id": adr.id, "matched_pattern": keyword}
                )
        return None

    def _check_semantic_drift_stub(self, adr, kb) -> Optional[Alert]:
        """
        S-11 stub: actual vector search is async in Sentinel.check_drift;
        here we return None to keep synchronous registry safe.
        """
        return None

    def _check_intent_stub(self, adr, kb) -> Optional[Alert]:
        """
        S-12 stub: actual LLM-based intent check is handled async in Sentinel.check_intent_async.
        """
        return None


# Global registry singleton
_registry = None

def get_registry() -> RuleRegistry:
    """Gets the global rule registry."""
    global _registry
    if _registry is None:
        _registry = RuleRegistry()
    return _registry


# Decorator for custom rules
def sentinel_rule(
    id: str,
    name: str,
    description: str = "",
    category: AlertCategory = AlertCategory.DRIFT,
    severity: AlertSeverity = AlertSeverity.WARNING
):
    """
    Decorator to register a function as a Sentinel rule.
    
    Usage:
        @sentinel_rule(id="S-CUSTOM-01", name="Custom Check")
        def my_check(adr, kb):
            if problem:
                return Alert("Problem found", AlertCategory.DRIFT, AlertSeverity.WARNING)
            return None
    """
    def decorator(fn: Callable[..., Optional[Alert]]):
        get_registry().register(
            id=id,
            name=name,
            description=description or fn.__doc__ or "",
            category=category,
            default_severity=severity,
            check_fn=fn
        )
        return fn
    return decorator
