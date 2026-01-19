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
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass, field

from .base import Agent, AgentRole, Problem, AgentResult
if TYPE_CHECKING:
    from .base import FileChange

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
    file_changes: List[Any] = field(default_factory=list) # Using Any to avoid circular import issues at runtime if needed
    
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
    
    def _init_llm_provider(self):
        """Initializes the LLM provider based on environment."""
        import os
        from core.llm import OpenAIProvider
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY missing. Real LLM provider is mandatory; no mock fallback.")
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
        Injects the LLM provider into the agent.
        """
        agent.llm = self._llm_provider
        self._agents[agent.role] = agent
    
    def get_agent(self, role: AgentRole) -> Optional[Agent]:
        """Gets an agent by role."""
        return self._agents.get(role)
    
    def list_agents(self) -> List[AgentRole]:
        """Returns list of registered agent roles."""
        return list(self._agents.keys())
    
    async def run_agent(self, role: AgentRole, problem: Problem, kb) -> Optional[AgentResult]:
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
            for agent in self._agents.values()
        ]
        return await asyncio.gather(*tasks)
    
    async def run_and_synthesize(self, problem: Problem, kb) -> SynthesizedResult:
        """
        Runs all agents and synthesizes their results.
        
        Returns:
            SynthesizedResult with combined analysis.
        """
        results = await self.run_all(problem, kb)
        return self._synthesize(results)
    
    def _synthesize(self, results: List[AgentResult]) -> SynthesizedResult:
        """Combines agent results into a synthesized output."""
        if not results:
            return SynthesizedResult(
                individual_results=[],
                consensus_recommendations=[],
                all_concerns=[],
                overall_confidence=0.0
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
        consensus = [
            r["text"] for r in all_recommendations.values()
            if r["count"] >= 2
        ]
        
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
            file_changes=all_file_changes
        )
