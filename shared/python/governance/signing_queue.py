"""
ICGL Governance — Signing Queue
==============================

Handles human-in-the-loop approval workflows (HDAL).
"""

import datetime
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SigningRequest:
    request_id: str
    proposed_by: str
    content: Dict[str, Any]
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    status: str = "pending"  # pending, approved, rejected


class SigningQueue:
    def __init__(self):
        self._queue: List[SigningRequest] = []

    def push(self, request: SigningRequest):
        self._queue.append(request)

    def list_pending(self) -> List[SigningRequest]:
        return [r for r in self._queue if r.status == "pending"]

    def add_to_queue(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        req_id = f"SIGN-{uuid.uuid4().hex[:8]}"
        self._queue.append(
            SigningRequest(
                request_id=req_id, proposed_by="System", content={"title": title, "description": description}
            )
        )
        return {"id": req_id, "status": "QUEUED"}

    def approve(self, request_id: str):
        for r in self._queue:
            if r.request_id == request_id:
                r.status = "approved"


signing_queue = SigningQueue()
