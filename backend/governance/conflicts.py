import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

CONFLICTS_DB_FILE = "data/conflicts.json"


class ConflictRegistry:
    """
    Manages system conflicts (persisted to JSON).
    Replaces in-memory mock lists.
    """

    def __init__(self):
        self._ensure_db()
        self.conflicts = self._load()

    def _ensure_db(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(CONFLICTS_DB_FILE):
            with open(CONFLICTS_DB_FILE, "w") as f:
                json.dump([], f)

    def _load(self) -> List[Dict]:
        try:
            with open(CONFLICTS_DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self):
        with open(CONFLICTS_DB_FILE, "w") as f:
            json.dump(self.conflicts, f, indent=2)

    def list_conflicts(self) -> List[Dict]:
        return self.conflicts

    def get_conflict(self, conflict_id: str) -> Optional[Dict]:
        for c in self.conflicts:
            if c["id"] == conflict_id:
                return c
        return None

    def create_conflict(
        self,
        title: str,
        description: str,
        severity: str = "medium",
        detected_by: str = "system",
    ) -> Dict:
        new_conflict = {
            "id": f"con-{str(uuid.uuid4())[:8]}",
            "title": title,
            "description": description,
            "severity": severity,
            "status": "open",
            "detected_by": detected_by,
            "created_at": datetime.now().isoformat(),
            "resolution": None,
        }
        self.conflicts.append(new_conflict)
        self._save()
        return new_conflict

    def resolve_conflict(
        self, conflict_id: str, resolution: str, resolved_by: str
    ) -> Optional[Dict]:
        for c in self.conflicts:
            if c["id"] == conflict_id:
                c["status"] = "resolved"
                c["resolution"] = resolution
                c["resolved_by"] = resolved_by
                c["resolved_at"] = datetime.now().isoformat()
                self._save()
                return c
        return None


# Global Singleton
conflict_registry = ConflictRegistry()
