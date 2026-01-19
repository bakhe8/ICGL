import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Optional

from .events import ObservabilityEvent, EventType
from .ledger import ObservabilityLedger
from .broadcaster import get_broadcaster
from .slack_adapter import GovernedSlackAdapter
from sentinel.sentinel import Sentinel
from agents.secretary_agent import SecretaryAgent
from utils.logging_config import get_logger

logger = get_logger(__name__)

class SovereignMonitorLoop:
    """
    Real-time monitoring daemon for the ICGL system.
    Operationalizes the 'Security & Compliance' Department.
    """
    
    def __init__(self, ledger: ObservabilityLedger, sentinel: Optional[Sentinel] = None):
        self.ledger = ledger
        self.sentinel = sentinel or Sentinel()
        self.broadcaster = get_broadcaster()
        self.slack = GovernedSlackAdapter() # Outbound Pilot Lock
        self.secretary = SecretaryAgent("SovereignSecretary") # Chief of Staff
        self.running = False
        self._last_event_id: Optional[str] = None

    async def start(self):
        """Starts the infinite monitor loop."""
        self.running = True
        logger.info("🛰️ Sovereign Monitor Loop STARTED.")
        
        while self.running:
            try:
                await self.tick()
                await asyncio.sleep(2) # Monitor every 2 seconds
            except Exception as e:
                logger.error(f"❌ Monitor Loop Pulse Error: {e}")
                await asyncio.sleep(5)

    async def tick(self):
        """Single monitoring cycle."""
        # 1. Fetch NEW events since last tick
        # (This is a simplified polling approach. In prod, we might use a queue/pub-sub).
        events = self._get_new_events()
        
        if not events:
            return

        for event in events:
            # 2. Analyze Event Behavior
            await self._analyze_event(event)
            
            # 3. Broadcast to Cockpit
            await self.broadcaster.broadcast_event(event)
            
        self._last_event_id = events[-1].event_id

    def _get_new_events(self) -> List[ObservabilityEvent]:
        """Fetches events from ledger added since last tick."""
        # Note: Ledger implementation needs to support 'since_id' or time filtering.
        # For this demo, we'll fetch the last 10 and filter locally.
        all_recent = self.ledger.get_recent_events(limit=20)
        
        if not self._last_event_id:
            return all_recent
            
        new_events = []
        for e in all_recent:
            if e.event_id == self._last_event_id:
                break
            new_events.append(e)
            
        return list(reversed(new_events)) # Order chronologically

    async def _analyze_event(self, event: ObservabilityEvent):
        """Runs Sentinel rules and Chief of Staff enrichment."""
        
        # 🟢 Sovereign Office: Automated Enrichment (Arabic)
        event.description_ar = await self.secretary.translate_event(
            event.event_type.value, 
            event.actor_id, 
            event.__dict__
        )
        
        # Pattern A: Multi-Agent Cascade (Detect runaway loops)
        if event.event_type == EventType.AGENT_FAILED:
             logger.warning(f"⚠️ FAILURE DETECTED: {event.actor_id} - {event.error_message}")
             # Trigger an "Alert" event back into the system
             alert_event = ObservabilityEvent(
                 event_id=f"alert-{int(time.time())}",
                 event_type=EventType.SENTINEL_ALERT,
                 timestamp=datetime.utcnow(),
                 trace_id=event.trace_id,
                 span_id="sentinel-alert",
                 actor_type="system",
                 actor_id="Sentinel",
                 action="raise_alert",
                 status="success",
                 error_message=f"Critical Agent Failure in {event.actor_id}"
             )
             await self.broadcaster.broadcast_event(alert_event)

        # Pattern B: Policy Violation
        if event.event_type == EventType.POLICY_VIOLATED:
            logger.critical(f"🛑 POLICY VIOLATION: {event.target} by {event.actor_id}")
            # Pilot Alert: External Notification
            await self.slack.notify(
                category="CRITICAL",
                message=f"Policy Violation Detected: {event.target} (Actor: {event.actor_id})",
                metadata={"trace_id": event.trace_id}
            )
            
        # Pattern C: Sentinel Alert (Critical systemic failure)
        if event.event_type == EventType.SENTINEL_ALERT:
            await self.slack.notify(
                category="CRITICAL",
                message=f"Systemic Sentinel Alert: {event.error_message}",
                metadata={"trace_id": event.trace_id}
            )
            
    def stop(self):
        self.running = False
        logger.info("🛰️ Monitor Loop STOPPED.")
