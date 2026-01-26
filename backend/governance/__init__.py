"""
Consensus AI — Governance Package
==================================

This package contains the ICGL (Iterative Co-Governance Loop) orchestrator.

Note: Avoid importing ICGL at package import time to prevent circular imports
with agents. Import `ICGL` directly from `backend.governance.icgl` when needed.
"""

from modules.governance.icgl import ICGL

__all__ = ["ICGL"]
