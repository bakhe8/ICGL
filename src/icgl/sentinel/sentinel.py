"""
Consensus AI — Sentinel
========================

The Sentinel is the system's immune layer.

Manifesto Reference:
- "Sentinel: Detects drift, unknown risks, violations, and instability."
- "Unknown risks cannot be eliminated — only contained and learned from."
"""

from typing import List
from ..kb.schemas import ADR


class Sentinel:
    """
    System immune layer that detects anomalies, drift, and policy violations.
    
    Current implementation is a stub. Future versions will include:
    - Semantic drift detection
    - Policy boundary enforcement
    - Cost anomaly detection
    - Stability analysis
    """

    def scan_adr(self, adr: ADR, kb) -> List[str]:
        """
        Scans an ADR for potential risks before human review.
        
        Returns:
            A list of alert messages (empty if no issues found).
        """
        alerts: List[str] = []

        # Rule: All ADRs should reference at least one policy.
        if adr.status == "DRAFT" and not adr.related_policies:
            alerts.append("⚠️ ADR has no related policies (potential drift risk)")

        return alerts
