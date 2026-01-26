import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

QUEUE_FILE = "data/signing_queue.json"


class SigningQueue:
    """
    Manages the 'Action Signing Queue' for the Executive Agent.
    Persists pending actions that require human sovereignty.
    """

    def __init__(self):
        self._ensure_db()
        self.queue = self._load()

    def _ensure_db(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load(self) -> List[Dict]:
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self):
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.queue, f, indent=2, ensure_ascii=False)

    def add_to_queue(
        self,
        title: str,
        description: str,
        actions: List[Dict],
        agent_id: str,
        risk_level: str = "HIGH",
    ) -> Dict:
        item = {
            "id": f"sign-{str(uuid.uuid4())[:8]}",
            "title": title,
            "description": description,
            "actions": actions,  # Serialized actions/file changes
            "agent_id": agent_id,
            "risk_level": risk_level,
            "status": "PENDING",  # PENDING, SIGNED, REJECTED
            "created_at": datetime.now().isoformat(),
            "signed_at": None,
            "signed_by": None,
        }
        self.queue.append(item)
        self._save()
        return item

    def get_pending(self) -> List[Dict]:
        return [q for q in self.queue if q["status"] == "PENDING"]

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Returns recently processed items (SIGNED/REJECTED)."""
        history = [q for q in self.queue if q["status"] != "PENDING"]
        # Sort by signed_at descending (newest first)
        history.sort(key=lambda x: x.get("signed_at") or "", reverse=True)
        return history[:limit]

    def sign_off(self, item_id: str, human_id: str) -> Optional[Dict]:
        for q in self.queue:
            if q["id"] == item_id and q["status"] == "PENDING":
                q["status"] = "SIGNED"
                q["signed_by"] = human_id
                q["signed_at"] = datetime.now().isoformat()
                self._save()
                return q
        return None

    def reject(self, item_id: str, human_id: str) -> Optional[Dict]:
        for q in self.queue:
            if q["id"] == item_id and q["status"] == "PENDING":
                q["status"] = "REJECTED"
                q["signed_by"] = human_id
                q["signed_at"] = datetime.now().isoformat()
                self._save()
                return q
        return None


# Global Singleton
signing_queue = SigningQueue()
