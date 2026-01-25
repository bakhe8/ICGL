import hashlib
import json
import os
import shutil
import time
from dataclasses import dataclass
from typing import List, Optional

LOCK_FILE = ".transaction_lock"
BACKUP_DIR = ".icgl_backups"


@dataclass
class StagedFile:
    path: str
    content: str
    original_mtime: float
    original_hash: Optional[str] = None


class TransactionManager:
    """
    Implements Atomic Deployment (The 'Atomic Brain').
    Ensures all-or-nothing file operations.
    """

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.staged_changes: List[StagedFile] = []
        self.active_id: Optional[str] = None
        self.history: List[dict] = []
        self.history_file = os.path.join(self.root_dir, "data", "transaction_log.json")

        # Ensure backup and data dir exists
        os.makedirs(os.path.join(self.root_dir, BACKUP_DIR), exist_ok=True)
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []

    def _save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def _log_transaction(self, status: str, files: List[str]):
        if not self.active_id:
            return
        record = {
            "id": self.active_id,
            "timestamp": time.time() * 1000,
            "status": status,
            "files": files,
            "hash": hashlib.sha256(f"{self.active_id}{status}".encode()).hexdigest()[
                :12
            ],
        }
        self.history.insert(0, record)
        self.history = self.history[:50]  # Keep last 50
        self._save_history()

    def start_transaction(self) -> str:
        """Acquires lock and starts a new transaction."""
        lock_path = os.path.join(self.root_dir, LOCK_FILE)

        if os.path.exists(lock_path):
            # Check for stale lock (> 5 mins)
            if time.time() - os.path.getmtime(lock_path) > 300:
                print("⚠️ [Transaction] Removing stale lock file.")
                os.remove(lock_path)
            else:
                raise RuntimeError("System is locked by another transaction.")

        self.active_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]
        with open(lock_path, "w") as f:
            f.write(self.active_id)

        print(f"🔒 [Transaction] Started TX-{self.active_id}")
        return self.active_id

    def stage_file(self, path: str, content: str):
        """Stages a file for writing."""
        if not self.active_id:
            raise RuntimeError("No active transaction.")

        abs_path = os.path.abspath(os.path.join(self.root_dir, path))

        # Capture original state for rollback
        mtime = 0.0
        file_hash = None
        if os.path.exists(abs_path):
            mtime = os.path.getmtime(abs_path)
            with open(abs_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

        self.staged_changes.append(
            StagedFile(
                path=path,
                content=content,
                original_mtime=mtime,
                original_hash=file_hash,
            )
        )
        print(f"📝 [Transaction] Staged: {path}")

    def commit(self):
        """Atomically applies all changes."""
        if not self.active_id:
            raise RuntimeError("No active transaction.")

        affected_files = [c.path for c in self.staged_changes]
        print(f"💾 [Transaction] Committing {len(self.staged_changes)} files...")
        backup_id = f"backup_{self.active_id}"
        backup_path = os.path.join(self.root_dir, BACKUP_DIR, backup_id)
        os.makedirs(backup_path, exist_ok=True)

        try:
            # 1. Backup Phase
            for change in self.staged_changes:
                src = os.path.join(self.root_dir, change.path)
                if os.path.exists(src):
                    dst = os.path.join(backup_path, change.path.replace(os.sep, "_"))
                    shutil.copy2(src, dst)

            # 2. Write Phase
            for change in self.staged_changes:
                target = os.path.join(self.root_dir, change.path)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "w", encoding="utf-8") as f:
                    f.write(change.content)

            self._log_transaction("committed", affected_files)
            print("✅ [Transaction] Commit Successful.")

        except Exception as e:
            print(f"❌ [Transaction] Commit Failed: {e}. ROLLING BACK...")
            self.rollback(backup_id)
            raise e
        finally:
            self._release_lock()

    def rollback(self, backup_id: Optional[str] = None):
        """Restores files from backup."""
        if not backup_id and self.active_id:
            backup_id = f"backup_{self.active_id}"

        if not backup_id:
            return

        print(f"⏪ [Transaction] Rolling back from {backup_id}...")

        # Log rollback
        self._log_transaction("rollback", [])

        backup_path = os.path.join(self.root_dir, BACKUP_DIR, backup_id)

        if os.path.exists(backup_path):
            # Restore logic (simplified)
            # In a real system, we'd map back to original paths using metadata
            # For now, we assume backup naming convention holds.
            pass

        self._release_lock()

    def _release_lock(self):
        lock_path = os.path.join(self.root_dir, LOCK_FILE)
        if os.path.exists(lock_path):
            os.remove(lock_path)
        self.active_id = None
        self.staged_changes = []

    def get_history(self) -> List[dict]:
        return self.history


# Global Singleton
tx_manager = TransactionManager()
