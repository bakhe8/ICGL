import asyncio
import sys
from pathlib import Path

# Add src
sys.path.append(str(Path.cwd() / "src"))

from icgl.coordination import CoordinationOrchestrator
from icgl.kb import PersistentKnowledgeBase, uid

async def test_coordination_protocol():
    print("🏛️ EXECUTING INTER-DEPARTMENT COORDINATION PROTOCOL (IDCP)")
    print("=========================================================")
    
    kb = PersistentKnowledgeBase()
    orch = CoordinationOrchestrator(kb)
    
    # 1️⃣ STAGE: Need Detection & Formal Request
    print("\n[1] Agent 'MonitorAgent' detecting need for 'Security Audit Tool'...")
    request_id = await orch.submit_request(
        requester="MonitorAgent",
        department="Engineering",
        requirement="Automated VPR Dependency Scanner",
        rationale="To prevent security drift according to P-OPS-05.",
        urgency="HIGH",
        risk_level="MEDIUM"
    )
    
    # 2️⃣ STAGE: Department Fulfillment
    print(f"\n[2] Engineering Department receiving request {request_id} via Orchestrator...")
    await asyncio.sleep(1)
    await orch.fulfill_request(
        request_id=request_id,
        department_agent="EngineerAgent",
        output_data="vpr_scanner_v1.py successfully scaffolded in staging."
    )
    
    # 3️⃣ STAGE: Governance Elevation
    print("\n[3] Elevating fulfillment to Governance (HDAL) for approval...")
    # Simulate a human signing an ADR logic
    adr_id = f"ADR-{uid()[:8]}"
    await orch.verify_governance(
        request_id=request_id,
        signed_by="Sovereign_CEO",
        adr_id=adr_id
    )
    
    # FINAL VERIFICATION
    final_req = kb.requests[request_id]
    print(f"\n✅ PROTOCOL COMPLETE:")
    print(f"   Request Status: {final_req.status}")
    print(f"   Authorized By:  {final_req.governance_adr_id}")
    print(f"   Output Proof:   {final_req.response_data}")

if __name__ == "__main__":
    asyncio.run(test_coordination_protocol())
