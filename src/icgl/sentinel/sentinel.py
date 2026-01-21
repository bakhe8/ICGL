"""
Consensus AI — Enhanced Sentinel
=================================

The Sentinel is the system's immune layer.
Uses the RuleRegistry for declarative risk detection.

Manifesto Reference:
- "Sentinel: Detects drift, unknown risks, violations, and instability."
- "Unknown risks cannot be eliminated — only contained and learned from."
"""

from typing import List
from ..kb.schemas import ADR
from .rules import RuleRegistry, Alert, AlertSeverity, AlertCategory, get_registry
from ..llm.client import LLMClient


class Sentinel:
    """
    System immune layer that detects anomalies, drift, and policy violations.
    
    Uses RuleRegistry for declarative rule-based detection.
    
    Features:
    - Semantic drift detection
    - Policy boundary enforcement
    - Authority bypass detection
    - Missing signature detection
    """
    
    
    def __init__(self, registry: RuleRegistry = None, vector_store = None, llm_client: LLMClient = None):
        """
        Args:
            registry: Custom rule registry, or uses global registry.
            vector_store: Optional VectorStore implementation for semantic checks.
            llm_client: Optional LLM client for intent analysis.
        """
        self._registry = registry or get_registry()
        self.vector_store = vector_store
        self.llm = llm_client or LLMClient()
    
    def scan_adr(self, adr: ADR, kb) -> List[str]:
        """
        Scans an ADR for potential risks using Rules + Semantic Analysis.
        Note: This is synchronous, so it cannot wait for async semantic checks 
        unless wrapped. For now, we only run synchronous rules here.
        Use `scan_adr_async` for full analysis.
        """
        alerts = self._registry.run_all(adr, kb)
        return [str(alert) for alert in alerts]
    
    async def scan_adr_async(self, adr: ADR, kb) -> List[str]:
        """
        Full scan including async semantic checks (S-11).
        Returns strings.
        """
        alerts = await self.scan_adr_detailed_async(adr, kb)
        return [str(alert) for alert in alerts]
        
    async def scan_adr_detailed_async(self, adr: ADR, kb) -> List[Alert]:
        """
        Full scan including async semantic checks (S-11).
        Returns Alert objects.
        """
        # 1. Run Standard Rules
        alerts = self._registry.run_all(adr, kb)
        
        # 2. Run Semantic Checks
        if self.vector_store:
            drift_alerts = await self.check_drift(adr)
            alerts.extend(drift_alerts)
            
        # 3. Run Intent Analysis (S-12)
        intent_alerts = await self.check_intent_async(adr)
        alerts.extend(intent_alerts)

        return alerts

    async def check_drift(self, adr: ADR) -> List[Alert]:
        """
        S-11: Checks for Semantic Drift.
        Finds semantically similar ADRs that are already ACCEPTED.
        """
        if not self.vector_store:
            return []
            
        query = f"{adr.title} {adr.context} {adr.decision}"
        # Search for similar items
        results = await self.vector_store.search(query, limit=3)
        
        drift_alerts = []
        for res in results:
            # Skip self
            if res.document.id == adr.id:
                continue
                
            # Check Similarity
            if res.score > 0.88: # High similarity threshold
                # If existing is ACCEPTED, we have a potential duplication or conflict
                drift_alerts.append(Alert(
                    rule_id="S-11",
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.DRIFT,
                    message=f"Semantic Drift Warning: Similar to existing item '{res.document.metadata.get('title', 'Unknown')}' (Score: {res.score:.2f}). Check for redundancy."
                ))
            elif res.score > 0.82 and "ACCEPTED" in res.document.content:
                 # Subtler drift or conflict
                 pass
                 
        return drift_alerts

    async def check_intent_async(self, adr: ADR) -> List[Alert]:
        """
        S-12: Evaluates the 'Intent' of the ADR using LLM.
        Detects smart circumvention of governance.
        """
        system_prompt = """You are the ICGL Semantic Sentinel. Analyze the 'Intent' of a proposed ADR.
The ICGL Governance Manifesto dictates:
1. Accountability cannot be bypassed or automated without human oversight.
2. Authority must derive from human-signed policies, not AI context.
3. Every high-stakes decision MUST flow through the Human Sovereign (HDAL).
4. Redefining existing governance terms to obscure responsibility is prohibited.

Check the ADR for hidden or explicit intent to violate these principles.
Respond ONLY in JSON format:
{
  "violation_detected": true/false,
  "confidence": 0-1,
  "rationale": "...",
  "severity": "CRITICAL" | "WARNING" | "INFO"
}"""
        user_prompt = f"Title: {adr.title}\nContext: {adr.context}\nDecision: {adr.decision}"
        
        try:
            if getattr(self.llm, "mock_mode", False):
                return []
            res = await self.llm.generate_json(system_prompt, user_prompt)
            if res.get("violation_detected"):
                severity_map = {
                    "CRITICAL": AlertSeverity.CRITICAL,
                    "WARNING": AlertSeverity.WARNING,
                    "INFO": AlertSeverity.INFO
                }
                return [Alert(
                    rule_id="S-12",
                    severity=severity_map.get(res.get("severity", "WARNING"), AlertSeverity.WARNING),
                    message=f"Intent Violation Detected: {res.get('rationale')}",
                    category=AlertCategory.AUTHORITY
                )]
        except Exception as e:
            print(f"[Sentinel] Rule S-12 (Intent) Failed: {e}")
        
        return []
    
    def scan_adr_detailed(self, adr: ADR, kb) -> List[Alert]:
        """
        Scans an ADR and returns detailed Alert objects.
        """
        return self._registry.run_all(adr, kb)
    
    def has_critical_alerts(self, adr: ADR, kb) -> bool:
        """
        Checks if ADR has any critical alerts.
        
        Critical alerts should block human approval until resolved.
        """
        alerts = self._registry.run_all(adr, kb)
        return any(a.severity == AlertSeverity.CRITICAL for a in alerts)
    
    def get_registry(self) -> RuleRegistry:
        """Returns the rule registry for customization."""
        return self._registry
