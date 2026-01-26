"""
ICGL — Mediator Agent
=====================

Resolves conflicts بين نتائج الوكلاء عند انخفاض الثقة الكلية.
مصمم ليكون آمناً بدون اعتماد على LLM إذا لم تتوفر مفاتيح.
"""


from modules.llm.client import LLMClient, LLMConfig
from .base import Agent, AgentResult, AgentRole, Problem


class MediatorAgent(Agent):
    """
    Mediator Agent: يصوغ تسوية/تصعيد عند تضارب نتائج الوكلاء.
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            agent_id="agent-mediator",
            role=AgentRole.MEDIATOR,
            llm_provider=llm_provider,
        )
        self.llm_client = LLMClient()

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        other_results = problem.metadata.get("agent_results", [])

        if not other_results:
            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                analysis="No agent results provided for mediation.",
                confidence=1.0,
                concerns=[],
            )

        # 1. Identify Conflicts (Interpretation & Confidence)
        [
            r["agent_id"] for r in other_results if r.get("confidence", 1.0) < 0.7
        ]
        interpretations = [
            f"{r['agent_id']}: {r.get('understanding', {}).get('interpretation', 'N/A')}"
            for r in other_results
        ]

        # 2. Configure LLM for Resolution
        config = LLMConfig(temperature=0.0, json_mode=True)

        mediation_prompt = (
            f"You are the ICGL Mediator Agent. Your role is to EXPOSE tensions between agents for human review.\n\n"
            f"IDEAL INTENT: {problem.intent.goal if problem.intent else problem.title}\n\n"
            f"AGENT PROPOSALS:\n" + "\n".join(interpretations) + "\n\n"
            "GOAL: Identify points of tension AND provide a suggested resolution for each.\n"
            "Your resolution should balance the competing concerns (e.g., recommend a middle ground or prioritize the most critical concern).\n"
            'OUTPUT JSON: {"tensions": [{"dimension": "...", "left_agent": "...", "right_agent": "...", "description": "...", "suggested_resolution": "..."}], "analysis": "...", "recommendations": []}'
        )

        # 3. Execute Mediation with Safety
        try:
            result = await self.llm_client.generate_json(
                system_prompt="You are an expert mediator. Your goal is to identify and surface conflicts between LLM agents.",
                user_prompt=mediation_prompt,
                config=config,
            )

            # Allow mocks to return dict only (tests) or (dict, usage) tuple (runtime)
            if isinstance(result, tuple):
                raw_json, usage = result  # type: ignore[misc]
            else:
                raw_json, usage = result, {}  # type: ignore[assignment]

            # Update Budget Tracking
            current_tokens = problem.metadata.get("total_tokens", 0)
            problem.metadata["total_tokens"] = current_tokens + usage.get(
                "total_tokens", 0
            )
            problem.metadata["last_agent_tokens"] = usage.get("total_tokens", 0)
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                analysis=f"⚠️ Mediation Failed due to LLM Error: {str(e)}",
                confidence=0.0,
                concerns=[f"LLM Error: {str(e)}"],
                clarity_needed=True,
                clarity_question="The Mediator failed. Human intervention required.",
            )

        # 4. Map to AgentResult
        if raw_json.get("consensus_reached") is False:
            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                analysis=raw_json.get(
                    "analysis", "Conflict detected; human review required."
                ),
                recommendations=raw_json.get("recommendations", []),
                clarity_needed=True,
                clarity_question=raw_json.get(
                    "clarity_question",
                    "Conflict detected between agent results. Human intervention required.",
                ),
                confidence=0.4,
                concerns=["Consensus not reached"],
            )

        # Default path when consensus reached or not specified
        tensions = raw_json.get("tensions", [])
        analysis = raw_json.get("analysis", "Tension analysis completed.")

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=raw_json.get("recommendations", []),
            confidence=raw_json.get(
                "confidence", 0.5 if tensions else 0.9
            ),  # Lower confidence if tensions exist
            tensions=tensions,
            clarity_needed=len(tensions) > 0,
            clarity_question=f"Tensions detected: {len(tensions)} issues require human review."
            if tensions
            else None,
        )
