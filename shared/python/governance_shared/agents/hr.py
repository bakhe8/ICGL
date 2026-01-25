from typing import Optional

from .base import Agent, AgentResult, AgentRole, Problem


class HRAgent(Agent):
    """
    HRAgent: Specialized in employee records, role definitions, and access mapping.
    """

    def __init__(self, llm_provider: Optional[any] = None):
        super().__init__(
            agent_id="hr",
            role=AgentRole.HR,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Analyzes problems from an HR perspective.
        """
        prompt = f"""
        Analyze the following problem from an HR and Organizational perspective:
        
        Title: {problem.title}
        Context: {problem.context}
        
        Focus on:
        1. Impact on existing role definitions.
        2. Necessary changes to access mapping or permissions.
        3. Human resource requirements or capacity shifts.
        4. Alignment with employee records/governance.
        
        Provide a detailed analysis, recommendations, and identify any HR-related concerns.
        """

        analysis_text = await self._ask_llm(prompt, problem)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis_text,
            recommendations=[
                "Review role mapping in HDAL",
                "Verify access tokens for involved parties",
            ],
            concerns=["Potential permission drift detected in proposal context"]
            if "permission" in problem.context.lower()
            else [],
            confidence=0.85,
        )

    async def perform_capability_review(self) -> str:
        """
        Phase 13: Periodic Capability Review (The 4th Right).
        Audits all agents for performance, redundancy, and health.
        """
        from ..observability import get_ledger

        print("   📋 [HR] Starting Periodic Capability Review...")

        if not self.registry:
            return "❌ HR cannot perform review: Registry not connected."

        ledger = get_ledger()
        # In a real impl, we'd query stats by agent_id from DB
        # For now, we get general stats and list agents

        agents = self.registry.list_agents()
        report = ["# 📋 Quarterly Capability Review", ""]

        for role in agents:
            agent = self.registry.get_agent(role)
            if not agent:
                continue

            # Mock metric retrieval - ideally connect to SQLiteLedger.query_events
            # But the ledger schema is event-based. We'd aggregate "COMPLETED" events.
            report.append(f"## 👤 {role.value.title()}")
            report.append("- **Status**: Active")
            report.append(
                f"- **Silent Monitoring**: {'Enabled' if hasattr(agent, 'enable_silent_monitoring') else 'Disabled'}"
            )
            report.append(f"- **Specialty**: {getattr(agent, 'specialty', 'General')}")
            report.append("")

        # Phase 13.2: The KPI Committee (Social Consensus)
        committee_members = [AgentRole.POLICY, AgentRole.ARCHITECT]
        committee_feedback = []

        for member in committee_members:
            res = await self.consult_peer(
                member,
                title="KPI Validation Request",
                context=f"Reviewing performance metrics for {len(agents)} agents. Are current KPIs (Speed, Confidence, Strictness) sufficient?",
                kb=None,
            )
            if res:
                committee_feedback.append(
                    f"### 🗳️ {member.value.title()} Feedback\n{res.analysis}"
                )

        report.append("## ⚖️ KPI Committee Findings")
        if committee_feedback:
            report.extend(committee_feedback)
        else:
            report.append("No feedback received from committee members.")

        summary = "\n".join(report)

        # Log this review to the Kernel via Steward?
        # For now, just return it.
        return summary
