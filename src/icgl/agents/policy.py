"""
Consensus AI — Policy Agent
============================

Checks compliance with all system policies (Rule of Law).
"""

from .base import Agent, AgentRole, Problem, AgentResult


class PolicyAgent(Agent):
    """
    Policy compliance agent.
    Verifies proposal against P-* policies.
    """
    
    def __init__(self):
        super().__init__(agent_id="agent-policy", role=AgentRole.POLICY)
        
    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # 1. Recall Relevant Policies from Memory
        recalled_policies = await self.recall(f"Policies regarding {problem.title} {problem.context}", limit=5)
        
        # 2. Build Context
        context = f"Proposal: {problem.title}\nContext: {problem.context}\n"
        if recalled_policies:
            context += "\nRelevant Governing Policies (from Knowledge Base):\n"
            for p in recalled_policies:
                context += f"- {p}\n"
        
        # 3. Query LLM
        prompt = (
            f"Compare the following proposal against our Governing Policies.\n\n"
            f"{context}\n\n"
            f"Identify any violations, risks, or required alignment actions."
        )
        
        system_prompt = (
            "You are the Policy Enforcement Agent. Your role is strictly to ensure the Rule of Law. "
            "Evaluate proposals against stated policies. If a proposal violates a policy, flag it as a CRITICAL concern. "
            "Provide a reasoned 'Insha'a' (composition) explaining the alignment or lack thereof."
        )
        
        raw_analysis = await self._ask_llm(prompt, system_prompt=system_prompt)
        
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=raw_analysis,
            recommendations=["Ensure proposal explicitly references policy codes"],
            concerns=[], # Concerns will be buried in the analysis text for now
            confidence=0.9
        )
