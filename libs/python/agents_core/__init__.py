"""
Agents Core library (shim).

Delegates to `modules.agents` so callers can depend on this package
while the domain is extracted into a standalone library.
"""

import importlib

_impl = importlib.import_module("modules.agents")

# Re-export everything for compatibility
globals().update(_impl.__dict__)
__all__ = getattr(_impl, "__all__", [])
