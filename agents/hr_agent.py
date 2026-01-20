"""
HR Agent — ICGL
---------------
Agent responsible for updating and generating responsibility documents for all agents and departments.
"""

from typing import List, Dict, Optional
from agents.base import Agent, AgentRole, Problem, AgentResult

class HRAgent(Agent):
    def __init__(self):
        super().__init__(agent_id="agent-hr", role=AgentRole.HR)
        self.records = []  # List of agent/department records

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        HR Analysis Logic.
        """
        # Simple mock logic for now or specific HR logic
        analysis = f"HR Analysis for: {problem.title}\nContext: {problem.context}\n"
        analysis += "Reviewing responsibility allocation and team structure."
        
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=["Update responsibility matrix", "Verify role definitions"],
            concerns=[],
            confidence=0.9
        )

    def update_record(self, record: Dict):
        self.records.append(record)
        return f"Record updated for: {record.get('name', 'Unknown')}"

    def generate_responsibility_docs(self) -> List[Dict]:
        return [
            {"name": r.get("name"), "role": r.get("role"), "duties": r.get("duties"), "limits": r.get("limits")} for r in self.records
        ]
