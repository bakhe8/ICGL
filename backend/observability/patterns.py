# Stub for patterns
class PatternDetector:
    def __init__(self):
        self._alerts = []

    def detect(self, data):
        return []

    def get_recent_alerts(self, limit: int = 50):
        return self._alerts[-limit:]

    def detect_patterns(self, events, window_minutes: int = 60):
        return []

def get_detector():
    return PatternDetector()
