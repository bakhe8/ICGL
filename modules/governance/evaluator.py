"""
Consensus AI — Sovereign Evaluator
===================================
The central "Purpose Gate" that evaluates whether an Intent Contract
aligns with the system's Sovereign Purpose.

This replaces scattered logic in `PolicyAgent` and `server.py`.
"""

from dataclasses import dataclass, field
from typing import List

from ..agents.base import AgentResult, Problem
from ..coordination.advanced_policies import ConditionalPolicy
from ..kb.schemas import Timestamp, now


@dataclass
class EvaluationResult:
    """Result of a Sovereign Evaluation."""

    score: int  # 0-100
    status: str  # PASS | FAIL | WARNING
    rationale: List[str]
    policy_violations: List[str]
    timestamp: Timestamp = field(default_factory=now)


class SovereignEvaluator:
    """
    The Authority that measures "Decision Quality" against the Sovereign Purpose.

    Uses `ConditionalPolicy` to strictly evaluate intent.
    """

    def __init__(self):
        self._init_core_policies()

    def _init_core_policies(self):
        """Initialize the core 'Hard Realism' policies."""
        # Policy: Intent must be clear (Confidence > 0.7)
        self.clarity_policy = ConditionalPolicy("policy-clarity-threshold")
        # We could add specific conditions here if the Condition class was fully fleshed out,
        # but for now we'll implement the logic in `evaluate_intent`.

    def evaluate_intent(
        self, problem: Problem, agent_results: List[AgentResult]
    ) -> EvaluationResult:
        """
        Evaluates the "Purpose Score" of a proposed cycle.

        Args:
            problem: The problem/intent being solved.
            agent_results: The analysis from the Council.

        Returns:
            EvaluationResult containing the strict Score (0-100).
        """
        score = 100
        rationale = []
        violations = []

        # 1. Critical Policy Check (from Agent Results)
        # If Policy agent flagged a CRITICAL violation, score drops to 0 immediately.
        policy_agent_result = next(
            (r for r in agent_results if r.role.value == "policy"), None
        )
        if policy_agent_result:
            critical_concerns = [
                c for c in policy_agent_result.concerns if "CRITICAL" in c.upper()
            ]
            if critical_concerns:
                score = 0
                violations.extend(critical_concerns)
                rationale.append(
                    "⛔ Critical Policy Violation detected by PolicyAgent."
                )
                return EvaluationResult(
                    score=0,
                    status="FAIL",
                    rationale=rationale,
                    policy_violations=violations,
                )

        # 2. Confidence Penalty
        # "Uncertainty is a risk to Sovereignty."
        avg_confidence = 0.0
        if agent_results:
            avg_confidence = sum(r.confidence for r in agent_results) / len(
                agent_results
            )

        if avg_confidence < 0.7:
            penalty = int((0.7 - avg_confidence) * 100)
            score -= penalty
            rationale.append(
                f"⚠️ Low Confidence Penalty (-{penalty}): Average confidence is {avg_confidence:.2f}"
            )

        # 3. Budget Awareness
        # "Resource waste is purpose failure."
        token_usage = problem.metadata.get("total_tokens", 0)
        budget_limit = 50000
        if token_usage > (budget_limit * 0.8):
            score -= 10
            rationale.append(
                f"📉 Budget Risk Penalty (-10): Usage {token_usage} is >80% of limit."
            )

        if token_usage > budget_limit:
            score -= 50
            violations.append("Budget Exceeded")
            rationale.append(
                f"⛔ Budget Breach Penalty (-50): Usage {token_usage} exceeded limit."
            )

        # 4. Purpose Alignment (Intent Check)
        # If the intent is "Unknown", we penalize.
        if not problem.intent:
            score -= 20
            rationale.append(
                "❓ Vague Intent Penalty (-20): No clear Intent Contract defined."
            )

        # Cap score
        score = max(0, min(100, score))

        # Determine Status
        status = "PASS"
        if score < 50:
            status = "FAIL"
        elif score < 80:
            status = "WARNING"

        return EvaluationResult(
            score=score,
            status=status,
            rationale=rationale,
            policy_violations=violations,
        )
