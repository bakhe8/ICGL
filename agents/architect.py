"""
Consensus AI — Architect Agent
===============================

Analyzes structural implications of decisions.
Focuses on cohesion, coupling, and long-term maintainability.
Uses Real LLM (via LLMClient) for intelligence, governed by strict JSON schemas.
"""

from agents.base import Agent, AgentRole, Problem, AgentResult
from core.client import LLMClient, LLMConfig
from core.prompts import build_architect_user_prompt, ARCHITECT_SYSTEM_PROMPT, JSONParser
from core.context import ContextBuilder # Cycle 8

class ArchitectAgent(Agent):
    """
    Architectural analysis agent.
    Checks for:
    - Coupling/Cohesion
    - System boundaries
    - Strategic optionality (P-CORE-01)
    """
    
    def __init__(self, llm_provider=None):
        # We ignore passed provider for now and use our robust LLMClient
        super().__init__(agent_id="agent-architect", role=AgentRole.ARCHITECT, llm_provider=llm_provider)
        self.llm_client = LLMClient()
        self.context_builder = ContextBuilder(".")

    def get_system_prompt(self) -> str:
        """
        Injects the Map into the default Architect Prompt.
        """
        try:
            repo_map = self.context_builder.generate_map(max_depth=3)
        except Exception:
            repo_map = "(Map generation failed)"
            
        return f"{ARCHITECT_SYSTEM_PROMPT}\n\n📡 REPOSITORY MAP:\n{repo_map}"
        
    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Runs the LLM-based architectural analysis.
        Strictly governed:
        - Timeout enforced
        - JSON only
        - No side effects
        """
        
        # 1. Build Context (Read-Only)
        context = problem.context
        decision = problem.metadata.get("decision", "N/A")
        
        # 1.5 Recall Institutional Memory
        recalled_items = await self.recall(f"{problem.title} {context}", limit=3)
        if recalled_items:
            context += "\n\nInstitutional Memory (Relevant Past Decisions/Policies):\n"
            for item in recalled_items:
                context += f"- {item}\n"
        
        # 2. Construct Prompt
        user_prompt = build_architect_user_prompt(
             title=problem.title, 
             context=context, 
             decision=decision
        )
        
        # 3. Configure Safe Execution
        config = LLMConfig(
            model="gpt-4-turbo-preview",
            temperature=0.0, # Deterministic
            timeout=45.0,     # Explicit timeout
            max_tokens=2000,
            json_mode=True
        )
        
        # 4. Execute LLM Call (Exceptions caught by Base Class Shield)
        if not self.llm_client.api_key:
            return self._fallback_result("Missing OPENAI_API_KEY. Cannot run real agent.")

        raw_json = await self.llm_client.generate_json(
            system_prompt=ARCHITECT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            config=config
        )
        
        # 5. Parse & Validate
        parsed = JSONParser.parse_architect_output(raw_json)
        
        # 6. Convert to Schema Objects
        from kb.schemas import FileChange
        file_changes_objs = []
        if hasattr(parsed, "file_changes"):
            for fc in parsed.file_changes:
                file_changes_objs.append(
                    FileChange(
                        path=fc["path"],
                        content=fc["content"],
                        action=fc.get("action", "CREATE")
                    )
                )

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=parsed.analysis,
            recommendations=parsed.recommendations,
            concerns=parsed.risks,
            confidence=parsed.confidence_score,
            file_changes=file_changes_objs
        )
