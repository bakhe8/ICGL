"""
ICGL Governance — Signing Queue
==============================

Handles human-in-the-loop approval workflows (HDAL).
"""

from typing import Any, Dict, List

from src.core.kb.schemas import SigningRequest, now, uid


class SigningQueue:
    """
    Handles human-in-the-loop approval workflows (HDAL) with persistence.
    """

    def __init__(self, kb=None):
        self.kb = kb

    def _ensure_kb(self):
        if self.kb is None:
            from src.api.deps import get_icgl

            self.kb = get_icgl().kb

    def list_pending(self) -> List[SigningRequest]:
        self._ensure_kb()
        return [r for r in self.kb.signing_requests.values() if r.status == "pending"]

    def add_to_queue(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        self._ensure_kb()
        req_id = f"SIGN-{uid()[:8]}"
        request = SigningRequest(
            id=req_id,
            adr_id=kwargs.get("adr_id"),
            title=title,
            description=description,
            proposed_by=kwargs.get("proposed_by", "System"),
            status="pending",
            risk_level=kwargs.get("risk_level", "MEDIUM"),
            actions=kwargs.get("actions", []),
            timestamp=now(),
        )
        self.kb.add_signing_request(request)
        return {"id": req_id, "status": "QUEUED"}

    def approve(self, request_id: str):
        self._ensure_kb()
        request = self.kb.get_signing_request(request_id)
        if request:
            request.status = "approved"
            self.kb.add_signing_request(request)  # Persist update

    def reject(self, request_id: str):
        self._ensure_kb()
        request = self.kb.get_signing_request(request_id)
        if request:
            request.status = "rejected"
            self.kb.add_signing_request(request)  # Persist update


signing_queue = SigningQueue()
