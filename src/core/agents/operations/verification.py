"""
ICGL Verification Agent
=======================

Comprehensive code verification agent for deep analysis beyond basic syntax checking.
"""

from src.core.agents.core.base import Agent, AgentResult, AgentRole, Problem
from src.core.llm.client import LLMClient, LLMConfig
from src.core.llm.prompts import VERIFICATION_SYSTEM_PROMPT


class VerificationAgent(Agent):
    """
    Comprehensive code verification agent.

    Works with BuilderAgent to ensure code quality and security.
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            agent_id="agent-verification",
            role=AgentRole.VERIFICATION,
            llm_provider=llm_provider,
        )
        self.llm_client = LLMClient()

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Perform comprehensive code verification.

        Analyzes:
        - Security vulnerabilities
        - Code quality
        - Best practices
        - Type safety
        - Performance concerns
        """

        # Extract code from problem
        code_to_verify = problem.metadata.get("code", problem.context)
        file_path = problem.metadata.get("file_path", "unknown")

        # Build verification prompt
        user_prompt = f"""
        **FILE:** {file_path}
        
        **CODE TO VERIFY:**
        ```
        {code_to_verify}
        ```
        
        **VERIFICATION REQUEST:**
        Perform comprehensive verification:
        1. Security scan (vulnerabilities)
        2. Code quality analysis
        3. Best practices check
        4. Type safety review
        5. Performance assessment
        
        Provide detailed findings with specific line references where applicable.
        """

        # Configure LLM
        config = LLMConfig(
            model="gpt-4-turbo-preview",
            temperature=0.1,  # Low for consistency
            json_mode=True,
            timeout=60.0,
        )

        if not self.llm_client.api_key:
            return self._fallback_result("Missing API Key for Verification.")

        # Call LLM
        raw_json = await self.llm_client.generate_json(
            system_prompt=VERIFICATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            config=config,
        )

        # Parse response
        analysis = raw_json.get("analysis", "Verification completed")
        concerns = raw_json.get("concerns", [])
        recommendations = raw_json.get("recommendations", [])
        confidence = raw_json.get("confidence_score", 0.8)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=recommendations,
            concerns=concerns,
            confidence=confidence,
            file_changes=[],  # Verification doesn't modify files
        )
