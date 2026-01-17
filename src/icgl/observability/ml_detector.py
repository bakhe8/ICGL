"""
ML-Based Anomaly Detection
---------------------------

Statistical machine learning for intelligent anomaly detection in agent behavior.

Approach: Isolation Forest (scikit-learn)
- Lightweight and fast
- No training data required initially
- Unsupervised learning
- Interpretable results

Features detected:
1. Channel behavior anomalies
2. Message pattern anomalies
3. Agent activity anomalies
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json

from ..observability.events import ObservabilityEvent, EventType
from ..kb.schemas import uid


class AnomalySeverity(Enum):
    """Anomaly severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Detected anomaly"""
    anomaly_id: str
    type: str  # "channel_behavior", "message_patterns", "agent_activity"
    severity: AnomalySeverity
    description: str
    event_ids: List[str]
    timestamp: datetime
    score: float  # Anomaly score (-1 to 1, lower = more anomalous)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "anomaly_id": self.anomaly_id,
            "type": self.type,
            "severity": self.severity.value,
            "description": self.description,
            "event_ids": self.event_ids,
            "timestamp": self.timestamp.isoformat(),
            "score": self.score,
            "metadata": self.metadata
        }


class MLAnomalyDetector:
    """
    ML-based anomaly detection using statistical models.
    
    Uses Isolation Forest for unsupervised anomaly detection.
    Falls back to rule-based when ML not available.
    """
    
    def __init__(self):
        self.trained = False
        self.training_event_count = 0
        self.last_training_time: Optional[datetime] = None
        self.detected_anomalies: List[Anomaly] = []
        
        # Try to import sklearn
        try:
            from sklearn.ensemble import IsolationForest
            self.sklearn_available = True
            self.models = {
                'channel_behavior': IsolationForest(
                    contamination=0.1,
                    random_state=42,
                    n_estimators=100
                ),
                'message_patterns': IsolationForest(
                    contamination=0.05,
                    random_state=42,
                    n_estimators=100
                ),
                'agent_activity': IsolationForest(
                    contamination=0.08,
                    random_state=42,
                    n_estimators=100
                )
            }
        except ImportError:
            self.sklearn_available = False
            self.models = {}
            print("⚠️ scikit-learn not available. Using rule-based fallback.")
    
    def train(self, events: List[ObservabilityEvent]) -> Dict[str, Any]:
        """
        Train ML models on historical events.
        
        Args:
            events: Historical events for training
            
        Returns:
            Training results
        """
        if not self.sklearn_available:
            return {"error": "scikit-learn not available", "fallback": "rule-based"}
        
        if len(events) < 100:
            return {"error": "Need at least 100 events", "current": len(events)}
        
        # Extract features
        features = self._extract_features(events)
        
        # Train each model
        results = {}
        for name, model in self.models.items():
            if name in features and len(features[name]) > 10:
                try:
                    import numpy as np
                    feature_array = np.array(features[name])
                    model.fit(feature_array)
                    results[name] = {"trained": True, "samples": len(feature_array)}
                except Exception as e:
                    results[name] = {"trained": False, "error": str(e)}
            else:
                results[name] = {"trained": False, "reason": "insufficient_data"}
        
        self.trained = any(r.get("trained") for r in results.values())
        self.training_event_count = len(events)
        self.last_training_time = datetime.utcnow()
        
        return {
            "trained": self.trained,
            "total_events": len(events),
            "models": results,
            "timestamp": self.last_training_time.isoformat()
        }
    
    def detect_anomalies(self, events: List[ObservabilityEvent]) -> List[Anomaly]:
        """
        Detect anomalies in recent events.
        
        Args:
            events: Recent events to analyze
            
        Returns:
            List of detected anomalies
        """
        if not events:
            return []
        
        # Use ML if available and trained
        if self.sklearn_available and self.trained:
            return self._detect_ml(events)
        else:
            return self._detect_rules(events)
    
    def _detect_ml(self, events: List[ObservabilityEvent]) -> List[Anomaly]:
        """ML-based detection using Isolation Forest"""
        import numpy as np
        
        anomalies = []
        features = self._extract_features(events)
        
        # Detect channel behavior anomalies
        if 'channel_behavior' in features and len(features['channel_behavior']) > 0:
            feature_array = np.array(features['channel_behavior'])
            predictions = self.models['channel_behavior'].predict(feature_array)
            scores = self.models['channel_behavior'].score_samples(feature_array)
            
            for idx, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:  # Anomaly detected
                    anomalies.append(Anomaly(
                        anomaly_id=uid(),
                        type="channel_behavior",
                        severity=self._score_to_severity(score),
                        description=f"Anomalous channel creation pattern detected",
                        event_ids=[features['channel_events'][idx].event_id],
                        timestamp=datetime.utcnow(),
                        score=float(score),
                        metadata={"features": feature_array[idx].tolist()}
                    ))
        
        # Detect message pattern anomalies
        if 'message_patterns' in features and len(features['message_patterns']) > 0:
            feature_array = np.array(features['message_patterns'])
            predictions = self.models['message_patterns'].predict(feature_array)
            scores = self.models['message_patterns'].score_samples(feature_array)
            
            for idx, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:
                    anomalies.append(Anomaly(
                        anomaly_id=uid(),
                        type="message_patterns",
                        severity=self._score_to_severity(score),
                        description=f"Unusual messaging behavior detected",
                        event_ids=[features['message_events'][idx].event_id],
                        timestamp=datetime.utcnow(),
                        score=float(score),
                        metadata={"features": feature_array[idx].tolist()}
                    ))
        
        # Detect agent activity anomalies
        if 'agent_activity' in features and len(features['agent_activity']) > 0:
            feature_array = np.array(features['agent_activity'])
            predictions = self.models['agent_activity'].predict(feature_array)
            scores = self.models['agent_activity'].score_samples(feature_array)
            
            for idx, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:
                    anomalies.append(Anomaly(
                        anomaly_id=uid(),
                        type="agent_activity",
                        severity=self._score_to_severity(score),
                        description=f"Abnormal agent behavior pattern",
                        event_ids=[features['agent_event_groups'][idx][0].event_id],
                        timestamp=datetime.utcnow(),
                        score=float(score),
                        metadata={
                            "agent_id": features['agent_ids'][idx],
                            "features": feature_array[idx].tolist()
                        }
                    ))
        
        self.detected_anomalies.extend(anomalies)
        return anomalies
    
    def _detect_rules(self, events: List[ObservabilityEvent]) -> List[Anomaly]:
        """Rule-based fallback detection"""
        anomalies = []
        now = datetime.utcnow()
        
        # Rule 1: Rapid channel creation
        channel_creates = [e for e in events if e.event_type == EventType.CHANNEL_CREATED]
        if len(channel_creates) > 15:
            anomalies.append(Anomaly(
                anomaly_id=uid(),
                type="channel_behavior",
                severity=AnomalySeverity.HIGH,
                description=f"Excessive channel creation: {len(channel_creates)} channels",
                event_ids=[e.event_id for e in channel_creates],
                timestamp=now,
                score=-0.8,
                metadata={"count": len(channel_creates), "method": "rule-based"}
            ))
        
        # Rule 2: High message frequency
        messages = [e for e in events if e.event_type == EventType.CHANNEL_MESSAGE]
        if messages:
            # Group by channel
            channel_msg_counts = {}
            for msg in messages:
                channel_id = msg.tags.get('channel_id') if msg.tags else None
                if channel_id:
                    channel_msg_counts[channel_id] = channel_msg_counts.get(channel_id, 0) + 1
            
            for channel_id, count in channel_msg_counts.items():
                if count > 30:
                    anomalies.append(Anomaly(
                        anomaly_id=uid(),
                        type="message_patterns",
                        severity=AnomalySeverity.MEDIUM,
                        description=f"High message frequency in channel: {count} messages",
                        event_ids=[e.event_id for e in messages if e.tags and e.tags.get('channel_id') == channel_id],
                        timestamp=now,
                        score=-0.6,
                        metadata={"channel_id": channel_id, "count": count, "method": "rule-based"}
                    ))
        
        # Rule 3: Repeated failures
        failures = [e for e in events if e.status == "failure"]
        if len(failures) > 10:
            anomalies.append(Anomaly(
                anomaly_id=uid(),
                type="agent_activity",
                severity=AnomalySeverity.HIGH,
                description=f"High failure rate: {len(failures)} failures",
                event_ids=[e.event_id for e in failures],
                timestamp=now,
                score=-0.75,
                metadata={"count": len(failures), "method": "rule-based"}
            ))
        
        self.detected_anomalies.extend(anomalies)
        return anomalies
    
    def _extract_features(self, events: List[ObservabilityEvent]) -> Dict[str, Any]:
        """Extract features from events for ML models"""
        features = {
            'channel_behavior': [],
            'message_patterns': [],
            'agent_activity': [],
            'channel_events': [],
            'message_events': [],
            'agent_event_groups': [],
            'agent_ids': []
        }
        
        # Channel behavior features
        channel_events = [e for e in events if e.event_type == EventType.CHANNEL_CREATED]
        for event in channel_events:
            features['channel_behavior'].append([
                self._time_of_day_feature(event.timestamp),
                self._day_of_week_feature(event.timestamp),
                1.0 if event.tags and event.tags.get('violation') else 0.0,
                len(str(event.input_payload)) if event.input_payload else 0
            ])
            features['channel_events'].append(event)
        
        # Message pattern features
        message_events = [e for e in events if e.event_type == EventType.CHANNEL_MESSAGE]
        for event in message_events:
            features['message_patterns'].append([
                self._time_of_day_feature(event.timestamp),
                len(str(event.input_payload)) if event.input_payload else 0,
                1.0 if event.status == "success" else 0.0,
                event.duration_ms or 0
            ])
            features['message_events'].append(event)
        
        # Agent activity features
        agents = {}
        for event in events:
            if event.actor_id not in agents:
                agents[event.actor_id] = []
            agents[event.actor_id].append(event)
        
        for agent_id, agent_events in agents.items():
            if len(agent_events) >= 3:  # Minimum events for meaningful features
                success_rate = sum(1 for e in agent_events if e.status == "success") / len(agent_events)
                avg_duration = sum(e.duration_ms or 0 for e in agent_events) / len(agent_events)
                event_diversity = len(set(e.event_type for e in agent_events)) / len(EventType)
                
                features['agent_activity'].append([
                    len(agent_events),
                    success_rate,
                    avg_duration,
                    event_diversity
                ])
                features['agent_event_groups'].append(agent_events)
                features['agent_ids'].append(agent_id)
        
        return features
    
    def _time_of_day_feature(self, timestamp: datetime) -> float:
        """Convert timestamp to time-of-day feature (0-1)"""
        return timestamp.hour / 24.0
    
    def _day_of_week_feature(self, timestamp: datetime) -> float:
        """Convert timestamp to day-of-week feature (0-1)"""
        return timestamp.weekday() / 7.0
    
    def _score_to_severity(self, score: float) -> AnomalySeverity:
        """Convert anomaly score to severity level"""
        if score < -0.5:
            return AnomalySeverity.CRITICAL
        elif score < -0.3:
            return AnomalySeverity.HIGH
        elif score < -0.1:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    def get_recent_anomalies(self, limit: int = 20) -> List[Anomaly]:
        """Get recent detected anomalies"""
        return sorted(
            self.detected_anomalies,
            key=lambda a: a.timestamp,
            reverse=True
        )[:limit]
    
    def hours_since_training(self) -> float:
        """Hours since last training"""
        if not self.last_training_time:
            return float('inf')
        return (datetime.utcnow() - self.last_training_time).total_seconds() / 3600


# Global detector instance
_ml_detector = MLAnomalyDetector()

def get_ml_detector() -> MLAnomalyDetector:
    """Get global ML detector instance"""
    return _ml_detector
