"""
Consensus AI — Database Architect Agent
=======================================

The "Data Sovereign".
Responsible for Schema Design, Data Integrity, Migrations, and Query Performance.
"""

from typing import Any, Optional

from .base import Agent, AgentResult, AgentRole, Problem


class DatabaseArchitectAgent(Agent):
    """
    The Data Sovereign.
    Ensures that the "Memory" of the system (Data) is structured, safe, and performant.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="agent-db-architect",
            role=AgentRole.DATABASE,  # Calculated Role
            llm_provider=llm_provider,
        )
        self.specialty = "database"

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Analyzes the problem from a Data/Schema perspective.
        """
        prompt = f"""
        You are the Database Architect (The Data Sovereign).
        Your Job: Ensure Data Integrity, Schema Efficiency, and Migration Safety.
        
        Analyze the following problem:
        Title: {problem.title}
        Context: {problem.context}
        
        Constraints:
        - We use SQLite for `kb.db` and `observability.db`.
        - Logic Kernel uses JSON files (Graph Structure).
        - We apply 'Hard Realism': No loose JSON dumps if a schema can exist.
        
        Tasks:
        1. Identify any implied data structure changes.
        2. Propose SQL Schema (DDL) if new tables are needed.
        3. Flag "N+1" query risks or inefficient patterns.
        4. recommend 'Migration Strategies' if data is at risk.
        """

        analysis = await self._ask_llm(prompt, problem)

        # Heuristic checks
        recommendations = []
        concerns = []

        if (
            "migration" in problem.context.lower()
            or "schema" in problem.context.lower()
        ):
            recommendations.append(
                "Create formal migration script in backend/data/migrations"
            )

        if (
            "json" in problem.context.lower()
            and "column" not in problem.context.lower()
        ):
            concerns.append(
                "Risk of 'JSON Dumping'. Consider structured tables for queryable fields."
            )

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=recommendations,
            concerns=concerns,
            confidence=0.95,
        )
