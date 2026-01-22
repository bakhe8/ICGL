"""
Lightweight compatibility shims for observability.

The original project referenced `backend.observability.*` modules that are not
present in this tree. To keep the API/server running, we provide no-op stubs.
If observability is later implemented, replace these with real logic.
"""

from typing import Any, Optional


def init_observability(db_path: str) -> None:
    """No-op initializer to satisfy imports."""
    return None


def get_ledger() -> Optional[Any]:
    """Return None to indicate observability is not initialized."""
    return None


def get_broadcaster() -> Optional[Any]:
    return None


def get_detector() -> Optional[Any]:
    return None


def get_ml_detector() -> Optional[Any]:
    return None
