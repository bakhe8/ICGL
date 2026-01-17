"""
Consensus AI — Concept Guardian
================================

Protects semantic integrity of concepts.
Prevents "Definition Drift".
"""

from .base import Agent, AgentRole, Problem, AgentResult


class ConceptGuardian(Agent):
    """
    Concept integrity agent.
    Ensures no implicit redefinition of terms.
    Reference: P-GOV-09
    """
    
    def __init__(self):
        super().__init__(agent_id="agent-guardian", role=AgentRole.GUARDIAN)
        
    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # 1. Recall Relevant Concepts
        recalled_concepts = await self.recall(f"Concepts related to {problem.title}", limit=5)
        
        # 2. Build Context
        context = f"Proposal: {problem.title}\nContext: {problem.context}\n"
        if recalled_concepts:
            context += "\nRelevant Concepts (from Knowledge Base):\n"
            for c in recalled_concepts:
                context += f"- {c}\n"
        
        # 3. Query LLM
        prompt = (
            f"Analyze the following proposal for semantic integrity.\n\n"
            f"{context}\n\n"
            f"Does this proposal redefine existing concepts? Does it introduce 'Definition Drift'?"
        )
        
        system_prompt = (
            "You are the Concept Guardian. Your mission is to protect the shared language of the system. "
            "Ensure that terms like 'Context', 'ADR', and 'Memory' are used consistently with the KB. "
            "Reject any proposal that redefines terms in a way that creates confusion."
        )
        
        raw_analysis = await self._ask_llm(prompt, system_prompt=system_prompt)
        
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=raw_analysis,
            recommendations=["Verify term usage against kb show concepts"],
            concerns=[],
            confidence=0.9
        )
