"""
Consensus AI — Knowledge Steward Agent
=======================================

Consolidates Documentation and Archival responsibilities.
Manages ADR lifecycle, system documentation, and historical records.
"""

from typing import Any, Optional

from shared.python.agents.base import Agent, AgentResult, AgentRole, Problem


class KnowledgeStewardAgent(Agent):
    """
    The Knowledge Steward: The single source of truth for system knowledge.
    Merges logic from original Archivist and Documentation agents.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="agent-knowledge-steward",
            role=AgentRole.STEWARD,  # Consolidated Knowledge Steward
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Unified analysis: ADR detection + Quality Assessment + History check.
        Phase 10: Logic Kernel - Promotes structured memory over narrative.
        """
        # 1. Proactive Synchronization
        sync_result = await self.sync_system_evolution()

        # 2. Institutional Response (Expansion Detection)
        if problem.title == "Sovereign Expansion Proposal":
            analysis = f"Expansion Request detected for Agent: {problem.metadata.get('role', 'unknown')}. Identifying domain overlaps and logging for executive review."
            await self.consult_peer(
                AgentRole.SECRETARY,
                title="SOVEREIGN GROWTH ALERT",
                context=f"The council is requesting expansion: {problem.context}",
                kb=kb,
            )
            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                analysis=analysis,
                recommendations=["Update strategic roadmap", "Prepare capability ADR"],
                confidence=1.0,
            )

        # 3. Contextual Retrieval (Institutional Memory Bridge)
        history_items = await self.recall(f"{problem.title} {problem.context}", limit=5)
        lessons = await self.recall_lessons(problem.context, limit=3)

        history_context = (
            "\n".join([f"- {h}" for h in history_items])
            if history_items
            else "No direct historical matches found."
        )

        prompt = f"""
        Analyze the following problem as the Knowledge Steward:
        
        Title: {problem.title}
        Context: {problem.context}
        
        🚀 SYSTEM EVOLUTION SYNC:
        {sync_result}
        
        📚 INSTITUTIONAL MEMORY:
        {history_context}
        
        Tasks:
        1. Contextualize within the 'Hard Realism' trajectory.
        2. Detect contradictions with current Logic Kernel patterns.
        3. ALWAYS recommend 'STRUCTURED_ADR' for lasting memory.
        """

        analysis = await self._ask_llm(prompt, problem)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                "GENERATE_STRUCTURED_ADR: Ensure this decision is stored in the Logic Kernel (JSON)",
                "Cross-reference against existing purpose audit results",
                "Update Purpose Gate logs if policy-relevant",
            ],
            confidence=0.98,
            references=history_items + lessons,
        )

    async def generate_structured_adr(
        self, adr_id: str, title: str, decision: str, context: str
    ) -> str:
        """
        Phase 10: Generates a JSON-structured ADR for computational memory.
        """
        import json
        from pathlib import Path

        print(
            f"   💾 [KnowledgeSteward] PHASE 10: Generating structured ADR {adr_id}..."
        )
        kernel_dir = Path("backend/kb/kernel")
        kernel_dir.mkdir(parents=True, exist_ok=True)

        adr_data = {
            "adr_id": adr_id,
            "title": title,
            "decision": decision,
            "context_summary": context[:500],
            "timestamp": "2026-01-24",
            "logical_impact": "SYSTEM_CORE",
            "governance_phase": 10,
        }

        file_path = kernel_dir / f"{adr_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(adr_data, f, indent=2)

        print(f"   ✅ [KnowledgeSteward] Logic Kernel updated: {file_path}")
        return f"Logic Kernel updated: {file_path}"

    async def generate_structured_lesson(self, log_entry: Any) -> str:
        """
        Phase 12: Generates a JSON-structured Lesson for computational memory.
        """
        import json
        from pathlib import Path

        print(
            f"   💾 [KnowledgeSteward] PHASE 12: Generating structured Lesson {log_entry.cycle}..."
        )
        kernel_dir = Path("backend/kb/kernel")
        kernel_dir.mkdir(parents=True, exist_ok=True)

        # Ensure we have a unique ID for the file
        lesson_id = f"lesson-{log_entry.cycle:04d}"

        lesson_data = {
            "id": lesson_id,
            "type": "LESSON",
            "cycle": log_entry.cycle,
            "summary": log_entry.summary,
            "notes": log_entry.notes,
            "new_policies": log_entry.new_policies,
            "timestamp": "2026-01-24",  # Hook to dynamic time later if needed
            "governance_phase": 12,
        }

        file_path = kernel_dir / f"{lesson_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(lesson_data, f, indent=2)

        print(f"   ✅ [KnowledgeSteward] Logic Kernel (Lesson) updated: {file_path}")
        return f"Logic Kernel updated: {file_path}"

    async def sync_system_evolution(self) -> str:
        """
        Synchronizes AGENTS.md, ADRs, and Logic Kernel.
        """
        import os
        from pathlib import Path

        registry_path = "backend/agents/registry.py"
        adr_dir = Path("backend/kb/adrs")
        kernel_dir = Path("backend/kb/kernel")

        registry_status = (
            "Registry Active." if os.path.exists(registry_path) else "Registry Missing."
        )
        adr_count = len(list(adr_dir.glob("*.md"))) if adr_dir.exists() else 0
        kernel_count = (
            len(list(kernel_dir.glob("*.json"))) if kernel_dir.exists() else 0
        )

        return f"{registry_status} ADRs: {adr_count} (Narrative), {kernel_count} (Logic Kernel)."
