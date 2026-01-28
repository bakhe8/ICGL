"""Lightweight git adapter package placeholder.

Provides a minimal `GitAdapter` used by the `EngineerAgent`. This shim
is intentionally simple to allow the backend to run in development and
CI environments where git integration is optional.
"""

from .adapter import GitAdapter

__all__ = ["GitAdapter"]
