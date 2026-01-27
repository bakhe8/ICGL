from typing import Any, List, Optional

from shared.python.agents.base import Agent, AgentResult, AgentRole, Problem
from shared.python.governance.signing_queue import signing_queue
from shared.python.kb.schemas import FileChange


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
        # 1. Sentinel Risk Check (Real Heuristic)
        _sentinel_result = "SENTINEL_OK"
        # We assume Sentinel is available via registry usually, but here we do a lightweight check
        # If problem implies high risk, we escalate.
        is_risky = "delete" in problem.context.lower() or "remove" in problem.context.lower()

        # 2. Mirror Protocol (LLM)
        prompt = f"""
        You are the EXECUTIVE AGENT, the primary bridge between the HUMAN OWNER and the ICGL.
        
        Current Request: {problem.title}
        Context: {problem.context}
        Risk Indicators: {"High Risk Terms Detected" if is_risky else "Standard"}
        
        YOUR OBJECTIVES:
        1. **Confirmation Mirror**: Paraphrase the user's request.
        2. **Assess**: Is this action irreversible?
        3. **Prepare Queue**: Summarize the intent for the Signing Queue.
        
        Output JSON only: {{ "mirror": "...", "risk_assessment": "...", "queue_summary": "..." }}
        """

        # Mocking LLM response for resilience if key missing, or use real one
        response_text = await self._ask_llm(prompt)

        try:
            # Basic parsing or fallback
            import json

            if "{" in response_text:
                data = json.loads(response_text[response_text.find("{") : response_text.rfind("}") + 1])
                mirror = data.get("mirror", "Understood.")
                _queue_summary = data.get("queue_summary", problem.title)
            else:
                mirror = response_text
                _queue_summary = problem.title
        except Exception as e:
            mirror = response_text
            _queue_summary = problem.title
            # Log the exception for observability
            print(f"[ExecutiveAgent] LLM parsing fallback due to: {e}")

        # 3. Add to Signing Queue (Persistence)
        # We interpret the problem as requiring actions.
        # In a full flow, Architect would have provided file_changes.
        # Here we queue the INTENT.

        queue_item = signing_queue.add_to_queue(
            title=f"Executive Sign-off: {problem.title}",
            description=f"Risk Assessment: {is_risky}. \nMirror: {mirror}",
            actions=[],  # Ideally populated from input or Architect
            agent_id=self.agent_id,
            risk_level="HIGH" if is_risky else "MEDIUM",
        )

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=f"🛑 Action Halted for Sovereign Signature.\n\nMirror: {mirror}\n\nItem queued as ID: {queue_item['id']}",
            confidence=1.0,
            clarity_needed=True,
            clarity_question=f"Please sign off on action {queue_item['id']} in the Executive Console.",
            recommendations=[
                "Go to Executive Console",
                "Review predicted impact",
                "Sign or Reject",
            ],
            metadata={
                "phase": "inverse_governance_mirror",
                "queue_id": queue_item["id"],
                "status": "QUEUED",
            },
        )

    async def generate_action_queue(self, confirmed_problem: Problem) -> List[FileChange]:
        """
        Generates actions AFTER signing.
        """
        return []
