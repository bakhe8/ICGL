"""
Consensus AI — Schema Validator
================================

🛡️ **PURPOSE**
---------------
This module provides validation logic for all Knowledge Base entities,
ensuring data integrity before registration.

Manifesto Reference:
- "Policies are hard constraints that cannot be overridden."
- "Sentinel: Detects drift, unknown risks, violations."

📖 **VALIDATION RULES**
-----------------------
Each entity type has specific validation rules:
- **Concept**: Must have id, name, definition, at least one invariant.
- **Policy**: Must have code matching pattern P-XXX-NN, valid severity.
- **ADR**: Must have valid status, non-empty context and decision.
- **SentinelSignal**: Must have valid category and default_action.
- **HumanDecision**: Must have valid action, non-empty rationale, signed_by.

🚨 **VALIDATION ERRORS**
------------------------
ValidationError is raised when data fails to meet requirements.
All errors include the field name and a descriptive message.
"""

from typing import List, Any
import re


# ==========================================================================
# 🚨 Validation Exceptions
# ==========================================================================

class ValidationError(Exception):
    """
    Raised when an entity fails validation.
    
    Attributes:
        entity_type: The type of entity that failed (e.g., "Concept").
        field: The field that failed validation.
        message: A human-readable error message.
    """
    def __init__(self, entity_type: str, field: str, message: str):
        self.entity_type = entity_type
        self.field = field
        self.message = message
        super().__init__(f"[{entity_type}] Validation failed for '{field}': {message}")


class MultiValidationError(Exception):
    """
    Raised when multiple validation errors occur.
    """
    def __init__(self, errors: List[ValidationError]):
        self.errors = errors
        messages = "\n".join([str(e) for e in errors])
        super().__init__(f"Multiple validation errors:\n{messages}")


# ==========================================================================
# 🔍 Validation Rules
# ==========================================================================

def validate_required(value: Any, entity_type: str, field: str) -> None:
    """Validates that a field is not None or empty."""
    if value is None:
        raise ValidationError(entity_type, field, "Field is required")
    if isinstance(value, str) and not value.strip():
        raise ValidationError(entity_type, field, "Field cannot be empty")
    if isinstance(value, list) and len(value) == 0:
        raise ValidationError(entity_type, field, "List cannot be empty")


def validate_pattern(value: str, pattern: str, entity_type: str, field: str) -> None:
    """Validates that a string matches a regex pattern."""
    if not re.match(pattern, value):
        raise ValidationError(entity_type, field, f"Must match pattern: {pattern}")


def validate_in_set(value: Any, allowed: set, entity_type: str, field: str) -> None:
    """Validates that a value is in a set of allowed values."""
    if value not in allowed:
        raise ValidationError(entity_type, field, f"Must be one of: {allowed}")


def validate_list_not_empty(value: List, entity_type: str, field: str) -> None:
    """Validates that a list has at least one element."""
    if not value or len(value) == 0:
        raise ValidationError(entity_type, field, "List must have at least one element")


def validate_id_format(value: str, entity_type: str, field: str = "id") -> None:
    """Validates that an ID is non-empty and contains no spaces."""
    validate_required(value, entity_type, field)
    if " " in value:
        raise ValidationError(entity_type, field, "ID cannot contain spaces")


# ==========================================================================
# 🧠 Entity Validators
# ==========================================================================

def validate_concept(concept) -> List[ValidationError]:
    """
    Validates a Concept entity.
    
    Rules:
    - id: Required, no spaces.
    - name: Required.
    - definition: Required.
    - invariants: At least one required.
    - owner: Must be "HUMAN".
    """
    errors: List[ValidationError] = []
    entity_type = "Concept"
    
    try:
        validate_id_format(concept.id, entity_type)
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(concept.name, entity_type, "name")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(concept.definition, entity_type, "definition")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_list_not_empty(concept.invariants, entity_type, "invariants")
    except ValidationError as e:
        errors.append(e)
    
    if concept.owner != "HUMAN":
        errors.append(ValidationError(entity_type, "owner", "Concept owner must be 'HUMAN'"))
    
    return errors


def validate_policy(policy) -> List[ValidationError]:
    """
    Validates a Policy entity.
    
    Rules:
    - id: Required, no spaces.
    - code: Must match pattern P-[A-Z]+-[0-9]+ (e.g., P-ARCH-04).
    - title: Required.
    - rule: Required.
    - severity: Must be LOW, MEDIUM, HIGH, or CRITICAL.
    - enforced_by: At least one enforcer required.
    """
    errors: List[ValidationError] = []
    entity_type = "Policy"
    
    try:
        validate_id_format(policy.id, entity_type)
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_pattern(policy.code, r"^P-[A-Z]+-\d+$", entity_type, "code")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(policy.title, entity_type, "title")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(policy.rule, entity_type, "rule")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_in_set(policy.severity, {"LOW", "MEDIUM", "HIGH", "CRITICAL"}, entity_type, "severity")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_list_not_empty(policy.enforced_by, entity_type, "enforced_by")
    except ValidationError as e:
        errors.append(e)
    
    return errors


def validate_adr(adr) -> List[ValidationError]:
    """
    Validates an ADR entity.
    
    Rules:
    - id: Required, no spaces.
    - title: Required.
    - status: Must be DRAFT, CONDITIONAL, ACCEPTED, REJECTED, or EXPERIMENTAL.
    - context: Required.
    - decision: Required.
    """
    errors: List[ValidationError] = []
    entity_type = "ADR"
    
    try:
        validate_id_format(adr.id, entity_type)
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(adr.title, entity_type, "title")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_in_set(adr.status, {"DRAFT", "CONDITIONAL", "ACCEPTED", "REJECTED", "EXPERIMENTAL"}, entity_type, "status")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(adr.context, entity_type, "context")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(adr.decision, entity_type, "decision")
    except ValidationError as e:
        errors.append(e)
    
    return errors


def validate_sentinel_signal(signal) -> List[ValidationError]:
    """
    Validates a SentinelSignal entity.
    
    Rules:
    - id: Required, no spaces.
    - name: Required.
    - description: Required.
    - category: Must be Drift, Authority, Cost, Safety, or Integrity.
    - default_action: Must be ALLOW, CONTAIN, or ESCALATE.
    """
    errors: List[ValidationError] = []
    entity_type = "SentinelSignal"
    
    try:
        validate_id_format(signal.id, entity_type)
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(signal.name, entity_type, "name")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(signal.description, entity_type, "description")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_in_set(signal.category, {"Drift", "Authority", "Cost", "Safety", "Integrity"}, entity_type, "category")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_in_set(signal.default_action, {"ALLOW", "CONTAIN", "ESCALATE"}, entity_type, "default_action")
    except ValidationError as e:
        errors.append(e)
    
    return errors


def validate_human_decision(decision) -> List[ValidationError]:
    """
    Validates a HumanDecision entity.
    
    Rules:
    - id: Required, no spaces.
    - adr_id: Required.
    - action: Must be APPROVE, REJECT, MODIFY, or EXPERIMENT.
    - rationale: Required.
    - signed_by: Required.
    - signature_hash: Required.
    """
    errors: List[ValidationError] = []
    entity_type = "HumanDecision"
    
    try:
        validate_id_format(decision.id, entity_type)
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(decision.adr_id, entity_type, "adr_id")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_in_set(decision.action, {"APPROVE", "REJECT", "MODIFY", "EXPERIMENT"}, entity_type, "action")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(decision.rationale, entity_type, "rationale")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(decision.signed_by, entity_type, "signed_by")
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_required(decision.signature_hash, entity_type, "signature_hash")
    except ValidationError as e:
        errors.append(e)
    
    return errors


# ==========================================================================
# 🔒 Validator Class
# ==========================================================================

class SchemaValidator:
    """
    Central validator for all Knowledge Base entities.
    
    Usage:
        validator = SchemaValidator()
        validator.validate(concept)  # Raises if invalid
        
        # Or check without raising:
        errors = validator.validate(concept, raise_on_error=False)
    """
    
    def __init__(self, strict: bool = True):
        """
        Args:
            strict: If True, raises MultiValidationError on any errors.
        """
        self.strict = strict
    
    def validate(self, entity, raise_on_error: bool = True) -> List[ValidationError]:
        """
        Validates an entity based on its type.
        
        Args:
            entity: The entity to validate.
            raise_on_error: If True, raises on validation failure.
        
        Returns:
            List of ValidationError (empty if valid).
        
        Raises:
            MultiValidationError: If validation fails and raise_on_error is True.
        """
        entity_type = type(entity).__name__
        
        validators = {
            "Concept": validate_concept,
            "Policy": validate_policy,
            "ADR": validate_adr,
            "SentinelSignal": validate_sentinel_signal,
            "HumanDecision": validate_human_decision,
        }
        
        validator_fn = validators.get(entity_type)
        if not validator_fn:
            raise ValueError(f"No validator found for entity type: {entity_type}")
        
        errors = validator_fn(entity)
        
        if errors and raise_on_error:
            raise MultiValidationError(errors)
        
        return errors
    
    def is_valid(self, entity) -> bool:
        """Returns True if the entity is valid."""
        errors = self.validate(entity, raise_on_error=False)
        return len(errors) == 0
