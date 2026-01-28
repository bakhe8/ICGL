"""
Minimal schema validator shim.

This provides a lightweight `SchemaValidator` class used by the knowledge
base components. It intentionally performs no strict validation in dev
environments to allow booting; implement stronger checks later if needed.
"""

from typing import Any


class SchemaValidator:
    """Simple validator shim used by KB components.

    Methods:
    - validate(obj): no-op (can be extended to raise on invalid data)
    """

    def __init__(self) -> None:
        pass

    def validate(self, obj: Any) -> None:
        """Performs basic schema validation on core entities.

        Args:
            obj: The entity to validate (ADR, Problem, etc.)

        Raises:
            ValueError: If the entity is missing mandatory fields or has invalid values.
        """
        # 1. ADR & Problem Quality Validation
        if hasattr(obj, "title") and hasattr(obj, "context"):
            if not obj.title or len(obj.title.strip()) < 10:
                raise ValueError(f"Invalid {type(obj).__name__}: Title must be at least 10 characters.")
            if not obj.context or len(obj.context.strip()) < 20:
                raise ValueError(f"Invalid {type(obj).__name__}: Context must be at least 20 characters for clarity.")

        # 2. ADR-Specific Logic (Decision and Consequences)
        if hasattr(obj, "decision") and hasattr(obj, "status"):
            if obj.status == "ACCEPTED" and (not obj.decision or len(obj.decision.strip()) < 10):
                raise ValueError("Accepted ADR must have a valid decision recorded.")

        # 3. Status Validation
        if hasattr(obj, "status"):
            valid_statuses = {"DRAFT", "CONDITIONAL", "ACCEPTED", "REJECTED", "EXPERIMENTAL"}
            if str(obj.status).upper() not in valid_statuses:
                raise ValueError(f"Invalid ADR status: {obj.status}. Must be one of {valid_statuses}")

        return
