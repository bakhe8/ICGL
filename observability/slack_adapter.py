from datetime import datetime
from typing import Optional, Dict, Any
from utils.logging_config import get_logger
from kb import now

logger = get_logger(__name__)

class GovernedSlackAdapter:
    """
    Controlled Pilot: Slack Notification Hook (ADR-PILOT-OPS-05-001).
    
    Hard Constraints:
    1. Outbound only (Notifications).
    2. Fixed Channel (Simulated).
    3. Filtering (Only Critical/Drift/Integrity).
    4. Kill Switch (Mechanical override).
    """
    
    def __init__(self, channel: str = "#icgl-alerts"):
        self.target_channel = channel
        self.is_active = True # Kill Switch State
        self.allowed_categories = {"CRITICAL", "DRIFT", "INTEGRITY"}
        logger.info(f"🛰️ Governed Slack Adapter initialized for {channel}.")

    def kill_switch(self):
        """Emergency shutdown of external communication."""
        self.is_active = False
        logger.critical("🛑 SLACK KILL SWITCH ACTIVATED. External comms terminated.")

    async def notify(self, category: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Outbound-Only notification method.
        """
        if not self.is_active:
            logger.warning("⚠️ Slack notify attempted but Kill Switch is ACTIVE.")
            return

        if category.upper() not in self.allowed_categories:
            logger.debug(f"ℹ️ Skipping Slack notification for category {category} (Protocol Filter).")
            return

        # SIMULATED SLACK CALL
        # In production, this would be requests.post(webhook_url, json=...)
        payload = {
            "channel": self.target_channel,
            "category": category.upper(),
            "message": message,
            "timestamp": now(),
            "metadata": metadata or {}
        }
        
        print(f"\n[SLACK OUTBOUND] >>> Message to {self.target_channel}:")
        print(f"   [{category.upper()}] {message}")
        print(f"   (Trace: {payload['timestamp']})")
        
        logger.info(f"✅ Slack Notification SENT: {category}")

    def get_pilot_status(self) -> Dict[str, Any]:
        return {
            "pilot_id": "ADR-PILOT-OPS-05-001",
            "active": self.is_active,
            "scope": "READ_ONLY",
            "categories": list(self.allowed_categories)
        }
