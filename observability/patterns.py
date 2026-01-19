"""
Pattern Detector
----------------

Rule-based pattern detection for agent behavior monitoring.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from .events import ObservabilityEvent, EventType


@dataclass
class Alert:
    """Pattern detection alert"""
    alert_id: str
    severity: str  # "low", "medium", "high", "critical"
    pattern: str
    description: str
    events: List[str]  # Event IDs
    timestamp: datetime
    metadata: Dict[str, Any]


class PatternDetector:
    """
    Detects suspicious patterns in agent behavior.
    
    Phase 1: Rule-based patterns
    Phase 2: ML-based anomaly detection (future)
    """
    
    def __init__(self):
        self.alerts: List[Alert] = []
    
    def detect_patterns(self, events: List[ObservabilityEvent], window_minutes: int = 5) -> List[Alert]:
        """
        Detect patterns in recent events.
        
        Args:
            events: Recent events to analyze
            window_minutes: Time window for pattern detection
            
        Returns:
            List of detected alerts
        """
        alerts = []
        
       # Pattern 1: Channel spam
        channel_spam = self._detect_channel_spam(events, window_minutes)
        if channel_spam:
            alerts.append(channel_spam)
        
        # Pattern 2: Circular messaging
        circular = self._detect_circular_messages(events, window_minutes)
        if circular:
            alerts.append(circular)
        
        # Pattern 3: Violation trend
        violations = self._detect_violation_trend(events, window_minutes)
        if violations:
            alerts.append(violations)
        
        # Pattern 4: Excessive LLM calls
        llm_spam = self._detect_llm_spam(events, window_minutes)
        if llm_spam:
            alerts.append(llm_spam)
        
        self.alerts.extend(alerts)
        return alerts
    
    def _detect_channel_spam(self, events: List[ObservabilityEvent], window_minutes: int) -> Alert | None:
        """Detect if agent is creating too many channels"""
        from ..kb.schemas import uid
        
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        channel_creates = [
            e for e in events
            if e.event_type == EventType.CHANNEL_CREATED and e.timestamp >= cutoff
        ]
        
        if len(channel_creates) > 10:  # More than 10 channels in window
            return Alert(
                alert_id=uid(),
                severity="high",
                pattern="channel_spam",
                description=f"Agent creating excessive channels: {len(channel_creates)} in {window_minutes} minutes",
                events=[e.event_id for e in channel_creates],
                timestamp=datetime.utcnow(),
                metadata={"count": len(channel_creates), "window_minutes": window_minutes}
            )
        return None
    
    def _detect_circular_messages(self, events: List[ObservabilityEvent], window_minutes: int) -> Alert | None:
        """Detect circular messaging loops"""
        from ..kb.schemas import uid
        
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        messages = [
            e for e in events
            if e.event_type == EventType.CHANNEL_MESSAGE and e.timestamp >= cutoff
        ]
        
        # Simple heuristic: same agents in same channel > 20 messages
        channel_counts = {}
        for msg in messages:
            channel_id = msg.tags.get("channel_id") if msg.tags else None
            if channel_id:
                channel_counts[channel_id] = channel_counts.get(channel_id, 0) + 1
        
        for channel_id, count in channel_counts.items():
            if count > 20:
                return Alert(
                    alert_id=uid(),
                    severity="critical",
                    pattern="circular_messaging",
                    description=f"Possible infinite loop in channel {channel_id}: {count} messages",
                    events=[e.event_id for e in messages if e.tags and e.tags.get("channel_id") == channel_id],
                    timestamp=datetime.utcnow(),
                    metadata={"channel_id": channel_id, "message_count": count}
                )
        return None
    
    def _detect_violation_trend(self, events: List[ObservabilityEvent], window_minutes: int) -> Alert | None:
        """Detect increasing policy violations"""
        from ..kb.schemas import uid
        
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        violations = [
            e for e in events
            if e.event_type == EventType.CHANNEL_MESSAGE 
            and e.status == "failure" 
            and e.timestamp >= cutoff
            and (e.tags and e.tags.get("violation") == "true")
        ]
        
        if len(violations) > 5:  # More than 5 violations
            return Alert(
                alert_id=uid(),
                severity="medium",
                pattern="increasing_violations",
                description=f"Increasing policy violations: {len(violations)} in {window_minutes} minutes",
                events=[e.event_id for e in violations],
                timestamp=datetime.utcnow(),
                metadata={"violation_count": len(violations)}
            )
        return None
    
    def _detect_llm_spam(self, events: List[ObservabilityEvent], window_minutes: int) -> Alert | None:
        """Detect excessive LLM calls"""
        from ..kb.schemas import uid
        
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        llm_calls = [
            e for e in events
            if e.event_type == EventType.LLM_CALLED and e.timestamp >= cutoff
        ]
        
        if len(llm_calls) > 50:  # More than 50 LLM calls
            return Alert(
                alert_id=uid(),
                severity="medium",
                pattern="llm_spam",
                description=f"Excessive LLM usage: {len(llm_calls)} calls in {window_minutes} minutes",
                events=[e.event_id for e in llm_calls],
                timestamp=datetime.utcnow(),
                metadata={"call_count": len(llm_calls)}
            )
        return None
    
    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """Get recent alerts"""
        return sorted(self.alerts, key=lambda a: a.timestamp, reverse=True)[:limit]


# Global detector instance
_detector = PatternDetector()

def get_detector() -> PatternDetector:
    """Get global pattern detector"""
    return _detector
