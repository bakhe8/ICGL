"""
Consensus AI — Policy Agent
============================

Checks compliance with all system policies (Rule of Law).
"""

from shared.python.agents.base import Agent, AgentResult, AgentRole, Problem
from shared.python.llm.client import LLMClient, LLMConfig


class PolicyAgent(Agent):
    """
    Policy compliance agent.
    Verifies proposal against P-* policies.
    """

    def __init__(self, llm_provider=None):
        super().__init__(agent_id="agent-policy", role=AgentRole.POLICY, llm_provider=llm_provider)
        self.llm_client = LLMClient()

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # 1. Load Purpose Directive (Purpose Gate)
        purpose_directive = ""
        try:
            with open("backend/governance/PURPOSE.md", "r", encoding="utf-8") as f:
                purpose_directive = f.read()
        except Exception:
            purpose_directive = "FAILED TO LOAD PURPOSE DIRECTIVE - FALLBACK TO NARRATIVE AUDIT."

        # 2. Recall Relevant Policies
        recalled_policies = await self.recall(f"Policies regarding {problem.title} {problem.context}", limit=5)

        # 3. Build Context for Purpose Audit
        context = f"""
        CORE PURPOSE DIRECTIVE (The Constitution):
        {purpose_directive}

        CURRENT PROPOSAL:
        Title: {problem.title}
        Context: {problem.context}
        """

        if recalled_policies:
            context += "\nSUPPLEMENTARY POLICIES:\n"
            for p in recalled_policies:
                context += f"- {p}\n"

        # 4. Configure LLM for Purpose Audit
        config = LLMConfig(temperature=0.0, json_mode=True)

        # 5. Execute Analysis
        try:
            raw_json, usage = await self.llm_client.generate_json(
                system_prompt="You are the Sovereign Purpose Gate. Your mission is HARD REALISM. Audit proposals against the Core Purpose Directive. Be ruthless about complexity and transparency.",
                user_prompt=f"Perform a PURPOSE AUDIT for the following proposal:\n\n{context}",
                config=config,
            )

            # Update Budget Tracking
            current_tokens = problem.metadata.get("total_tokens", 0)
            problem.metadata["total_tokens"] = current_tokens + usage.get("total_tokens", 0)
            problem.metadata["last_agent_tokens"] = usage.get("total_tokens", 0)
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                analysis=f"⚠️ Purpose Gate bypassed due to error: {str(e)}",
                confidence=0.0,
                concerns=[f"LLM Error during Purpose Audit: {str(e)}"],
            )

        # 6. Final Result Mapping (Phase 11: Purpose Score)
        # We now require a numerical 'purpose_score' from the LLM based on SED-01.
        purpose_score = raw_json.get("purpose_score", 0)
        is_compliant = raw_json.get("purpose_compliance", True) and (purpose_score >= 50)

        confidence = raw_json.get("confidence", 0.9) if is_compliant else 0.1

        concerns = raw_json.get("concerns", [])
        if not is_compliant:
            concerns.append(f"VIOLATION: Decision Quality too low ({purpose_score}/100) per SED-01 Hard Realism.")

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=raw_json.get("analysis", ""),
            recommendations=raw_json.get("recommendations") or ["Follow policy guidelines"],
            concerns=concerns or ["No policy violations found"],
            confidence=max(0.0, min(1.0, confidence)),
            understanding=raw_json.get("understanding"),
            risk_pre_mortem=raw_json.get("risk_pre_mortem") or [],
            trigger=raw_json.get("trigger"),
            impact=raw_json.get("impact"),
        )
