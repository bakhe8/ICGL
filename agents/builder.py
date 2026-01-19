"""
Consensus AI — Builder Agent
============================

Specialized agent for Cycle 7 (Physical Construction) and Cycle 9 (Runtime Integration).
Translates a human decision into concrete FileChange objects.
"""

from agents.base import Agent, AgentRole, Problem, AgentResult
from core.client import LLMClient, LLMConfig
from core.prompts import JSONParser

BUILDER_SYSTEM_PROMPT = """
You are the **Builder Agent** of the ICGL.
Your sole purpose is to translate high-level governance decisions into concrete filesystem actions.

**Directives:**
1. **Concrete Action**: If the decision says "Create a file", you MUST generate the file content.
2. **Strict Schema**: You must output ONLY JSON following the schema.
3. **Safety**: Ensure paths are relative to the project root.

**JSON Schema:**
{
    "analysis": "Brief explanation of how you are implementing the decision.",
    "risks": ["Potential risk 1", "Risk 2"],
    "recommendations": ["Recommendation 1", "Rec 2"],
    "file_changes": [
        { "path": "relative/path/to/file", "content": "full content", "action": "CREATE|UPDATE|DELETE" }
    ],
    "confidence_score": 1.0
}
"""

class BuilderAgent(Agent):
    def __init__(self, llm_provider=None):
        super().__init__(agent_id="agent-builder", role=AgentRole.BUILDER, llm_provider=llm_provider)
        self.llm_client = LLMClient()

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        decision = problem.metadata.get("decision", "N/A")
        
        user_prompt = f"""
        **PROPOSED DECISION**: {decision}
        **CONTEXT**: {problem.context}
        
        Translate this decision into concrete code changes or file creations.
        If the decision doesn't require filesystem changes, return an empty 'file_changes' list.
        """
        
        config = LLMConfig(
            model="gpt-4-turbo-preview",
            temperature=0.0,
            json_mode=True
        )
        
        if not self.llm_client.api_key:
            return self._fallback_result("Missing API Key for Builder.")

        raw_json = await self.llm_client.generate_json(
            system_prompt=BUILDER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            config=config
        )
        
        # We reuse the Architect parser for now as the schema is compatible
        parsed = JSONParser.parse_architect_output(raw_json)
        
        from kb.schemas import FileChange
        file_changes_objs = [
            FileChange(path=fc["path"], content=fc["content"], action=fc.get("action", "CREATE"))
            for fc in parsed.file_changes
        ]

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=parsed.analysis,
            recommendations=["Apply code changes as requested."],
            concerns=[],
            confidence=parsed.confidence_score,
            file_changes=file_changes_objs
        )
