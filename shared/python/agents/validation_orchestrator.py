from typing import Any, Optional

from shared.python.agents.base import Agent, AgentResult, AgentRole, Problem


class ValidationOrchestratorAgent(Agent):
    """
    The Validation Orchestrator.
    Synthesizes results from TestingAgent and VerificationAgent
    to provide a final Quality Gate clearance.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="validation-orchestrator",
            role=AgentRole.VALIDATION_ORCHESTRATOR,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # Consult testing and verification peers
        testing_res = await self.consult_peer(
            AgentRole.TESTING, problem.title, problem.context, kb
        )
        verification_res = await self.consult_peer(
            AgentRole.VERIFICATION, problem.title, problem.context, kb
        )

        prompt = f"""
        You are the Validation Orchestrator (The Final Gatekeeper).
        Your Job: Determine if the code/proposal is truly ready for deployment.
        
        Testing Results: {testing_res.analysis if testing_res else "No testing data"}
        Verification Results: {verification_res.analysis if verification_res else "No verification data"}
        
        Decision Criteria:
        1. 100% Syntax pass.
        2. Policy alignment.
        3. No major regression risks detected by Testing.
        """

        analysis = await self._ask_llm(prompt, problem)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            confidence=0.99,
            recommendations=["Pass Quality Gate", "Verify logs post-deploy"],
            metadata={"gate_status": "final_validation"},
        )
