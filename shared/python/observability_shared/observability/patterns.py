from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List


@dataclass
class PatternAlert:
    alert_id: str
    severity: str
    pattern: str
    description: str
    timestamp: datetime
    events: List[dict]


class PatternDetector:
    """
    بسيط: يولّد تنبيهات عند وجود أحداث تحمل كلمة 'error' أو عند تجاوز عدد الأحداث خلال نافذة زمنية.
    """

    def __init__(self):
        self._alerts: List[PatternAlert] = []

    def detect(self, events):
        return self.detect_patterns(events)

    def detect_patterns(self, events, window_minutes: int = 60):
        alerts = []
        if not events:
            return alerts
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent = [e for e in events if datetime.fromisoformat(e.get("timestamp", datetime.utcnow().isoformat())) >= cutoff]

        # قاعدة 1: أحداث خطأ
        error_events = [e for e in recent if "error" in str(e.get("event_type", "")).lower() or "error" in str(e.get("payload", "")).lower()]
        if error_events:
            alert = PatternAlert(
                alert_id=f"error-{len(self._alerts)+1}",
                severity="high",
                pattern="Error Events",
                description=f"{len(error_events)} error events detected in last {window_minutes} minutes",
                timestamp=datetime.utcnow(),
                events=error_events,
            )
            alerts.append(alert)
            self._alerts.append(alert)

        # قاعدة 2: معدل أحداث مرتفع
        if len(recent) > 25:
            alert = PatternAlert(
                alert_id=f"volume-{len(self._alerts)+1}",
                severity="medium",
                pattern="High Event Volume",
                description=f"{len(recent)} events in last {window_minutes} minutes",
                timestamp=datetime.utcnow(),
                events=recent,
            )
            alerts.append(alert)
            self._alerts.append(alert)

        return alerts

    def get_recent_alerts(self, limit: int = 50):
        return self._alerts[-limit:]


def get_detector():
    return PatternDetector()
