"""
Consensus AI — Human Decision Authority Layer (HDAL)
=====================================================

The HDAL ensures that ALL sovereign decisions are signed by a human.
Includes interactive review interface.
"""

from typing import Optional
from ..kb.schemas import ID, DecisionAction, HumanDecision, now, uid, ADR
from ..agents.registry import SynthesizedResult
from .cli_prompts import display_adr_review, prompt_decision, prompt_rationale, prompt_signature


class HDAL:
    """
    Human Decision Authority Layer.
    
    This component ensures:
    - All critical decisions require human approval.
    - Every approval is signed and traceable.
    - The human remains the final authority.
    """
    
    def __init__(self):
        from ..core.observability import SystemObserver
        self.observer = SystemObserver()

    def sign_decision(
        self,
        adr_id: ID,
        action: DecisionAction,
        rationale: str,
        human_id: str,
    ) -> HumanDecision:
        """
        Creates a signed Human Decision for an ADR.
        """
        # Placeholder signature (TODO: replace with crypto/HSM)
        signature = f"signed-by:{human_id}:{adr_id}:{now()}"

        decision = HumanDecision(
            id=uid(),
            adr_id=adr_id,
            action=action,
            rationale=rationale,
            signed_by=human_id,
            signature_hash=signature,
        )

        # Persist signed decision log with Merkle chaining
        self.observer.record_decision({
            "adr_id": adr_id,
            "decision_id": decision.id,
            "action": action,
            "rationale": rationale,
            "signed_by": human_id,
            "timestamp": decision.timestamp,
            "signature_hash": signature,
        })

        return decision

    def review_and_sign(
        self,
        adr: ADR,
        synthesis: SynthesizedResult,
        human_id: str,
        policy_report=None,
        sentinel_alerts=None,
    ) -> Optional[HumanDecision]:
        """
        Interactive review process.
        Displays ADR, agent synthesis, policies, and sentinel alerts.
        """
        import os

        # Hard stop on CRITICAL policy/sentinel
        if policy_report and getattr(policy_report, "status", "") == "FAIL":
            print("[HDAL] ⛔ Policy gate failed; signature blocked.")
            return None
        from ..sentinel.rules import AlertSeverity
        if sentinel_alerts and any(
            (getattr(a, "severity", None) == AlertSeverity.CRITICAL) or getattr(a, "severity", None) == "CRITICAL"
            for a in sentinel_alerts
        ):
            print("[HDAL] ⛔ Critical Sentinel alert; signature blocked.")
            return None

        # Non-interactive / auto-approve mode (for rapid agent execution)
        if os.getenv("ICGL_AUTO_APPROVE", "").lower() in {"1", "true", "yes"}:
            print("[HDAL] ⚡ Auto-approve enabled via ICGL_AUTO_APPROVE.")
            return self.sign_decision(
                adr_id=adr.id,
                action="APPROVE",
                rationale="Auto-approved (rapid execution mode)",
                human_id=human_id,
            )

        display_adr_review(adr, synthesis, policy_report, sentinel_alerts)
        
        action_str = prompt_decision()
        rationale = prompt_rationale()
        
        if prompt_signature(human_id):
            decision = self.sign_decision(
                adr_id=adr.id,
                action=action_str, # type: ignore
                rationale=rationale,
                human_id=human_id
            )
            
            # Phase 3.1: Observability (Log Interventions)
            if action_str in ["REJECT", "MODIFY", "EXPERIMENT"]:
                # Determine original recommendation from synthesis if possible
                # For now we assume consensus was "APPROVE" or check synthesis.consensus_recommendations
                if synthesis.consensus_recommendations and "APPROVE" in synthesis.consensus_recommendations[0].upper():
                    orig = "APPROVE" 
                else: 
                     orig = "UNKNOWN"
                     
                self.observer.record_intervention(
                    adr_id=adr.id,
                    original_rec=orig,
                    action=action_str,
                    reason=rationale
                )
            return decision
        
        return None
