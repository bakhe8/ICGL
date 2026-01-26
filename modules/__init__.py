"""
Modules namespace package.

Staging area for domain modules (agents, governance, observability, memory, knowledge_base, hr, hdal, policies).
Initially re-exports existing backend packages to keep imports stable while we migrate.
"""

import importlib
import pkgutil

# Extend package path for submodules if needed
pkgutil.extend_path(__path__, __name__)

# Optionally preload shims (import on demand)
def __getattr__(name):
  if name in {"agents", "governance", "observability", "memory", "knowledge_base", "kb", "hr", "llm", "core", "git", "utils", "sentinel", "hdal", "policies"}:
    return importlib.import_module(f"{__name__}.{name}")
  raise AttributeError(name)


__all__ = ["agents", "governance", "observability", "memory", "knowledge_base", "kb", "hr", "llm", "core", "git", "utils", "sentinel", "hdal", "policies"]
