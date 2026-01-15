"""
Consensus AI — ICGL (Iterative Co-Governance Loop)
===================================================

The ICGL is the evolution engine of Consensus AI.

Manifesto Reference:
- "ICGL: Every important decision flows through governance before execution."

Lifecycle:
1. Proposal submitted
2. ADR drafted
3. Policy gate enforced
4. Sentinel scanning
5. Agent analysis & synthesis
6. Human sovereign decision
7. Knowledge base update
8. Next iteration
"""

from ..kb.schemas import ADR, LearningLog
from ..kb import KnowledgeBase
from ..sentinel import Sentinel
from ..hdal import HDAL


class ICGL:
    """
    ICGL: Iterative Co-Governance Loop.
    
    Orchestrates a single governance cycle:
    ADR Registration → Sentinel Scan → Human Decision → Learning Log
    """

    def __init__(self, kb: KnowledgeBase, sentinel: Sentinel, hdal: HDAL):
        self.kb = kb
        self.sentinel = sentinel
        self.hdal = hdal

    def run_cycle(self, adr: ADR, human_id: str):
        """
        Executes one complete ICGL governance cycle.
        
        Args:
            adr: The Architectural Decision Record to process.
            human_id: The human who will sign the decision.
        """
        print(f"[ICGL] 🔁 Starting governance cycle for: {adr.title}")

        # Step 3: Register ADR in Knowledge Base
        self.kb.add_adr(adr)

        # Step 4: Sentinel scanning
        alerts = self.sentinel.scan_adr(adr, self.kb)
        if alerts:
            print("[Sentinel] 🛡️ Alerts detected:")
            for alert in alerts:
                print(f"   - {alert}")

        # Step 6: Human sovereign decision
        decision = self.hdal.sign_decision(
            adr_id=adr.id,
            action="APPROVE",
            rationale="Bootstrap approval",
            human_id=human_id,
        )

        # Step 7: Knowledge base update
        self.kb.add_human_decision(decision)
        adr.human_decision_id = decision.id

        self.kb.add_learning_log(
            LearningLog(
                cycle=len(self.kb.learning_log) + 1,
                summary=f"Processed ADR {adr.id}: {adr.title}",
                new_policies=[],
                new_signals=[],
                new_concepts=[],
                notes="Bootstrap cycle",
            )
        )

        print(f"[ICGL] ✅ Cycle completed. Decision: {decision.action}")
