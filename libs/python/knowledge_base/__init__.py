"""
Knowledge Base library (shim).

Delegates to the canonical implementation under `modules.kb`.
This keeps imports stable while the package is extracted as a standalone library.
"""

import importlib

_impl = importlib.import_module("modules.kb")

# Re-export everything for compatibility
globals().update(_impl.__dict__)
__all__ = getattr(_impl, "__all__", [])
