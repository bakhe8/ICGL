"""
ICGL Observability Layer
========================

"The Eyes of the System."
Handles recording of:
- Intervention Logs (Human vs Machine disagreement)
- Agent Metrics (Performance/Stability)
- Merkle Sovereign Ledger

All persistence is now unified within the Knowledge Base (kb.db).
"""

import hashlib
import json
from typing import Optional

from src.core.kb.schemas import AgentMetric, InterventionLog, now, uid


class SystemObserver:
    """
    Observer for the ICGL system.
    Delegates all persistence to the PersistentKnowledgeBase.
    """

    def __init__(self, kb=None):
        self.kb = kb
        # If kb is not provided, it will be injected or accessed via ICGL singleton
        self._prev_hash: Optional[str] = None

    def _ensure_kb(self):
        if self.kb is None:
            from src.api.deps import get_icgl

            try:
                engine = get_icgl()
                self.kb = engine.kb
            except Exception:
                # Fallback or error if engine not booted
                # In some CLI/harness contexts, we might need a manual KB
                pass

        if self.kb is None:
            raise RuntimeError("SystemObserver: No Knowledge Base (kb) available for persistence.")

    def record_intervention(
        self, adr_id: str, original_rec: str, action: str, reason: str, diff_summary: Optional[str] = None
    ):
        """
        Log a human intervention.
        """
        self._ensure_kb()

        log = InterventionLog(
            id=uid(),
            adr_id=adr_id,
            original_recommendation=original_rec,
            human_action=action,  # type: ignore
            reason=reason,
            diff_summary=diff_summary,
            timestamp=now(),
        )
        self.kb.add_intervention(log)
        print(f"   👁️ Observed Intervention: [{action}] on {adr_id}. Reason: {reason}")

    def record_metric(
        self,
        agent_id: str,
        role: str,
        latency: float,
        confidence: float,
        success: bool = True,
        error_code: Optional[str] = None,
        task_type: str = "analysis",
    ):
        """
        Log an agent performance metric.
        """
        self._ensure_kb()
        metric = AgentMetric(
            agent_id=agent_id,
            role=role,
            task_type=task_type,
            latency_ms=latency,
            confidence_score=confidence,
            success=success,
            error_code=error_code,
            timestamp=now(),
        )
        self.kb.add_agent_metric(metric)

    def record_decision(self, decision_record: dict):
        """
        Append a signed decision record and update Merkle ledger in DB.
        This is thread-safe for SQLite as it fetches the latest state from DB.
        """
        self._ensure_kb()

        # 1. Always get the latest hash from DB to ensure chain integrity under concurrency
        ledger = self.kb.get_merkle_ledger()
        if ledger:
            prev_hash = ledger[-1]["node_hash"]
        else:
            prev_hash = ""  # Genesis starts with empty string as prev

        # 2. Compute new hash
        payload = json.dumps(decision_record, sort_keys=True)
        h = hashlib.sha256((prev_hash + payload).encode("utf-8")).hexdigest()

        # 3. Persist to DB
        ts = now()
        self.kb.record_decision_ledger(h, prev_hash, payload, ts)

        # 4. Update memory cache (optional UI hint)
        self._prev_hash = h
        return h

    def verify_merkle_chain(self) -> tuple[bool, int]:
        """
        Verify Merkle-like chain integrity from the database.
        Returns (is_valid, broken_index).
        """
        self._ensure_kb()
        ledger = self.kb.get_merkle_ledger()

        if not ledger:
            return True, -1

        prev_hash = ""
        for idx, node in enumerate(ledger):
            stored_hash = node["node_hash"]
            stored_prev = node["prev_hash"]
            payload = node["payload"]

            if stored_prev != prev_hash:
                return False, idx

            recomputed = hashlib.sha256((prev_hash + payload).encode("utf-8")).hexdigest()
            if stored_hash != recomputed:
                return False, idx

            prev_hash = stored_hash

        return True, -1
