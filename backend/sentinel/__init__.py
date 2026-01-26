"""
Shim: delegates Sentinel domain to `modules.sentinel` (canonical).
"""

import importlib

_impl = importlib.import_module("modules.sentinel")
globals().update(_impl.__dict__)
__path__ = _impl.__path__
__all__ = getattr(_impl, "__all__", [])
