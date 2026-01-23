from .graph import TraceGraphBuilder
from .events import EventType
from .broadcaster import Broadcaster
from .patterns import PatternDetector
from .ml_detector import MLDetector
from datetime import datetime
from typing import Optional

# Simple in-memory ledger shim to satisfy server expectations
class _Ledger:
    def __init__(self):
        self._traces = {}
        self._events = []

    def get_stats(self):
        return {
            "trace_count": len(self._traces),
            "event_count": len(self._events),
        }

    def get_recent_traces(self, limit: int = 50):
        keys = list(self._traces.keys())[-limit:]
        return [self._traces[k] for k in keys]

    def get_trace(self, trace_id: str):
        return self._traces.get(trace_id, [])

    def log(self, event_type, user_id: str, trace_id: str, input_payload: Optional[dict] = None):
        entry = {
            "event_type": getattr(event_type, "value", str(event_type)),
            "user_id": user_id,
            "trace_id": trace_id,
            "payload": input_payload or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._events.append(entry)
        try:
            _broadcaster.broadcast_nowait(entry)
        except Exception:
            pass
        return entry

    def query_events(self, trace_id=None, session_id=None, adr_id=None, event_type=None, limit=100):
        # naive filter
        results = []
        for e in self._events:
            if trace_id and e.get("trace_id") != trace_id:
                continue
            if session_id and e.get("session_id") != session_id:
                continue
            if adr_id and e.get("adr_id") != adr_id:
                continue
            results.append(e)
            if len(results) >= limit:
                break
        return results


# Module-level singletons
_ledger_instance: _Ledger = _Ledger()
_broadcaster = Broadcaster()
_detector = PatternDetector()
_ml_detector = MLDetector()


def init_observability(db_path: str) -> None:
    # No-op for now; keep API compatibility
    return None


def get_ledger() -> _Ledger:
    return _ledger_instance


def get_broadcaster() -> Broadcaster:
    return _broadcaster


def get_detector() -> PatternDetector:
    return _detector


def get_ml_detector() -> MLDetector:
    return _ml_detector
