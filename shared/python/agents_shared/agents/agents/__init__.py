"""
Consensus AI ? Agents Package (shim)
====================================

Delegates to modules.agents.agents as the canonical implementation.
"""

import importlib

_modules_pkg = importlib.import_module("modules.agents.agents")

# Allow resolving submodules via backend.agents.*
__path__ = _modules_pkg.__path__

for name in getattr(_modules_pkg, "__all__", []):
    globals()[name] = getattr(_modules_pkg, name)

__all__ = getattr(_modules_pkg, "__all__", [])
