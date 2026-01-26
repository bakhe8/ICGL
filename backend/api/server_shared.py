import threading
from typing import Any, Optional

<<<<<<< HEAD:api/server_shared.py
from modules.governance.icgl import ICGL
from modules.utils.logging_config import get_logger
=======
from shared.python.governance_shared.governance.icgl import ICGL
from shared.python.utils_shared.utils.logging_config import get_logger
>>>>>>> 1017ee5d6165b6b836bcf8f4a86dd3b8c5d9a8a4:backend/api/server_shared.py

logger = get_logger(__name__)

# --- Global Singletons ---
_icgl_instance: Optional[ICGL] = None
_channel_router: Any = None
_icgl_lock = threading.Lock()


def get_icgl() -> ICGL:
    """Get or create the ICGL engine singleton (thread-safe)."""
    global _icgl_instance
    if _icgl_instance is None:
        with _icgl_lock:
            if _icgl_instance is None:
                logger.info("🚀 Booting ICGL Engine Singleton...")
                try:
                    # Initialize Observability (Deferred imports to avoid cycles)
                    from pathlib import Path

<<<<<<< HEAD:api/server_shared.py
                    from modules.observability import init_observability
=======
                    from shared.python.observability_shared.observability import init_observability
>>>>>>> 1017ee5d6165b6b836bcf8f4a86dd3b8c5d9a8a4:backend/api/server_shared.py

                    base_dir = Path(__file__).resolve().parent.parent
                    obs_db_path = base_dir / "data" / "observability.db"
                    init_observability(str(obs_db_path))

                    _icgl_instance = ICGL()

                    # Initialize Router
                    from backend.coordination.router import DirectChannelRouter

                    global _channel_router
                    _channel_router = DirectChannelRouter(
                        icgl_provider=lambda: _icgl_instance
                    )
                    _icgl_instance.registry.set_router(_channel_router)

                    logger.info("✅ Engine Booted Successfully.")
                except Exception as e:
                    logger.critical(f"❌ Engine Boot Failed: {e}", exc_info=True)
                    raise RuntimeError(f"Engine Failure: {e}")
    return _icgl_instance


def get_channel_router():
    """Get the global channel router instance"""
    get_icgl()
    return _channel_router
