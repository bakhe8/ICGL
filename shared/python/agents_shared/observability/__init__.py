from .broadcaster import Broadcaster
from .events import EventType
from .graph import TraceGraphBuilder
from .ml_detector import MLDetector
from .patterns import PatternDetector
from .storage import SQLiteLedger

# Module-level singletons
# Legacy shim class removed - using persistent storage directly.
_ledger_instance = SQLiteLedger("data/observability.db")
_broadcaster = Broadcaster()
_detector = PatternDetector()
_ml_detector = MLDetector()


def init_observability(db_path: str) -> None:
    # No-op for now; keep API compatibility
    return None


def get_ledger() -> SQLiteLedger:
    return _ledger_instance


def get_broadcaster() -> Broadcaster:
    return _broadcaster


def get_detector() -> PatternDetector:
    return _detector


def get_ml_detector() -> MLDetector:
    return _ml_detector


__all__ = [
    "Broadcaster",
    "EventType",
    "TraceGraphBuilder",
    "MLDetector",
    "PatternDetector",
    "SQLiteLedger",
    "init_observability",
    "get_ledger",
    "get_broadcaster",
    "get_detector",
    "get_ml_detector",
]
