import threading
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from shared.python.core.runtime_guard import RuntimeIntegrityGuard
from shared.python.governance.icgl import ICGL
from shared.python.utils.logging_config import get_logger

# 1. 🔴 MANDATORY: Load Environment FIRST
BASE_DIR = Path(__file__).parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

logger = get_logger(__name__)

# --- Global Engine Singleton ---
_icgl_instance: Optional[ICGL] = None
_icgl_lock = threading.Lock()


def get_icgl() -> ICGL:
    """Get or create the ICGL engine singleton (thread-safe)."""
    global _icgl_instance
    if _icgl_instance is None:
        with _icgl_lock:
            if _icgl_instance is None:
                logger.info("🚀 Booting ICGL Engine Singleton (from deps)...")
                try:
                    # Initialize Observability FIRST
                    from shared.python.observability import init_observability

                    obs_db_path = BASE_DIR / "data" / "observability.db"
                    init_observability(str(obs_db_path))
                    logger.info("📊 Observability Ledger Initialized")

                    # Runtime integrity check
                    rig = RuntimeIntegrityGuard()
                    rig.check()

                    # Boot ICGL
                    _icgl_instance = ICGL(db_path=str(BASE_DIR / "data" / "kb.db"))
                    logger.info("✅ Engine Booted Successfully.")
                except Exception as e:
                    logger.critical(f"❌ Engine Boot Failed: {e}", exc_info=True)
                    raise RuntimeError(f"Engine Failure: {e}")
    return _icgl_instance
