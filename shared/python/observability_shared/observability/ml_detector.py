from datetime import datetime
from typing import Optional


class MLDetector:
    def __init__(self):
        self._models = {}
        self.sklearn_available = False
        self.trained = False
        self.training_event_count = 0
        self.last_training_time: Optional[datetime] = None
        self.detected_anomalies = []

    def detect(self, data):
        return self.detect_anomalies(data)

    def detect_anomalies(self, metrics, threshold: float = 0.8):
        # naive rule: اعتبر أي عنصر score>threshold anomaly
        anomalies = [m for m in (metrics or []) if getattr(m, "score", 0) > threshold]
        self.detected_anomalies.extend(anomalies)
        return anomalies

    def get_recent_anomalies(self, limit: int = 50):
        return self.detected_anomalies[-limit:]

    def register_model(self, name: str, model):
        self._models[name] = model

    def list_models(self):
        return list(self._models.keys())

    def train(self, events):
        # pretend to train
        self.trained = True
        self.training_event_count += len(events or [])
        self.last_training_time = datetime.utcnow()

    @property
    def hours_since_training(self) -> Optional[float]:
        if not self.last_training_time:
            return None
        delta = datetime.utcnow() - self.last_training_time
        return round(delta.total_seconds() / 3600, 2)


def get_ml_detector():
    return MLDetector()
