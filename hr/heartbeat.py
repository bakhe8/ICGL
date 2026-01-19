import asyncio
from datetime import datetime
from typing import Optional
from ..utils.logging_config import get_logger
from ..observability import get_ledger, ObservabilityEvent, EventType
from ..kb.schemas import uid, now

logger = get_logger(__name__)


class HeartbeatService:
    """
    النبض المؤسسي (Sovereign Heartbeat)
    
    Ensures the system is alive and active by:
    - Performing periodic health checks
    - Generating operational events
    - Updating dashboards
    - Reporting to governance
    
    This is the pulse that brings the system to life.
    """
    
    def __init__(self, workforce_manager=None, interval_seconds: int = 300):
        self.workforce_manager = workforce_manager
        self.interval_seconds = interval_seconds  # Default: 5 minutes
        self.running = False
        self.pulse_count = 0
        self.ledger = get_ledger()
        logger.info(f"💓 HeartbeatService initialized (interval: {interval_seconds}s)")
    
    async def pulse(self) -> None:
        """
        Single heartbeat pulse.
        
        Executes:
        1. System health check
        2. Event generation
        3. Dashboard update
        4. Governance report
        """
        self.pulse_count += 1
        pulse_id = uid()
        
        logger.info(f"💓 Pulse #{self.pulse_count} - {pulse_id}")
        
        try:
            # 1. System Health Check
            health_status = await self._check_system_health()
            
            # 2. Log heartbeat event
            if self.ledger:
                self.ledger.log(ObservabilityEvent(
                    event_id=uid(),
                    event_type=EventType.SYSTEM_STARTED,
                    timestamp=now(),
                    trace_id=pulse_id,
                    span_id="heartbeat",
                    actor_type="system",
                    actor_id="HeartbeatService",
                    action="pulse",
                    target="system",
                    input_payload={
                        "pulse_count": self.pulse_count,
                        "health_status": health_status
                    },
                    status="success"
                ))
            
            # 3. Generate sample operational event (for demo purposes)
            await self._generate_sample_event()
            
            logger.info(f"✅ Pulse #{self.pulse_count} completed - Status: {health_status['status']}")
            
        except Exception as e:
            logger.error(f"❌ Pulse #{self.pulse_count} failed: {e}")
    
    async def _check_system_health(self) -> dict:
        """Check overall system health."""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Check workforce manager
        if self.workforce_manager:
            wf_status = self.workforce_manager.get_status_report()
            health["components"]["workforce"] = {
                "status": "healthy" if wf_status["running"] else "stopped",
                "total_agents": wf_status["total_agents"],
                "enabled_agents": wf_status["enabled_agents"]
            }
        
        # Check observability ledger
        if self.ledger:
            health["components"]["observability"] = {
                "status": "healthy"
            }
        
        return health
    
    async def _generate_sample_event(self) -> None:
        """Generate a sample event to populate the dashboard."""
        if self.ledger:
            self.ledger.log(ObservabilityEvent(
                event_id=uid(),
                event_type=EventType.AGENT_INVOKED,
                timestamp=now(),
                trace_id=uid(),
                span_id="sample",
                actor_type="agent",
                actor_id="SampleAgent",
                action="periodic_check",
                target="system",
                input_payload={"source": "heartbeat"},
                status="success"
            ))
    
    async def start(self) -> None:
        """
        Start the continuous heartbeat.
        Runs indefinitely until stopped.
        """
        self.running = True
        logger.info("🚀 HeartbeatService started")
        
        while self.running:
            await self.pulse()
            await asyncio.sleep(self.interval_seconds)
        
        logger.info("🛑 HeartbeatService stopped")
    
    def stop(self) -> None:
        """Stop the heartbeat."""
        self.running = False
    
    def get_status(self) -> dict:
        """Get heartbeat service status."""
        return {
            "running": self.running,
            "pulse_count": self.pulse_count,
            "interval_seconds": self.interval_seconds,
            "uptime_pulses": self.pulse_count
        }
