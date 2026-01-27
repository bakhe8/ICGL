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
        """No-op validation to allow legacy data to pass through.

        Override this method to implement schema checks.
        """
        return
