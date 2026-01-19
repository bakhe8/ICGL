"""
ICGL Observability Layer
========================

"The Eyes of the System."
Handles recording of:
- Intervention Logs (Human vs Machine disagreement)
- Agent Metrics (Performance/Stability)

This meta-data is used by Cycle 4+ agents to optimize the system.
"""

import json
import os
from pathlib import Path
from dataclasses import asdict
from kb.schemas import InterventionLog, AgentMetric, uid, now

class SystemObserver:
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.intervention_file = self.log_dir / "interventions.jsonl"
        self.metrics_file = self.log_dir / "agent_metrics.jsonl"
        self.decision_log = self.log_dir / "decisions.log"
        self.merkle_log = self.log_dir / "decisions.merkle"

    def record_intervention(self, adr_id: str, original_rec: str, action: str, reason: str):
        """
        Log a human intervention.
        """
        log = InterventionLog(
            id=uid(),
            adr_id=adr_id,
            original_recommendation=original_rec,
            human_action=action,
            reason=reason
        )
        self._append_jsonl(self.intervention_file, log)
        print(f"   👁️ Observed Intervention: [{action}] on {adr_id}. Reason: {reason}")

    def record_metric(self, agent_id: str, role: str, latency: float, confidence: float, success: bool = True, error_code: str = None):
        """
        Log an agent performance metric.
        """
        metric = AgentMetric(
            agent_id=agent_id,
            role=role,
            task_type="analysis",
            latency_ms=latency,
            confidence_score=confidence,
            success=success,
            error_code=error_code
        )
        self._append_jsonl(self.metrics_file, metric)

    def record_decision(self, decision_record: dict):
        """
        Append a signed decision record and update Merkle chain.
        """
        # Append decision JSON line
        self._append_jsonl(self.decision_log, decision_record)
        # Update Merkle chain
        new_hash = self._update_merkle(decision_record)
        return new_hash

    def _append_jsonl(self, path: Path, entity):
        """Helper to append dataclass or dict as JSON line."""
        from dataclasses import is_dataclass
        payload = asdict(entity) if is_dataclass(entity) else entity
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

    def verify_merkle_chain(self) -> tuple[bool, int]:
        """
        Verify Merkle-like chain integrity.
        Returns (is_valid, broken_index).
        """
        if not self.merkle_log.exists():
            return True, -1
        import hashlib
        lines = self.merkle_log.read_text(encoding="utf-8").splitlines()
        prev_hash = ""
        for idx, line in enumerate(lines):
            try:
                stored_hash, stored_prev, payload = line.split(",", 2)
            except ValueError:
                return False, idx
            if stored_prev != prev_hash:
                return False, idx
            recomputed = hashlib.sha256((prev_hash + payload).encode("utf-8")).hexdigest()
            if stored_hash != recomputed:
                return False, idx
            prev_hash = stored_hash
        return True, -1

    def _update_merkle(self, record: dict) -> str:
        """
        Very lightweight Merkle-like chaining: hash(prev_hash + json(record)).
        """
        import hashlib
        prev_hash = ""
        if self.merkle_log.exists():
            last = self.merkle_log.read_text(encoding="utf-8").splitlines()
            prev_hash = last[-1].split(",")[0] if last else ""
        payload = json.dumps(record, sort_keys=True)
        h = hashlib.sha256((prev_hash + payload).encode("utf-8")).hexdigest()
        with open(self.merkle_log, "a", encoding="utf-8") as f:
            f.write(f"{h},{prev_hash},{payload}\n")
        return h
