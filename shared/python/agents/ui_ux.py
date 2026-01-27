"""
Consensus AI — UI/UX Agent
==========================

Specialized in user experience, interface consistency, and accessibility.
Ensures that frontend changes align with usability standards and project aesthetics.
"""

from typing import Any, Optional

from shared.python.agents.base import Agent, AgentResult, AgentRole, Problem


class UIUXAgent(Agent):
    """
    The UI/UX Agent: Manages the 'Perception Gate'.
    Phase 5 Sovereign Demand fulfillment.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="agent-uiux",
            role=AgentRole.UI_UX,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Sovereign UI Analysis: Perceives topology and orchestrates via Builder.
        """
        # 1. UI Topology Perception (Awareness Layer)
        # This provides the agent with a 'mental map' of the existing interfaces.
        ui_map = """
        CURRENT UI TOPOLOGY (Perception Gate):
        - Routes: 
            - /app/cockpit (CockpitPage.tsx): The Sovereign Hub dashboard.
            - /app/mind (MindPage.tsx): Knowledge retrieval and mind map.
            - /app/timeline (TimelinePage.tsx): System event stream.
            - /app/agents-flow (AgentsFlowPage): Autonomous coordination visualization.
        - High-Fidelity Components:
            - CouncilPulse.tsx: Real-time peer consultation visualization.
            - SecretaryLogsWidget.tsx: Executive relay log display.
        - Global Design:
            - index.css: Glassmorphic tokens and Sovereign glow effects.
        """

        # 2. Institutional Perception
        ui_history = ""
        try:
            steward_res = await self.consult_peer(
                AgentRole.STEWARD,
                title="UI Evolution Retrieval",
                context="What are the most recent changes to the system CSS or Dashboard components?",
                kb=kb,
            )
            ui_history = steward_res.analysis if steward_res else "No recent UI records found."
        except Exception:
            ui_history = "Institutional memory unreachable."

        prompt = f"""
        You are the Sovereign UI/UX Agent (Design Auditor).
        
        YOUR PERCEPTION OF THE CODEBASE:
        {ui_map}
        
        INSTITUTIONAL MEMORY:
        {ui_history}
        
        CURRENT PROBLEM:
        Title: {problem.title}
        Context: {problem.context}
        
        RULES:
        1. You are the architect, NOT the builder. You DO NOT write code.
        2. If you identify a design gap, you must formulate a 'Design Mandate' for the Builder Agent.
        3. Reference specific routes or components from your 'Perception Gate'.
        
        TASKS:
        - Identify if the request aligns with the current 'Sovereign' aesthetics.
        - Propose exact UI/UX refinements.
        - If changes are needed, explicitly state 'DESIGN MANDATE FOR BUILDER: [details]'.
        """

        from shared.python.llm.client import LLMClient, LLMConfig
        from shared.python.llm.prompts import JSONParser

        client = LLMClient()
        config = LLMConfig(temperature=0.2, json_mode=True)

        try:
            raw_json, usage = await client.generate_json(
                system_prompt=prompt,  # Using prompt as system here since it's pre-formatted
                user_prompt=f"Perform UI Audit for: {problem.title}",
                config=config,
            )
        except Exception as e:
            return self._fallback_result(str(e))

        parsed = JSONParser.parse_specialist_output(raw_json)
        analysis = parsed.get("analysis", "")

        # 3. Action Redirection (Phase 8.1: Implementation via Builder)
        if "DESIGN MANDATE" in analysis.upper():
            print(f"   🎨 [{self.agent_id}] Issuing Design Mandate to Builder Agent...")
            # Council Directive: Fast Track for CSS/UI updates
            fast_track_context = f"""
            The UI/UX Auditor has identified a design gap based on current topology. 
            ANALYSIS: {analysis}
            
            GOVERNANCE OVERRIDE: 
            - Risk Level: LOW (Visual Only)
            - Path: FAST_TRACK (Direct Builder Execution)
            """

            await self.consult_peer(
                AgentRole.BUILDER,
                title="Design Mandate: UI Enhancement",
                context=fast_track_context,
                kb=kb,
            )

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=parsed.get("recommendations")
            or [
                "Ensure glassmorphic layers maintain accessibility focus",
                "Verify visual links in CouncilPulse after any routing change",
                "Audit cognitive load on the CockpitPage regularly",
            ],
            concerns=parsed.get("concerns") or [],
            confidence=max(0.0, min(1.0, parsed.get("confidence", 0.95))),
            metadata=parsed.get("metadata", {}),
        )

    async def spawn_specialist(self, specialty_name: str, task: str, kb: Any) -> AgentResult:
        """
        Dynamically generates a specialized sub-agent (Assistant) for specific UI tasks.
        User Request fulfillment: 'Generate specialized assistants for UIUXAgent'.
        """
        print(f"   🪄 [{self.agent_id}] Spawning Specialist: {specialty_name}...")

        from .specialists import CodeSpecialist

        # Instantiate a generic specialist
        specialist = CodeSpecialist(agent_id=f"specialist-{specialty_name.lower()}")
        specialist.llm = self.llm  # Share the same cognitive engine

        # Override System Prompt to be Domain-Specific
        original_prompt = specialist.get_system_prompt()
        definition = f"""
        YOU ARE NOW THE {specialty_name.upper()}.
        You are a sub-specialist of the UI/UX Agent.
        
        YOUR MANDATE:
        {task}
        
        INHERITED CONSTRAINTS:
        {original_prompt}
        """

        # We need to Monkey-Patch or Wrap the get_system_prompt to return our new definition
        # Since get_system_prompt is a method, we can just assign a lambda
        specialist.get_system_prompt = lambda: definition  # type: ignore

        # Run the specialist
        problem = Problem(title=f"Specialist Task: {specialty_name}", context=task)

        return await specialist.analyze(problem, kb)
