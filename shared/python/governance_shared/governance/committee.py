"""
Consensus AI — Sovereign UI Committee
=====================================
User Request: A committee of 14+ agents to study the system periodically
and express its state via the Frontend.
"""

import asyncio

from ..agents.base import AgentRole, Problem
from ..governance.icgl import ICGL


class SovereignCommittee:
    def __init__(self, icgl: ICGL):
        self.icgl = icgl
        # The user requested 14 specifically:
        self.members = [
            AgentRole.UI_UX,
            AgentRole.REFACTORING,
            AgentRole.DATABASE,
            AgentRole.VERIFICATION,
            AgentRole.TESTING,
            AgentRole.ARCHITECT,
            AgentRole.SPECIALIST,  # Was CODE_SPECIALIST
            AgentRole.GUARDIAN,  # ConceptGuardian
            AgentRole.SECRETARY,
            AgentRole.STEWARD,
            AgentRole.HDAL_AGENT,
            AgentRole.EFFICIENCY,
            AgentRole.CENTRAL_CATALYST,  # Was CATALYST
            AgentRole.BUILDER,
        ]

    async def convene(self) -> str:
        """
        Convening the 'System Reflection' session.
        Each agent submits a 'Vibe Check' / Status Report used to paint the system's soul.
        """
        print("\n🏛️ [Committee] Convening the Sovereign UI Committee (14 Members)...")

        # 1. Gather Perspectives
        reports = {}

        problem = Problem(
            title="System Reflection: Self-Expression",
            context="""
            We are creating a 'System Soul Page' in the UI.
            QUESTION: Based on your domain, what visual metaphor represents our *current* state?
            
            E.g. If Chaos is high -> "Stormy Red".
            If Efficiency is high -> "Clean Minimalist".
            If DB is corrupt -> "Glitching Matrix".
            """,
        )

        # Broadcast to all members
        # We run in parallel batches to speed up
        tasks = []
        for role in self.members:
            # CodeSpecialist Role in Enum is actually 'specialist'?
            # Let's map strict roles.
            tasks.append(
                self.icgl.registry.run_single_agent(role.value, problem, self.icgl.kb)
            )

        results = await asyncio.gather(*tasks)

        valid_results = [r for r in results if r]

        # 2. Synthesize using Catalyst
        print("   🧪 [Catalyst] Synthesizing the Collective Soul...")
        synthesis_context = "\n\n".join(
            [
                f"--- {res.role.value.upper()} SAYS: ---\n{res.analysis}"
                for res in valid_results
            ]
        )

        # We ask Catalyst to describe the UI
        catalyst_res = await self.icgl.registry.run_single_agent(
            AgentRole.CENTRAL_CATALYST.value,
            Problem(
                title="Synthesize System Soul UI",
                context=f"Combine these perspectives into a cohesive UI description for 'SystemSoulPage.tsx'.\nINPUTS:\n{synthesis_context}",
            ),
            self.icgl.kb,
        )

        soul_description = (
            catalyst_res.analysis
            if catalyst_res
            else "System is Silent (Synthesis Failed)."
        )

        # 3. Execution: Spawn Specialist to Render
        print("   🎨 [UI/UX] Spawning 'SoulRenderer' Specialist to write code...")

        ui_agent = self.icgl.registry.get_agent(AgentRole.UI_UX)
        if ui_agent and hasattr(ui_agent, "spawn_specialist"):
            # We ask the specialist to generate the React Component
            render_result = await ui_agent.spawn_specialist(
                specialty_name="SoulRenderer",
                task=f"""
                Create (or update) 'web/src/routes/SystemSoulPage.tsx'.
                
                DESIGN MANDATE:
                {soul_description}
                
                REQUIREMENTS:
                - Use Tailwind CSS.
                - Use Framer Motion for 'breathing' animations.
                - Display the list of Committee Members who contributed.
                - Make it look 'Sovereign' and 'Premium'.
                """,
                kb=self.icgl.kb,
            )

            # 4. Save the Code (via Engineer logic, but here we might simulate)
            # CodeSpecialist returns FileChanges. We should execute them.
            if render_result.file_changes:
                for change in render_result.file_changes:
                    print(f"   💾 Writing Soul File: {change.path}")
                    # In a real run, we'd use os.open, here we trust the script runner or Engineer
                    import os

                    # Ensure dir exists
                    os.makedirs(os.path.dirname(change.path), exist_ok=True)
                    with open(change.path, "w", encoding="utf-8") as f:
                        f.write(change.content)

            return "Soul Page Updated Successfully."

        else:
            return "❌ UI Agent not found or missing capability."

    # End of Class
