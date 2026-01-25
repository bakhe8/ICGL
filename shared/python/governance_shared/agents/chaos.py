"""
Consensus AI — Chaos Agent (The Red Team)
=========================================

"To build a resilient system, one must try to break it."

Roles:
1. Devil's Advocate: Challenges groupthink and consensus.
2. Stress Tester: Simulates high load or edge cases (Theoretically).
3. Security Red Teaming: Identifies vulnerabilities.

SAFEGUARDS:
- By default, runs in SIMULATION_MODE.
- Cannot execute write operations (DELETE, DROP) directly.
- Must be explicitly invited by the Sentinel.
"""

from typing import Any, Optional

from .base import Agent, AgentResult, AgentRole, Problem


class ChaosAgent(Agent):
    """
    The Chaos Agent / Red Team.
    Operates under strict rules of engagement to ensure system safety.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="agent-chaos",
            role=AgentRole.CHAOS,
            llm_provider=llm_provider,
        )
        self.specialty = "red_teaming"
        self.simulation_mode = True  # HARCODED SAFETY LOCK

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Attacks the problem logic to find weaknesses.
        """
        prompt = f"""
        You are the Chaos Agent (Red Team).
        Your Goal: Break the proposed logic. Find the flaw everyone else missed.
        
        Analyze:
        Title: {problem.title}
        Context: {problem.context}
        
        Directives (SIMULATION MODE ACTIVE):
        1. DO NOT suggest "fixing" the code.
        2. DO suggest "exploiting" it. (e.g., "If I send -1 tokens, does it crash?")
        3. Challenge assumptions: "Why do we trust the user input here?"
        4. Identify "Groupthink": If everyone agrees, be the dissenter.
        
        Output:
        - A list of 'Theoretical Attacks'.
        - A 'Fragility Score' (1-100).
        """

        analysis = await self._ask_llm(prompt, problem)

        # Self-Monitoring: Ensure we declare this is a SIMULATION
        analysis = f"⚠️ [RED TEAM SIMULATION]\n{analysis}"

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                "Review vulnerability report",
                "Add regression test for identified edge case",
            ],
            concerns=["Detailed attack vectors listed in analysis"],
            confidence=0.5,  # Always low confidence in "safety" to force review
        )
