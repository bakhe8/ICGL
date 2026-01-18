import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src
sys.path.append(str(Path.cwd() / "src"))

from icgl.observability import init_observability, get_ledger, SovereignMonitorLoop, EventType, ObservabilityEvent
from icgl.kb import PersistentKnowledgeBase, uid

async def stress_test_pilot():
    print("🛰️ EXECUTING SLACK PILOT STRESS TEST (ADR-PILOT-OPS-05-001)")
    print("=========================================================")
    
    # 1. Init
    db_path = "data/observability.db"
    init_observability(db_path)
    ledger = get_ledger()
    
    monitor = SovereignMonitorLoop(ledger)
    print("✅ Monitor Loop loaded with Governed Slack Adapter.")
    
    # 2. Simulate CRITICAL POLICY VIOLATION
    print("\n[TEST] Simulating Policy Violation (Forbidden Write)...")
    violation = ObservabilityEvent(
        event_id=uid(),
        event_type=EventType.POLICY_VIOLATED,
        timestamp=datetime.utcnow(),
        trace_id=uid(),
        span_id=uid(),
        actor_type="agent",
        actor_id="RogueAgentSimulator",
        action="write_to_core",
        target="src/icgl/governance/icgl.py",
        status="failure",
        error_message="Hard Boundary Breach"
    )
    ledger.log(violation)
    
    # Run one tick to process
    await monitor.tick()
    
    # 3. Simulate IGNORED CATEGORY (Notification should be skipped)
    print("\n[TEST] Simulating Low-Level Event (Should be skipped by Slack filter)...")
    low_event = ObservabilityEvent(
        event_id=uid(),
        event_type=EventType.AGENT_RESPONDED,
        timestamp=datetime.utcnow(),
        trace_id=uid(),
        span_id=uid(),
        actor_type="agent",
        actor_id="MonitorAgent",
        action="log_metrics",
        status="success"
    )
    ledger.log(low_event)
    await monitor.tick()
    
    # 4. Test KILL SWITCH
    print("\n[TEST] Activating Kill Switch...")
    monitor.slack.kill_switch()
    
    print("[TEST] Simulating Another Critical Alert (Should be blocked by Kill Switch)...")
    ledger.log(violation)
    await monitor.tick()
    
    print("\n✅ PILOT STRESS TEST COMPLETE.")

if __name__ == "__main__":
    asyncio.run(stress_test_pilot())
