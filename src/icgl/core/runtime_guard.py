"""
Runtime Integrity Guard (RIG)
-----------------------------

Ensures ICGL runs in real memory mode or aborts explicitly.
Checks:
- Exclusive ICGL lock
- Qdrant availability and lock
- Merkle chain consistency
- Writable persistence

Provides repair routine to clean stale locks and re-init Merkle safely.
"""

from __future__ import annotations
import os
import json
import atexit
from pathlib import Path
from typing import Optional, Tuple
import portalocker
from loguru import logger
from dotenv import load_dotenv

_PROCESS_LOCK_HANDLE = None
_PROCESS_LOCK_OWNER: Optional[int] = None


class RuntimeIntegrityError(RuntimeError):
    pass


class RuntimeIntegrityGuard:
    def __init__(self, db_path: str = "data/kb.db", fast_start: bool = False):
        self.base_dir = Path(db_path).parent
        self.mem_path = self.base_dir / "qdrant_memory"
        self.lock_path = self.base_dir / "icgl.lock"
        self.health_log = self.base_dir / "runtime_health.log"
        self.merkle_path = Path("data/logs/decisions.merkle")
        self._lock_handle = None
        # fast_start = True will allow deferring optional heavy checks; call run_optional_checks() later
        self.fast_start = fast_start
        self._optional_checks_ran = False

    # ----------------- Public API -----------------
    def check(self) -> None:
        """Run all runtime guards. Raises RuntimeIntegrityError on any failure."""
        self._log("RIG_START", "Starting runtime integrity guard")
        self._verify_env()
        self._acquire_process_lock()
        self._verify_paths()
        if self.fast_start:
            # Defer heavier checks to run_optional_checks to reduce startup latency
            self._log("RIG_FAST_START", "Skipping optional checks (qdrant/merkle) until run_optional_checks() is called")
        else:
            self._verify_qdrant()
            self._verify_merkle()
            self._optional_checks_ran = True
        self._log("RIG_OK", "Runtime integrity guard passed")
        atexit.register(self.release)

    def run_optional_checks(self) -> None:
        """Run deferred checks when fast_start=True."""
        if self._optional_checks_ran:
            return
        self._verify_qdrant()
        self._verify_merkle()
        self._optional_checks_ran = True

    def release(self) -> None:
        """Release process lock."""
        try:
            if self._lock_handle:
                self._lock_handle.close()
                global _PROCESS_LOCK_HANDLE, _PROCESS_LOCK_OWNER
                if self._lock_handle is _PROCESS_LOCK_HANDLE:
                    _PROCESS_LOCK_HANDLE = None
                    _PROCESS_LOCK_OWNER = None
                self._lock_handle = None
        except Exception:
            pass

    def repair(self) -> None:
        """Attempt safe repair: clear stale locks, reinit merkle, validate Qdrant."""
        self._log("RIG_REPAIR_START", "Starting runtime repair")
        self._clear_stale_icgl_lock()
        self._clear_qdrant_lock()
        self._reset_merkle()
        self._verify_qdrant()
        self._log("RIG_REPAIR_OK", "Runtime repair completed")

    # ----------------- Internal Checks -----------------
    def _acquire_process_lock(self):
        global _PROCESS_LOCK_HANDLE, _PROCESS_LOCK_OWNER
        if _PROCESS_LOCK_OWNER == os.getpid() and _PROCESS_LOCK_HANDLE:
            self._lock_handle = _PROCESS_LOCK_HANDLE
            return

        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(2):
            try:
                fh = open(self.lock_path, "w+")
                portalocker.lock(fh, portalocker.LOCK_EX | portalocker.LOCK_NB)
                fh.write(json.dumps({"pid": os.getpid()}) + "\n")
                fh.flush()
                _PROCESS_LOCK_HANDLE = fh
                _PROCESS_LOCK_OWNER = os.getpid()
                self._lock_handle = fh
                return
            except portalocker.AlreadyLocked:
                pid = self._read_pid(self.lock_path)
                if pid == os.getpid():
                    # Re-entrant in same process
                    self._lock_handle = _PROCESS_LOCK_HANDLE
                    return
                if not pid or not self._pid_alive(pid):
                    # Stale lock, clear and retry once
                    self.lock_path.unlink(missing_ok=True)
                    continue
                msg = f"ICGL lock in use at {self.lock_path} (pid={pid})."
                self._log("RIG_LOCKED", msg)
                raise RuntimeIntegrityError(msg)

    def _verify_paths(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.mem_path.mkdir(parents=True, exist_ok=True)
        test_file = self.base_dir / ".rig_write_test"
        try:
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink()
        except Exception as e:
            msg = f"Persistence not writable: {e}"
            self._log("RIG_PATH_FAIL", msg)
            raise RuntimeIntegrityError(msg)

    def _verify_env(self):
        """Ensure required runtime environment is present."""
        # Attempt to load .env from project root if not already loaded
        if "OPENAI_API_KEY" not in os.environ:
            # runtime_guard.py -> core -> icgl -> src -> project root
            project_root = Path(__file__).resolve().parents[3]
            env_path = project_root / ".env"
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            msg = "OPENAI_API_KEY missing. Governance requires real LLM access."
            self._log("RIG_ENV_FAIL", msg)
            raise RuntimeIntegrityError(msg)

    def _verify_qdrant(self):
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(path=str(self.mem_path))
            client.get_collections()
        except portalocker.AlreadyLocked:
            msg = f"Qdrant storage locked at {self.mem_path}. Stop other ICGL/Qdrant processes."
            self._log("RIG_QDRANT_LOCK", msg)
            raise RuntimeIntegrityError(msg)
        except Exception as e:
            text = str(e)
            if "already accessed by another instance of Qdrant client" in text:
                # Another client in this process/session is already holding the handle; treat as healthy
                self._log("RIG_QDRANT_REUSE", "Qdrant already active in current process; reusing existing handle.")
                return
            msg = f"Qdrant check failed: {e}"
            self._log("RIG_QDRANT_FAIL", msg)
            raise RuntimeIntegrityError(msg)

    def _verify_merkle(self):
        from .observability import SystemObserver
        obs = SystemObserver()
        ok, broken_at = obs.verify_merkle_chain()
        if not ok:
            msg = f"Merkle chain inconsistent at index {broken_at}. Run `icgl runtime repair`."
            self._log("RIG_MERKLE_FAIL", msg)
            raise RuntimeIntegrityError(msg)

    # ----------------- Helpers -----------------
    def _clear_stale_icgl_lock(self):
        if not self.lock_path.exists():
            return
        pid = self._read_pid(self.lock_path)
        if pid and self._pid_alive(pid):
            msg = f"ICGL lock held by live pid {pid}. Stop that process first."
            self._log("RIG_LOCK_HELD", msg)
            raise RuntimeIntegrityError(msg)
        self.lock_path.unlink(missing_ok=True)
        self._log("RIG_LOCK_CLEAR", "Removed stale icgl.lock")

    def _clear_qdrant_lock(self):
        lock_file = self.mem_path / ".lock"
        if lock_file.exists():
            try:
                lock_file.unlink()
                self._log("RIG_QDRANT_LOCK_CLEAR", "Removed stale qdrant .lock (ensure no other instance running)")
            except Exception as e:
                msg = f"Cannot clear Qdrant lock: {e}"
                self._log("RIG_QDRANT_LOCK_FAIL", msg)
                raise RuntimeIntegrityError(msg)

    def _reset_merkle(self):
        if self.merkle_path.exists():
            bak = self.merkle_path.with_suffix(".merkle.bak")
            if bak.exists():
                bak.unlink()
            self.merkle_path.rename(bak)
            self._log("RIG_MERKLE_RESET", f"Merkle chain reset to {bak}")

    def _read_pid(self, path: Path) -> Optional[int]:
        try:
            data = json.loads(path.read_text())
            return data.get("pid")
        except Exception:
            return None

    def _pid_alive(self, pid: int) -> bool:
        try:
            os.kill(pid, 0)
            return True
        except Exception:
            return False

    def _log(self, code: str, message: str):
        self.health_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.health_log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"code": code, "message": message}) + "\n")
        try:
            logger.info(f"[RIG] {code}: {message}")
        except Exception:
            pass
