import threading
from typing import Optional

from backend.governance import ICGL
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

_icgl_instance: Optional[ICGL] = None
_icgl_lock = threading.Lock()


def get_icgl() -> ICGL:
    """Get or create the ICGL engine singleton (thread-safe)."""
    global _icgl_instance
    if _icgl_instance is None:
        with _icgl_lock:
            if _icgl_instance is None:
                _icgl_instance = ICGL()
    return _icgl_instance
