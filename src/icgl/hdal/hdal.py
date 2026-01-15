"""
Consensus AI — Human Decision Authority Layer (HDAL)
=====================================================

The HDAL ensures that ALL sovereign decisions are signed by a human.

Manifesto Reference:
- "HDAL: Final human authority. All sovereign decisions must be signed."
- "No concept, policy, or core rule may change without explicit human approval."
"""

from ..kb.schemas import ID, DecisionAction, HumanDecision, now, uid


class HDAL:
    """
    Human Decision Authority Layer.
    
    This component ensures:
    - All critical decisions require human approval.
    - Every approval is signed and traceable.
    - The human remains the final authority.
    """

    def sign_decision(
        self,
        adr_id: ID,
        action: DecisionAction,
        rationale: str,
        human_id: str,
    ) -> HumanDecision:
        """
        Creates a signed Human Decision for an ADR.
        
        Args:
            adr_id: The ID of the ADR being decided.
            action: APPROVE, REJECT, MODIFY, or EXPERIMENT.
            rationale: Human-provided reasoning.
            human_id: Identifier of the signing human.
        
        Returns:
            A HumanDecision record with a signature hash.
        """
        # Placeholder signature (TODO: replace with crypto/HSM)
        signature = f"signed-by:{human_id}:{adr_id}:{now()}"

        return HumanDecision(
            id=uid(),
            adr_id=adr_id,
            action=action,
            rationale=rationale,
            signed_by=human_id,
            signature_hash=signature,
        )
