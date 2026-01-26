"""
Observability library (shim).

Delegates to `modules.observability`.
"""

import importlib

_impl = importlib.import_module("modules.observability")

globals().update(_impl.__dict__)
__all__ = getattr(_impl, "__all__", [])
