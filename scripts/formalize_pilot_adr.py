import asyncio
import sys
from pathlib import Path

# Add src
sys.path.append(str(Path.cwd() / "src"))

from icgl.kb import PersistentKnowledgeBase, ADR, HumanDecision, uid, now

async def formalize_pilot_adr():
    print("🏛️ FORMALIZING SOVEREIGN DECISION: ADR-PILOT-OPS-05-001")
    print("=========================================================")
    
    kb = PersistentKnowledgeBase()
    
    # 1. Create the ADR (Aligned with schema)
    pilot_adr = ADR(
        id="ADR-PILOT-OPS-05-001",
        title="Controlled External Notification Hook (Slack)",
        status="CONDITIONAL",
        context="MonitorAgent requested a Slack hook for proactive alerting (P-OPS-05 test).",
        decision="Conditional Approval for a Controlled Pilot implementation.",
        consequences=["Governed pattern for external alerts", "Reduced response time for critical drift"],
        related_policies=["P-OPS-05"],
        sentinel_signals=[],
        human_decision_id=None # Will be linked below
    )
    
    # 2. Record the Sovereign Decision
    decision_id = uid()
    decision = HumanDecision(
        id=decision_id,
        adr_id=pilot_adr.id,
        action="APPROVE", # Literal based on DecisionAction type
        rationale="Testing P-OPS-05 protocol via a controlled pilot. Scope must be outbound only.",
        signed_by="Sovereign_CEO",
        signature_hash="SIG_SOVEREIGN_PILOT_M_2026.1",
        timestamp=now()
    )
    
    pilot_adr.human_decision_id = decision_id
    
    kb.add_adr(pilot_adr)
    kb.add_human_decision(decision)
    
    print(f"✅ ADR Formally Registered: {pilot_adr.id}")
    print(f"✅ Sovereign Decision Linked: {decision_id}")

if __name__ == "__main__":
    asyncio.run(formalize_pilot_adr())
