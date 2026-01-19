from typing import Optional, List, Dict, Any
from .base import Agent, AgentResult, Problem, AgentRole
from hr_agent import HRAgent


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
        """Provide a snapshot of HR records and any gaps."""
        record_count = len(self.hr_core.records)
        analysis = f"HR review: {record_count} records tracked. Context: {problem.title}"
        concerns: List[str] = []
        if record_count == 0:
            concerns.append("No HR records available")
        recs: List[str] = []
        if record_count == 0:
            recs.append("Add initial HR records (roles, duties, limits)")
        else:
            recs.append("Validate role definitions against current policies")

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=recs,
            concerns=concerns,
            confidence=1.0 if record_count > 0 else 0.5,
        )

    # Convenience methods to update HR data (invoked via API/controller, not autonomous)
    def add_record(self, record: Dict[str, Any]) -> str:
        return self.hr_core.update_record(record)
