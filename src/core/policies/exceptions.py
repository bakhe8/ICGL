"""
Consensus AI — Policy Enforcement Exceptions
=============================================

Custom exceptions for policy violations.

Manifesto Reference:
- "Policies are hard constraints that cannot be overridden by optimization or voting."
"""


class PolicyViolationError(Exception):
    """
    Raised when a hard policy constraint is violated.
    
    This is a non-recoverable error that must be handled
    by escalating to human review.
    """
    
    def __init__(self, policy_code: str, message: str, severity: str = "LOW", context: dict = None):
        self.policy_code = policy_code
        self.message = message
        self.severity = severity
        self.context = context or {}
        super().__init__(f"[{policy_code}] ({severity}) Policy Violation: {message}")


class AuthorityViolationError(PolicyViolationError):
    """
    Raised when an entity attempts to claim authority it doesn't have.
    
    Reference: P-ARCH-04 (Context Is Not Authority)
    """
    
    def __init__(self, entity_type: str, attempted_action: str):
        super().__init__(
            policy_code="P-ARCH-04",
            message=f"{entity_type} cannot perform '{attempted_action}' - context is not authority",
            severity="CRITICAL",
            context={"entity_type": entity_type, "attempted_action": attempted_action}
        )


class ImmutabilityViolationError(PolicyViolationError):
    """
    Raised when an attempt is made to modify an immutable entity.
    
    Reference: P-ARCH-05 (Occurrence Must Be Immutable)
    """
    
    def __init__(self, entity_id: str, field: str):
        super().__init__(
            policy_code="P-ARCH-05",
            message=f"Cannot modify immutable entity '{entity_id}' field '{field}'",
            severity="CRITICAL",
            context={"entity_id": entity_id, "field": field}
        )


class ConceptModificationError(PolicyViolationError):
    """
    Raised when a concept modification is attempted without human approval.
    
    Reference: P-GOV-09 (Human Exclusive Concept Authority)
    """
    
    def __init__(self, concept_id: str, modifier: str):
        super().__init__(
            policy_code="P-GOV-09",
            message=f"Concept '{concept_id}' cannot be modified by '{modifier}' without HDAL approval",
            severity="HIGH",
            context={"concept_id": concept_id, "modifier": modifier}
        )


class StrategicOptionViolationError(PolicyViolationError):
    """
    Raised when a decision would lock strategic optionality.
    
    Reference: P-CORE-01 (Strategic Optionality Preservation)
    """
    
    def __init__(self, decision: str, locked_options: list):
        super().__init__(
            policy_code="P-CORE-01",
            message=f"Decision '{decision}' would lock the following options: {locked_options}",
            severity="HIGH",
            context={"decision": decision, "locked_options": locked_options}
        )
