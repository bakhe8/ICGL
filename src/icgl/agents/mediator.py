"""
ICGL — Mediator Agent
=====================

Resolves conflicts بين نتائج الوكلاء عند انخفاض الثقة الكلية.
مصمم ليكون آمناً بدون اعتماد على LLM إذا لم تتوفر مفاتيح.
"""

from .base import Agent, AgentRole, Problem, AgentResult


class MediatorAgent(Agent):
    """
    Mediator Agent: يصوغ تسوية/تصعيد عند تضارب نتائج الوكلاء.
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            agent_id="agent-mediator",
            role=AgentRole.ARCHITECT,
            llm_provider=llm_provider,
        )

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

        # تجميع المخاوف والتوصيات
        concerns = []
        recs = []
        for r in other_results:
            concerns.extend(r.get("concerns", []))
            recs.extend(r.get("recommendations", []))

        # محاولة استخدام LLM إن توفّر
        if self.llm:
            prompt = (
                f"Proposal: {problem.title}\nContext: {problem.context}\n\n"
                f"Summarize concerns and propose a compromise plan.\n"
                f"Concerns: {concerns}\nRecommendations: {recs}"
            )
            try:
                content = await self._ask_llm(prompt)
                analysis_text = content
                confidence = 0.75
            except Exception as e:
                analysis_text = f"[Fallback] Mediation without LLM due to error: {e}"
                confidence = 0.4
        else:
            analysis_text = (
                "LLM not available; synthesized compromise:\n"
                f"- Top concerns: {', '.join(concerns[:3])}\n"
                f"- Recommendations to align: {', '.join(recs[:3])}"
            )
            confidence = 0.4

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis_text,
            recommendations=recs[:3],
            concerns=concerns[:3],
            confidence=confidence,
        )
