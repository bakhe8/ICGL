"""
Consensus AI — Agent Registry
==============================

Central registry for managing and running agents.

Features:
- Register agents by role
- Run agents in parallel or sequential
- Collect and synthesize results

Usage:
    registry = AgentRegistry()
    registry.register(ArchitectAgent())
    results = await registry.run_all(problem, kb)
"""

import asyncio
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from backend.core.llm import OpenAIProvider

from .base import Agent, AgentResult, AgentRole, Problem

if TYPE_CHECKING:
    pass


@dataclass
class SynthesizedResult:
    """
    Combined results from all agents.

    Attributes:
        individual_results: Results from each agent.
        consensus_recommendations: Recommendations agreed by multiple agents.
        all_concerns: All identified concerns.
        overall_confidence: Average confidence across agents.
        file_changes: Aggregated file changes proposed by agents.
    """

    individual_results: List[AgentResult]
    consensus_recommendations: List[str]
    all_concerns: List[str]
    overall_confidence: float
    mediation: Optional[Dict[str, Any]] = None
    file_changes: List[Any] = field(
        default_factory=list
    )  # Using Any to avoid circular import issues at runtime if needed

    def to_markdown(self) -> str:
        """Formats synthesized result as Markdown."""
        lines = [
            "# Agent Analysis Synthesis",
            "",
            f"**Overall Confidence:** {self.overall_confidence:.0%}",
            f"**Agents Consulted:** {len(self.individual_results)}",
            "",
        ]

        if self.consensus_recommendations:
            lines.append("## Consensus Recommendations")
            for rec in self.consensus_recommendations:
                lines.append(f"- ✅ {rec}")
            lines.append("")

        if self.all_concerns:
            lines.append("## Identified Concerns")
            for concern in self.all_concerns:
                lines.append(f"- ⚠️ {concern}")
            lines.append("")

        if self.mediation:
            lines.append("## Mediation Summary")
            lines.append(self.mediation.get("analysis", "No analysis provided."))
            lines.append("")

        lines.append("---")
        lines.append("")

        for result in self.individual_results:
            lines.append(result.to_markdown())

        return "\n".join(lines)


class AgentRegistry:
    """
    Central registry for managing agents.

    Supports:
    - Registering agents by role
    - Running all agents in parallel
    - Synthesizing combined results
    """

    def __init__(self):
        self._agents: Dict[AgentRole, Agent] = {}
        self._llm_provider = self._init_llm_provider()
        self.router = None  # Injected by ICGL/Server

    def set_router(self, router: Any) -> None:
        """Sets the router and injects it into all registered agents."""
        self.router = router
        for agent in self._agents.values():
            agent.channel_router = router

    def _init_llm_provider(self):
        """Initializes the LLM provider based on environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY missing. Real LLM provider is mandatory; no mock fallback."
            )
        try:
            print("[AgentRegistry] 🧠 Initializing OpenAI Provider...")
            return OpenAIProvider(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI provider: {e}")

    def get_llm_provider(self):
        """Expose the underlying LLM provider (for mediator or external agents)."""
        return self._llm_provider

    def register(self, agent: Agent) -> None:
        """
        Registers an agent by its role.
        Injects the LLM provider, Registry, and Router into the agent.
        """
        agent.llm = self._llm_provider
        agent.registry = self
        agent.channel_router = self.router
        self._agents[agent.role] = agent

    def get_agent(self, role: AgentRole) -> Optional[Agent]:
        """Gets an agent by role."""
        return self._agents.get(role)

    def list_agents(self) -> List[AgentRole]:
        """Returns list of registered agent roles."""
        return list(self._agents.keys())

    async def run_agent(
        self, role: AgentRole, problem: Problem, kb
    ) -> Optional[AgentResult]:
        """Runs a single agent by role."""
        agent = self._agents.get(role)
        if agent:
            return await agent.analyze(problem, kb)
        return None

    async def run_all(self, problem: Problem, kb) -> List[AgentResult]:
        """
        Runs all registered agents in parallel.

        Returns:
            List of AgentResults from all agents.
        """
        tasks = [
            agent.analyze(problem, kb)
            for role, agent in self._agents.items()
            if role != AgentRole.MEDIATOR
        ]
        return await asyncio.gather(*tasks)

    async def run_single_agent(
        self, agent_identifier: str, problem: Problem, kb
    ) -> Optional[AgentResult]:
        """
        Run a single agent by ID or Role str.
        Handles mapping 'agent-architect' -> AgentRole.ARCHITECT
        """
        target_agent = None

        # Try direct role match first
        try:
            role_enum = AgentRole(agent_identifier)
            target_agent = self._agents.get(role_enum)
        except ValueError:
            # Try search by agent_id
            for agent in self._agents.values():
                if (
                    agent.agent_id == agent_identifier
                    or agent.role.value == agent_identifier
                ):
                    target_agent = agent
                    break

        if target_agent:
            return await target_agent.analyze(problem, kb)

        return None

    async def run_and_synthesize_dynamic(
        self,
        problem: Problem,
        kb,
        allowed_agents: Optional[List[str]] = None,
        precomputed_results: List[AgentResult] = None,
    ) -> SynthesizedResult:
        """
        Cycle 15: Run only the ALLOWED agents (The Council).
        Includes Phase 10 Consultation Budgeting.
        """
        # --- PHASE 10: Consultation Budgeting ---
        current_depth = problem.metadata.get("consultation_depth", 0)
        max_depth = int(os.getenv("ICGL_MAX_CONSULTATION_DEPTH", 3))

        if current_depth >= max_depth:
            print(
                f"[Registry] ⚠️ Max consultation depth ({max_depth}) reached. Terminating recursion."
            )
            return self._synthesize(precomputed_results or [])

        # Check Token Budget (Phase 12 Refactor)
        from backend.governance.budget import TokenBudget

        budget = TokenBudget()

        current_tokens = problem.metadata.get("total_tokens", 0)

        if not budget.check_usage(current_tokens):
            status = budget.get_status(current_tokens)
            print(
                f"[Registry] ⚠️ Token Budget {status.state} ({status.used}/{status.limit}). Terminating cycle."
            )
            return self._synthesize(precomputed_results or [])

        # Increment depth for downstream consultations
        problem.metadata["consultation_depth"] = current_depth + 1
        # ----------------------------------------

        results = precomputed_results or []

        if allowed_agents is None:
            # Fallback to run all
            new_results = await self.run_all(problem, kb)
            results.extend(new_results)
        else:
            # Filter and Run
            tasks = []
            allowed_set = {a.lower() for a in allowed_agents}

            for role, agent in self._agents.items():
                # Skip Mediator (handled separately)
                if role == AgentRole.MEDIATOR:
                    continue

                # Skip if we already used it (e.g. Architect)
                if any(r.agent_id == agent.agent_id for r in results):
                    continue

                # Check if allowed
                if agent.role.value in allowed_set or agent.agent_id in allowed_set:
                    tasks.append(agent.analyze(problem, kb))

            if tasks:
                new_results = await asyncio.gather(*tasks)
                results.extend(new_results)

        # Synthesize everything
        synthesis = self._synthesize(results)

        # SYSTEM VISIBILITY: Report to Secretary
        secretary = self.get_agent(AgentRole.SECRETARY)
        if secretary and hasattr(secretary, "_log_relay_event"):
            try:
                participating_agents = [r.agent_id for r in results]
                # Log the synthesis event
                secretary._log_relay_event(
                    event_type="SYNTHESIS_COMPLETE",
                    summary=f"Consensus reached for: {problem.title}",
                    technical_details=f"Confidence: {synthesis.overall_confidence:.0%}. Agents: {', '.join(participating_agents)}",
                    stakeholders=[r.role.value for r in results],
                    priority="high" if synthesis.overall_confidence < 0.7 else "normal",
                )
            except Exception as e:
                print(f"[Registry] Failed to log to secretary: {e}")

        # Auto-Mediation Activation
        # If confidence is low or agents are conflicting, pull in the Mediator
        if synthesis.overall_confidence < 0.7 or len(synthesis.all_concerns) > 3:
            mediator = self.get_agent(AgentRole.MEDIATOR)
            if mediator:
                print(
                    f"[AgentRegistry] ⚖️ Low confidence ({synthesis.overall_confidence:.1%}) detected. Invoking MediatorAgent..."
                )

                # Notify Secretary about Mediation
                if secretary and hasattr(secretary, "_log_relay_event"):
                    secretary._log_relay_event(
                        event_type="MEDIATION_TRIGGERED",
                        summary="Mediator intervened due to low confidence",
                        technical_details=f"Confidence: {synthesis.overall_confidence:.0%}. Concerns: {len(synthesis.all_concerns)}",
                        stakeholders=["Mediator", "Council"],
                        priority="high",
                    )

                # Inject results into problem metadata for mediator context
                problem.metadata["agent_results"] = [
                    {
                        "agent_id": r.agent_id,
                        "analysis": r.analysis,
                        "recommendations": r.recommendations,
                        "concerns": r.concerns,
                        "understanding": r.understanding,
                        "confidence": r.confidence,
                    }
                    for r in results
                ]
                mediation_result = await mediator.analyze(problem, kb)
                synthesis.mediation = {
                    "agent_id": mediation_result.agent_id,
                    "analysis": mediation_result.analysis,
                    "confidence": mediation_result.confidence,
                    "recommendations": mediation_result.recommendations,
                }

        return synthesis

    def _synthesize(self, results: List[AgentResult]) -> SynthesizedResult:
        """Combines agent results into a synthesized output."""
        if not results:
            return SynthesizedResult(
                individual_results=[],
                consensus_recommendations=[],
                all_concerns=[],
                overall_confidence=0.0,
            )

        # Collect all recommendations and find consensus
        all_recommendations = {}
        for result in results:
            for rec in result.recommendations:
                rec_lower = rec.lower()
                if rec_lower not in all_recommendations:
                    all_recommendations[rec_lower] = {"text": rec, "count": 0}
                all_recommendations[rec_lower]["count"] += 1

        # Consensus = recommended by 2+ agents
        consensus = [r["text"] for r in all_recommendations.values() if r["count"] >= 2]

        # If no consensus, take top recommendations
        if not consensus:
            consensus = [r["text"] for r in list(all_recommendations.values())[:3]]

        # Collect all concerns
        all_concerns = []
        for result in results:
            all_concerns.extend(result.concerns)
        all_concerns = list(set(all_concerns))

        # Calculate overall confidence
        overall_confidence = sum(r.confidence for r in results) / len(results)

        # Collect all file changes
        all_file_changes = []
        for result in results:
            if hasattr(result, "file_changes"):
                all_file_changes.extend(result.file_changes)

        return SynthesizedResult(
            individual_results=results,
            consensus_recommendations=consensus,
            all_concerns=all_concerns,
            overall_confidence=overall_confidence,
            file_changes=all_file_changes,
        )
