from typing import Any, List, Optional

from .base import Agent, AgentResult, AgentRole, FileChange, Problem


class ExecutiveAgent(Agent):
    """
    ExecutiveAgent: The Sovereign Human Bridge.
    Implements Inverse Governance via the 'Confirmation Mirror'.
    Ensures no physical action is taken without explicit human signing.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="executive-bridge",
            role=AgentRole.EXECUTIVE,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Main deliberation loop for the Executive Agent.
        """
        # Phase 1: Confirmation Mirror (Inverse Governance)
        # We ask the LLM to summarize what it thinks the user wants.

        prompt = f"""
        You are the EXECUTIVE AGENT, the primary bridge between the HUMAN OWNER and the ICGL.
        
        Current Request: {problem.title}
        Context: {problem.context}
        
        YOUR OBJECTIVES:
        1. **Confirmation Mirror**: Paraphrase the user's request to ensure you understood it perfectly. 
           Say: "I understood that you want to [paraphrase]. Is this correct?"
        2. **Proposed Actions**: List exactly what you intend to do if confirmed.
        3. **Sentinel Check**: State that you will defer to the Sentinel and Security Orchestrator for safety.

        Output your analysis in a conversational but professional tone.
        """

        analysis_text = await self._ask_llm(prompt, problem)

        # In a real scenario, we'd extract specific file changes if the user confirmed.
        # For now, we return a result that flags 'clarity_needed' to pause for human.

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis_text,
            confidence=0.99,
            clarity_needed=True,
            clarity_question="هل هذا الفهم صحيح؟ (Is this understanding correct?)",
            recommendations=[
                "Awaiting owner confirmation",
                "Queue actions for signing",
            ],
            metadata={"phase": "inverse_governance_mirror"},
        )

    async def generate_action_queue(
        self, confirmed_problem: Problem
    ) -> List[FileChange]:
        """
        Generates a list of actions (file changes/commands) for the user to sign.
        """
        # This would normally be a call to Builder/Engineer or a targeted LLM prompt.
        # Mocking for Phase 9 initialization.
        return [
            FileChange(
                path="icgl_sovereign_intent.md",
                content="# Sovereign Intent\nConfirmed by Owner.",
            ),
        ]
