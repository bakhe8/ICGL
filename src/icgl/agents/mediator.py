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

    async def request_consultation(self, requester_id: str, request_data: Dict[str, Any], consultant_agent: Any) -> Dict[str, Any]:
        """
        Manages access to the External Consultant to save costs/load.
        
        Policy:
        - CRITICAL severity -> ALLOW instantly.
        - HIGH severity -> ALLOW if budget permits.
        - MEDIUM/LOW -> REJECT or QUEUE.
        """
        severity = request_data.get("severity", "MEDIUM")
        content_hash = hash(str(request_data.get("content", "")))
        
        # 1. Check Priority
        if severity == "CRITICAL":
            # Bypass budget check for emergencies
            return await self._execute_consultation(requester_id, request_data, consultant_agent)
            
        # 2. Check Redundancy (Mock cache)
        # if content_hash in self.cache: return self.cache[content_hash]
        
        # 3. Simulate "Budget Check" (Heuristic)
        # Allow 80% of High priority, 20% of Medium
        import random
        if severity == "HIGH" and random.random() > 0.2:
             return await self._execute_consultation(requester_id, request_data, consultant_agent)
             
        if severity == "MEDIUM" and random.random() > 0.8:
             return await self._execute_consultation(requester_id, request_data, consultant_agent)
             
        return {
            "approved": False,
            "reason": "Traffic Control: Request suppressed to save budget (Low Priority).",
            "consultation_result": None
        }

    async def _execute_consultation(self, requester_id: str, data: Dict, consultant: Any) -> Dict:
        """Executes the call and logs it."""
        try:
            # Determine method based on data
            doc_type = data.get("doc_type", "General")
            content = data.get("content", "")
            
            result = await consultant.review_document_draft(doc_type, content)
            
            return {
                "approved": True,
                "reason": "Authorized by Mediator",
                "consultation_result": result
            }
        except Exception as e:
            return {"approved": False, "reason": f"Consultant Error: {e}", "consultation_result": None}

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # ... existing logic ...
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
