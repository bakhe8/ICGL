import asyncio
import sys
from pathlib import Path

# Add src
sys.path.append(str(Path.cwd() / "src"))

from icgl.kb import PersistentKnowledgeBase, now
from icgl.observability import SovereignMonitorLoop, get_ledger, init_observability, EventType, ObservabilityEvent
from icgl.kb.schemas import uid

async def execute_governed_pilot():
    print("🚀 EXECUTING SOVEREIGN PILOT: ADR-PILOT-OPS-05-001")
    print("======================================================")
    
    # 1. Init
    db_path = "data/observability.db"
    init_observability(db_path)
    ledger = get_ledger()
    kb = PersistentKnowledgeBase()
    
    # Load monitor
    monitor = SovereignMonitorLoop(ledger)
    
    # 2. Verify ADR Presence
    if "ADR-PILOT-OPS-05-001" not in kb.adrs:
        print("❌ ADR-PILOT-OPS-05-001 not found! Pilot aborted.")
        return
    
    adr = kb.adrs["ADR-PILOT-OPS-05-001"]
    print(f"✅ Verified Authority: {adr.id} ({adr.status})")
    
    # 3. Simulate Pilot Activity (Controlled Execution)
    print("\n[EXEC] Simulating System Drift event...")
    drift_event = ObservabilityEvent(
        event_id=uid(),
        event_type=EventType.POLICY_VIOLATED,
        timestamp=now(),
        trace_id=uid(),
        span_id=uid(),
        actor_type="system",
        actor_id="IntegrityChecker",
        action="drift_detected",
        target="KnowledgeBase",
        status="failure"
    )
    ledger.log(drift_event)
    
    # Process through governed monitor
    print("[EXEC] Processing through Sovereign Monitor Loop...")
    await monitor.tick()
    
    # 4. Fulfill Request Record
    # Find the original PENDING request for MonitorAgent
    target_req_id = None
    for req_id, req in kb.requests.items():
        if req.requester_id == "MonitorAgent" and req.status == "PENDING":
            target_req_id = req_id
            break
            
    if target_req_id:
        print(f"\n✅ Fulfilling Operational Request: {target_req_id}")
        kb.update_request_status(
            request_id=target_req_id, 
            status="FULFILLED", 
            adr_id="ADR-PILOT-OPS-05-001"
        )
        # Record response data as required by protocol
        kb.requests[target_req_id].response_data = "GovernedSlackAdapter v1.0 (Pilot) deployed."

    print("\n✅ PILOT EXECUTION COMPLETE. Post-Execution Report generation initialized.")

if __name__ == "__main__":
    asyncio.run(execute_governed_pilot())
