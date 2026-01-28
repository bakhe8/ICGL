"""
HDAL Agent - Human Decision Authority Layer
==========================================

The HDAL Agent manages the human-in-the-loop approval workflow,
including signature queues, decision tracking, and audit trails.
"""

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from src.core.agents.core.base import Agent, AgentResult, AgentRole, Problem
from src.core.kb.schemas import now


class DecisionStatus(Enum):
    """Status of approval decisions."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class ApprovalRequest:
    """Represents a pending approval request."""

    def __init__(
        self,
        request_id: str,
        title: str,
        description: str,
        risk_level: str,
        requester: str,
    ):
        self.request_id = request_id
        self.title = title
        self.description = description
        self.risk_level = risk_level
        self.requester = requester
        self.created_at = now()
        self.status = DecisionStatus.PENDING
        self.decision_by: Optional[str] = None
        self.decision_at: Optional[str] = None
        self.rationale: Optional[str] = None


class HDALAgent(Agent):
    """
    HDAL Agent: Human Decision Authority Layer interface.

    Responsibilities:
    - Manage signature queue for human approvals
    - Track decision history and audit trail
    - Assess risk levels and escalation needs
    - Ensure appropriate authority review
    - Maintain compliance and governance records
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="hdal",
            role=AgentRole.HDAL_AGENT,
            llm_provider=llm_provider,
        )
        self.signature_queue: List[ApprovalRequest] = []
        self.approval_history: List[ApprovalRequest] = []

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Analyzes problems from governance and approval perspective.

        Focus areas:
        - What decisions require human approval
        - Risk assessment and authority levels
        - Audit trail requirements
        - Escalation paths
        """

        # Assess risk level
        risk_level = self._assess_risk_level(problem)

        # Determine required approval authority
        required_authority = self._determine_authority_level(risk_level)

        # Generate approval recommendation
        approval_analysis = await self._generate_approval_analysis(problem, risk_level)

        # Check if escalation needed
        needs_escalation = self._check_escalation_needed(problem, risk_level)

        # Build comprehensive analysis
        analysis = f"""
=== GOVERNANCE ASSESSMENT ===
Risk Level: {risk_level.upper()}
Required Authority: {required_authority}
Escalation Needed: {"Yes" if needs_escalation else "No"}

=== APPROVAL ANALYSIS ===
{approval_analysis}

=== AUDIT TRAIL REQUIREMENTS ===
{self._get_audit_requirements(risk_level)}

=== DECISION WORKFLOW ===
{self._get_workflow_steps(risk_level, needs_escalation)}
"""

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                f"Queue for {required_authority} approval",
                "Document decision rationale in detail",
                "Prepare impact assessment for reviewers",
                "Set up audit trail logging",
            ],
            concerns=[
                f"High-impact decision requires {required_authority} oversight",
                "Approval delay may impact timeline",
                "Requires comprehensive documentation" if risk_level == "high" else "Standard review process",
            ],
            confidence=0.90,
        )

    def _assess_risk_level(self, problem: Problem) -> str:
        """Assess risk level of the decision."""
        context_lower = problem.context.lower()

        # Critical risk indicators
        critical_keywords = [
            "production",
            "deployment",
            "security breach",
            "data loss",
            "system failure",
            "critical",
        ]
        if any(kw in context_lower for kw in critical_keywords):
            return "critical"

        # High risk indicators
        high_keywords = [
            "security",
            "policy change",
            "architecture",
            "breaking change",
            "database",
            "authentication",
        ]
        if any(kw in context_lower for kw in high_keywords):
            return "high"

        # Medium risk indicators
        medium_keywords = ["feature", "enhancement", "refactor", "update", "modify"]
        if any(kw in context_lower for kw in medium_keywords):
            return "medium"

        return "low"

    def _determine_authority_level(self, risk_level: str) -> str:
        """Determine required approval authority based on risk."""
        authority_map = {
            "critical": "Executive Leadership + Security Officer",
            "high": "Senior Leadership",
            "medium": "Team Lead",
            "low": "Peer Review",
        }
        return authority_map.get(risk_level, "Team Lead")

    async def _generate_approval_analysis(self, problem: Problem, risk_level: str) -> str:
        """Generate detailed approval recommendation using LLM."""
        prompt = f"""
You are a governance officer reviewing a decision for approval.

Decision: {problem.title}
Context: {problem.context}
Risk Level: {risk_level}

Provide a concise approval recommendation (3-4 sentences) covering:
1. Key risks and implications
2. What authority should review this
3. Critical items to verify before approval
4. Suggested approval conditions if any
"""

        try:
            analysis = await self._ask_llm(prompt)
            return analysis.strip()
        except Exception:
            return (
                f"This {risk_level}-risk decision requires formal review. "
                "Recommend documenting all assumptions, conducting risk assessment, "
                "and obtaining appropriate authority approval before proceeding."
            )

    def _check_escalation_needed(self, problem: Problem, risk_level: str) -> bool:
        """Check if escalation to higher authority is needed."""
        # Always escalate critical and high-risk decisions
        if risk_level in ["critical", "high"]:
            return True

        # Check for specific escalation keywords
        escalation_keywords = [
            "compliance",
            "legal",
            "regulation",
            "audit",
            "policy violation",
            "security incident",
        ]
        return any(kw in problem.context.lower() for kw in escalation_keywords)

    def _get_audit_requirements(self, risk_level: str) -> str:
        """Get audit trail requirements based on risk level."""
        requirements = {
            "critical": """
- Full decision timeline with timestamps
- All stakeholder communications
- Technical impact assessment
- Rollback plan documentation
- Post-implementation review scheduled
            """,
            "high": """
- Decision rationale documented
- Risk assessment recorded
- Approval chain captured
- Implementation verification plan
            """,
            "medium": """
- Basic decision log entry
- Approver identity recorded
- Implementation notes
            """,
            "low": """
- Simple approval record
- Peer review confirmation
            """,
        }
        return requirements.get(risk_level, requirements["medium"]).strip()

    def _get_workflow_steps(self, risk_level: str, needs_escalation: bool) -> str:
        """Get workflow steps for this approval."""
        steps = [
            "1. Submit to signature queue",
            "2. Notify required approvers",
        ]

        if needs_escalation:
            steps.append("3. Escalate to executive review")
            steps.append("4. Await executive decision")
        else:
            steps.append("3. Await standard approval")

        steps.extend(
            [
                f"{len(steps) + 1}. Log decision in audit trail",
                f"{len(steps) + 2}. Notify stakeholders of outcome",
            ]
        )

        return "\n".join(steps)

    def queue_approval(self, title: str, description: str, risk_level: str, requester: str) -> ApprovalRequest:
        """Queue a new approval request."""
        request_id = f"APR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        request = ApprovalRequest(
            request_id=request_id,
            title=title,
            description=description,
            risk_level=risk_level,
            requester=requester,
        )

        self.signature_queue.append(request)
        return request

    def approve_request(self, request_id: str, approver: str, rationale: str) -> bool:
        """Approve a pending request."""
        for request in self.signature_queue:
            if request.request_id == request_id:
                request.status = DecisionStatus.APPROVED
                request.decision_by = approver
                request.decision_at = now()
                request.rationale = rationale

                # Move to history
                self.signature_queue.remove(request)
                self.approval_history.append(request)
                return True
        return False

    def reject_request(self, request_id: str, approver: str, rationale: str) -> bool:
        """Reject a pending request."""
        for request in self.signature_queue:
            if request.request_id == request_id:
                request.status = DecisionStatus.REJECTED
                request.decision_by = approver
                request.decision_at = now()
                request.rationale = rationale

                # Move to history
                self.signature_queue.remove(request)
                self.approval_history.append(request)
                return True
        return False

    def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Get all pending approval requests."""
        return list(self.signature_queue)

    def get_approval_history(self, limit: int = 20) -> List[ApprovalRequest]:
        """Get recent approval history."""
        return self.approval_history[-limit:]
