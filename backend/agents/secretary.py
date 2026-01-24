"""
Secretary Agent - Executive Coordination and Communication Gateway
==================================================================

The Secretary Agent acts as the translation layer between technical operations
and executive leadership, managing coordination, event logging, and stakeholder
communication.
"""

from typing import Any, Dict, List, Optional

from ..kb.schemas import now
from .base import Agent, AgentResult, AgentRole, Problem


class RelayLogEntry:
    """Represents a single relay log entry for executive tracking."""

    def __init__(
        self,
        event_type: str,
        summary: str,
        technical_details: str,
        stakeholders: List[str],
        priority: str = "normal",
    ):
        self.timestamp = now()
        self.event_type = event_type
        self.summary = summary
        self.technical_details = technical_details
        self.stakeholders = stakeholders
        self.priority = priority

    def to_executive_format(self) -> str:
        """Convert technical event to executive-friendly format."""
        priority_indicator = (
            "🔴"
            if self.priority == "high"
            else "🟡"
            if self.priority == "medium"
            else "🟢"
        )

        return f"""
{priority_indicator} {self.event_type.upper()}
Time: {self.timestamp}
Summary: {self.summary}
Stakeholders: {", ".join(self.stakeholders)}
"""


class SecretaryAgent(Agent):
    """
    Secretary Agent: Executive coordination and communication gateway.

    Responsibilities:
    - Translate technical events to executive summaries
    - Maintain relay log for leadership visibility
    - Coordinate stakeholder communication
    - Track cross-departmental dependencies
    - Prepare executive briefings and status reports
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="secretary",
            role=AgentRole.SECRETARY,
            llm_provider=llm_provider,
        )
        self.relay_log: List[RelayLogEntry] = []
        self.active_coordinations: Dict[str, Dict[str, Any]] = {}

        # Cycle 14: Use Real LLM for Native Understanding
        from ..llm.client import LLMClient

        self.llm_client = LLMClient()

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Native Understanding Layer (Cycle 14) + Relay Logging.
        """
        # Phase 6: Handle internal Sovereign Alerts
        if "SOVEREIGN" in problem.title.upper():
            self._log_relay_event(
                event_type="GROWTH_ALERT",
                summary=problem.title,
                technical_details=problem.context,
                stakeholders=["Executive Council", "Stewards"],
                priority="high",
            )
            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                analysis=f"Sovereign event recorded: {problem.title}",
                recommendations=["Notify human stakeholder"],
                confidence=1.0,
            )

        from ..llm.prompts import SECRETARY_SYSTEM_PROMPT

        # 1. Ask LLM for Interpretation
        response_json = await self._ask_llm_json(
            prompt=f"User Input: {problem.title}\nContext: {problem.context}",
            system_prompt=SECRETARY_SYSTEM_PROMPT,
        )

        # 2. Parse Results
        interpretation = response_json.get("interpretation_ar", "No interpretation")
        technical_intent = response_json.get("technical_intent", "")
        ambiguity = int(response_json.get("ambiguity_score", 5))
        clarity_needed = response_json.get("clarity_needed", False)

        # 3. Secure Handoff (Zero Interference)
        # We only notify the Architect if we are confident and clear.
        if not clarity_needed and technical_intent:
            try:
                await self.send_to_agent(
                    target_agent="architect",
                    action="PROPOSE_INTENT",
                    payload={
                        "technical_intent": technical_intent,
                        "original_input": problem.title,
                        "source": "Native Understanding Layer",
                    },
                )
                print(
                    f"   📡 [Secretary] Handoff to Architect: {technical_intent[:50]}..."
                )
            except Exception as e:
                print(f"   ⚠️ [Secretary] Channel Handoff Failed: {e}")

        # 4. Return Result for UI
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=response_json.get("analysis", "Understanding processed."),
            recommendations=response_json.get("recommendations", []),
            concerns=response_json.get("concerns", []),
            confidence=response_json.get("confidence_score", 0.8),
            # Cycle 14 Fields
            interpretation_ar=interpretation,
            english_intent=technical_intent,
            ambiguity_level="High"
            if ambiguity > 7
            else "Medium"
            if ambiguity > 3
            else "Low",
            clarity_needed=clarity_needed,
            clarity_question=response_json.get("clarity_question"),
        )

    async def _ask_llm_json(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """Helper for JSON responses using Real LLMClient."""
        from ..llm.client import LLMConfig

        config = LLMConfig(
            model="gpt-4-turbo-preview", temperature=0.3, timeout=30.0, json_mode=True
        )

        try:
            # Use the real LLM Client directly
            result, usage = await self.llm_client.generate_json(
                system_prompt=system_prompt, user_prompt=prompt, config=config
            )

            # Update Budget Tracking (Accessing problem via self or passed context - for Secretary, we'll assume current problem context if possible)
            # Since _ask_llm_json might be called in a context where problem isn't directly available,
            # we should update it if we can find it.
            # In _analyze, we'll pass it. Let's update _ask_llm_json signature too.

            if isinstance(result, dict):
                return result

            # Fallback if client returns string
            import json

            cleaned = str(result).replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)

        except Exception as e:
            print(f"⚠️ [Secretary] LLM Error: {e}")
            return {
                "interpretation_ar": "تعذر التفسير (خطأ في الاتصال)",
                "technical_intent": prompt,
                "ambiguity_score": 5,
                "clarity_needed": True,
            }

    def _identify_stakeholders(self, problem: Problem) -> List[str]:
        """Identify relevant stakeholders from problem context."""
        stakeholders = set()

        # Keywords that indicate stakeholder involvement
        stakeholder_map = {
            "security": "Security Team",
            "architect": "Architecture Team",
            "policy": "Governance Team",
            "hr": "HR Team",
            "engineer": "Engineering Team",
            "test": "QA Team",
            "deploy": "Operations Team",
            "user": "Product Team",
        }

        context_lower = problem.context.lower()
        for keyword, stakeholder in stakeholder_map.items():
            if keyword in context_lower:
                stakeholders.add(stakeholder)

        # Always include executive leadership for governance matters
        stakeholders.add("Executive Leadership")

        return list(stakeholders)

    async def _generate_executive_summary(self, problem: Problem) -> str:
        """Generate concise executive summary using LLM."""
        prompt = f"""
You are an executive assistant preparing a brief for leadership.
Translate this technical problem into a 2-3 sentence executive summary.

Problem: {problem.title}
Details: {problem.context}

Rules:
- Use business language, not technical jargon
- Focus on impact and decisions needed
- Be concise and actionable
- Highlight risks and opportunities
"""

        try:
            summary = await self._ask_llm(prompt, problem)
            return summary.strip()
        except Exception:
            # Fallback to simple summary
            return (
                f"Decision required: {problem.title}. "
                "Review and approval needed for governance compliance."
            )

    def _analyze_coordination_needs(
        self, problem: Problem, stakeholders: List[str]
    ) -> str:
        """Analyze what coordination is needed across teams."""
        needs = []

        if len(stakeholders) > 2:
            needs.append(
                "⚠️ Multi-team coordination required - suggest alignment meeting"
            )

        if "security" in problem.context.lower():
            needs.append("🔒 Security review mandatory before implementation")

        if "policy" in problem.context.lower():
            needs.append("📋 Policy compliance verification needed")

        if not needs:
            needs.append("✅ Standard governance flow - minimal coordination overhead")

        return "\n".join(needs)

    def _assess_priority(self, problem: Problem) -> str:
        """Assess priority level for executive attention."""
        context_lower = problem.context.lower()

        # High priority indicators
        high_keywords = ["critical", "security", "breach", "failure"]
        if any(word in context_lower for word in high_keywords):
            return "high"

        # Medium priority indicators
        medium_keywords = ["important", "policy", "compliance"]
        if any(word in context_lower for word in medium_keywords):
            return "medium"

        return "normal"

    def _log_relay_event(
        self,
        event_type: str,
        summary: str,
        technical_details: str,
        stakeholders: List[str],
        priority: str = "normal",
    ) -> None:
        """Log event to relay log for executive tracking."""
        entry = RelayLogEntry(
            event_type=event_type,
            summary=summary,
            technical_details=technical_details,
            stakeholders=stakeholders,
            priority=priority,
        )
        self.relay_log.append(entry)

        # Keep only last 100 entries to prevent memory bloat
        if len(self.relay_log) > 100:
            self.relay_log = self.relay_log[-100:]

    def get_executive_report(self, last_n_events: int = 10) -> str:
        """Generate executive report from recent relay log entries."""
        recent_entries = self.relay_log[-last_n_events:]

        if not recent_entries:
            return "No recent events to report."

        report_lines = ["=== EXECUTIVE STATUS REPORT ===", ""]
        for entry in reversed(recent_entries):  # Most recent first
            report_lines.append(entry.to_executive_format())

        return "\n".join(report_lines)
