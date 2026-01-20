from typing import List, Dict, Any
from .base import Agent, AgentResult, Problem, AgentRole
from agents.hr_agent import HRAgent


class HRProxyAgent(Agent):
    """
    HR Proxy Agent
    --------------
    Wraps the existing HRAgent to operate within the Agent interface.
    Focus: records and role definitions; no mock behaviors.
    """

    def __init__(self, agent_id: str = "agent-hr"):
        super().__init__(agent_id=agent_id, role=AgentRole.HR)
        self.hr_core = HRAgent()

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """Provide a snapshot of HR records and any gaps using real KB data when available."""
        # Load latest HR records from persisted store if available
        try:
            from pathlib import Path
            import json
            store = Path(__file__).resolve().parents[3] / "data" / "hr_records.json"
            if store.exists():
                self.hr_core.records = json.loads(store.read_text(encoding="utf-8"))
        except Exception:
            pass

        record_count = len(self.hr_core.records)
        decisions = getattr(kb, "human_decisions", []) or []
        signers = sorted({d.signed_by for d in decisions if getattr(d, "signed_by", None)})
        analysis_parts: List[str] = []
        analysis_parts.append(f"HR review · context: {problem.title}")
        analysis_parts.append(f"Tracked HR records: {record_count}")
        analysis_parts.append(f"Recorded decisions: {len(decisions)}")
        if signers:
            analysis_parts.append(f"Signers on record: {', '.join(signers)}")

        concerns: List[str] = []
        if record_count == 0:
            concerns.append("No HR records available")
        if not decisions:
            concerns.append("No signed decisions available for role validation")

        recs: List[str] = []
        if record_count == 0:
            recs.append("Add initial HR records (roles, duties, limits)")
        else:
            recs.append("Validate role definitions against current policies")
        if decisions and record_count:
            recs.append("Cross-check signers vs. allowed roles in HR registry")

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis="\n".join(analysis_parts),
            recommendations=recs,
            concerns=concerns,
            references=[
                f"decisions={len(decisions)}",
                f"signers={', '.join(signers) if signers else 'none'}",
            ],
            confidence=1.0 if record_count > 0 else 0.5,
        )

    # Convenience methods to update HR data (invoked via API/controller, not autonomous)
    def add_record(self, record: Dict[str, Any]) -> str:
        return self.hr_core.update_record(record)
