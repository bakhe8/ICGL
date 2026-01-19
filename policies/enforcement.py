"""
Consensus AI — Policy Enforcement Layer
========================================

Pre-execution policy checks that prevent violations before they occur.

Manifesto Reference:
- "Policies are hard constraints that cannot be overridden."
- "Violation triggers containment."

Usage:
    enforcer = PolicyEnforcer(kb)
    report = enforcer.check_adr_compliance(adr)
"""

from typing import List, Optional, Callable, Dict
from dataclasses import dataclass, field

from kb.schemas import ADR, Concept, Policy, HumanDecision
from policies.exceptions import (
    PolicyViolationError,
    AuthorityViolationError,
    ImmutabilityViolationError,
    ConceptModificationError,
)

@dataclass
class PolicyReport:
    """Structured report of policy enforcement results."""
    passed_policies: List[str] = field(default_factory=list)
    violated_policies: List[Dict[str, str]] = field(default_factory=list)
    status: str = "PASS" # PASS, WARN, ESCALATE, FAIL
    max_severity: str = "LOW"

@dataclass
class PolicyCheck:
    """A registered policy check."""
    policy_code: str
    description: str
    check_fn: Callable[..., Optional[PolicyViolationError]]


class PolicyEnforcer:
    """
    Enforces policy constraints before operations are executed.
    
    This is a pre-execution gate that prevents policy violations
    by checking proposed actions against registered policies.
    """
    
    def __init__(self, kb=None):
        """
        Args:
            kb: Knowledge Base instance for policy lookups.
        """
        self.kb = kb
        self._checks: List[PolicyCheck] = []
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Registers built-in policy checks."""
        
        # P-ARCH-04: Context Is Not Authority
        self.register_check(
            policy_code="P-ARCH-04",
            description="Prevent context entities from driving decisions",
            check_fn=self._check_context_not_authority
        )
        
        # P-ARCH-05: Occurrence Immutability
        self.register_check(
            policy_code="P-ARCH-05",
            description="Prevent modification of immutable records",
            check_fn=self._check_immutability
        )
        
        # P-GOV-09: Human Concept Authority
        self.register_check(
            policy_code="P-GOV-09",
            description="Require human approval for concept changes",
            check_fn=self._check_concept_authority
        )
    
    def register_check(
        self,
        policy_code: str,
        description: str,
        check_fn: Callable[..., Optional[PolicyViolationError]]
    ) -> None:
        """Registers a new policy check."""
        self._checks.append(PolicyCheck(
            policy_code=policy_code,
            description=description,
            check_fn=check_fn
        ))
    
    def check_adr_compliance(self, adr: ADR) -> PolicyReport:
        """
        Runs all relevant policy checks and returns a detailed report.
        """
        report = PolicyReport()
        severity_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        max_sev_val = 0

        # Run checks specifically relevant to ADR creation
        # In a real engine, we'd filter _checks by 'trigger'
        
        # For this implementation, we map manual checks to the standard logic
        checks_to_run = [
            self._check_p_arch_04_context_authority_adr,
            self._check_p_arch_05_occurrence_immutable_adr,
            self._check_p_gov_09_human_concept_authority_adr,
            self._check_p_core_01_optional_lock
        ]

        for check in checks_to_run:
            try:
                policy_id = check(adr)
                if policy_id:
                    report.passed_policies.append(policy_id)
            except PolicyViolationError as e:
                report.violated_policies.append({
                    "code": e.policy_code,
                    "severity": e.severity,
                    "message": str(e)
                })
                # Update Max Severity
                sev_val = severity_rank.get(e.severity, 1)
                if sev_val > max_sev_val:
                    max_sev_val = sev_val
                    report.max_severity = e.severity

        # Determine Final Decision
        if max_sev_val >= 4: # CRITICAL
            report.status = "FAIL"
        elif max_sev_val == 3: # HIGH
            report.status = "ESCALATE"
        elif len(report.violated_policies) > 0:
            report.status = "WARN"
        else:
            report.status = "PASS"

        return report

    def check_adr_creation(self, adr: ADR) -> None:
        """
        Legacy wrapper: raises exception on first Critical violation.
        Kept for backward compatibility if needed.
        """
        report = self.check_adr_compliance(adr)
        if report.status == "FAIL":
            # Re-raise the first critical violation
            for v in report.violated_policies:
                if v['severity'] == "CRITICAL":
                    raise PolicyViolationError(
                        policy_code=v['code'],
                        message=v['message'],
                        severity="CRITICAL"
                    )

    # =========================================================================
    # ADR Specific Checks (Helpers for check_adr_compliance)
    # =========================================================================

    def _check_p_arch_04_context_authority_adr(self, adr: ADR):
        """P-ARCH-04 check for ADR content."""
        keywords = ["decide based on context", "context implies", "derive from batch"]
        context_lower = adr.decision.lower()
        if any(kw in context_lower for kw in keywords):
             raise PolicyViolationError(
                policy_code="P-ARCH-04",
                message="ADR attempts to use Context for decision authority",
                severity="CRITICAL"
            )
        return "P-ARCH-04"

    def _check_p_arch_05_occurrence_immutable_adr(self, adr: ADR):
        """P-ARCH-05 check for ADR content."""
        if "modify occurrence" in adr.decision.lower() or "update occurrence" in adr.decision.lower():
             raise PolicyViolationError(
                policy_code="P-ARCH-05",
                message="ADR attempts to modify an Occurrence (Immutable)",
                severity="CRITICAL"
            )
        return "P-ARCH-05"

    def _check_p_gov_09_human_concept_authority_adr(self, adr: ADR):
        """P-GOV-09 check for ADR content."""
        if "redefine" in adr.decision.lower() and "concept" in adr.decision.lower():
            if not adr.human_decision_id: 
                 raise PolicyViolationError(
                    policy_code="P-GOV-09",
                    message="Attempt to redefine Concept without explicit Human Sovereignty",
                    severity="HIGH"
                )
        return "P-GOV-09"

    def _check_p_core_01_optional_lock(self, adr: ADR):
        """P-CORE-01: Prevent locking future options."""
        lock_keywords = ["irreversible", "only option", "cannot revert", "one-way", "لا رجعة"]
        text = (adr.context + " " + adr.decision).lower()
        if any(kw in text for kw in lock_keywords):
            raise PolicyViolationError(
                policy_code="P-CORE-01",
                message="ADR may lock strategic optionality",
                severity="HIGH"
            )
        return "P-CORE-01"

    # =========================================================================
    # Generic Action Checks (Used by enforce_all)
    # =========================================================================
    
    def _check_context_not_authority(self, action: str, **context) -> Optional[PolicyViolationError]:
        if context.get("authority_source") in ["context", "batch", "occurrence"]:
            return AuthorityViolationError(
                entity_type=context.get("authority_source", "unknown"),
                attempted_action=action
            )
        return None
    
    def _check_immutability(self, action: str, **context) -> Optional[PolicyViolationError]:
        if action == "modify_occurrence":
            return ImmutabilityViolationError(
                entity_id=context.get("entity_id", "unknown"),
                field=context.get("field", "unknown")
            )
        return None
    
    def _check_concept_authority(self, action: str, **context) -> Optional[PolicyViolationError]:
        if action == "modify_concept" and not context.get("has_hdal_approval"):
            return ConceptModificationError(
                concept_id=context.get("concept_id", "unknown"),
                modifier=context.get("modifier", "unknown")
            )
        return None
