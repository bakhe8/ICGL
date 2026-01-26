"""
Memory library (shim).

Delegates to `modules.memory`.
"""

import importlib

_impl = importlib.import_module("modules.memory")

globals().update(_impl.__dict__)
__all__ = getattr(_impl, "__all__", [])
