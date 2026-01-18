import asyncio
import sys
from pathlib import Path
from datetime import datetime
import random

# Add src
sys.path.append(str(Path.cwd() / "src"))

from icgl.observability import init_observability, get_ledger, SovereignMonitorLoop, EventType, ObservabilityEvent
from icgl.kb.schemas import uid

async def activate_and_demo():
    print("🛰️ ACTIVATING SOVEREIGN MONITORING")
    print("==================================")
    
    # 1. Initialize System
    db_path = "data/observability.db"
    # Ensure dir exists
    Path("data").mkdir(exist_ok=True)
    
    init_observability(db_path)
    ledger = get_ledger()
    
    if not ledger:
        print("❌ Failed to initialize Ledger.")
        return

    # 2. Setup Monitor
    monitor = SovereignMonitorLoop(ledger)
    
    # 3. Start Monitor in background
    monitor_task = asyncio.create_task(monitor.start())
    
    print("✅ System Online. Broadcasting Heartbeat...")
    
    try:
        # Simulate a stream of events for 30 seconds
        for i in range(5):
            # Create a heartbeat event
            event = ObservabilityEvent(
                event_id=uid(),
                event_type=EventType.AGENT_INVOKED,
                timestamp=datetime.utcnow(),
                trace_id=uid(),
                span_id=uid(),
                actor_type="system",
                actor_id="HeartbeatService",
                action="pulse",
                status="success",
                tags={"load": f"{random.randint(10, 30)}%"}
            )
            
            print(f"📡 Pulse {i+1}... (Event: {event.event_id})")
            ledger.log(event)
            
            # Occasionally simulate a warning
            if i == 2:
                warning = ObservabilityEvent(
                    event_id=uid(),
                    event_type=EventType.POLICY_CHECKED,
                    timestamp=datetime.utcnow(),
                    trace_id=uid(),
                    span_id=uid(),
                    actor_type="agent",
                    actor_id="MonitorAgent",
                    action="boundary_scan",
                    status="success",
                    target="src/icgl/governance",
                    tags={"result": "SAFE"}
                )
                print("⚠️  Running Strategic Boundary Scan...")
                ledger.log(warning)

            await asyncio.sleep(4)
            
        print("\n✅ Monitoring Demo Complete. The Loop is now active at the system level.")
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down.")
    finally:
        monitor.stop()
        await monitor_task

if __name__ == "__main__":
    asyncio.run(activate_and_demo())
