"""
ICGL Testing Agent
==================

Automated test generation agent for comprehensive code testing.
"""

from src.core.agents.core.base import Agent, AgentResult, AgentRole, Problem
from src.core.kb.schemas import FileChange
from src.core.llm.client import LLMClient, LLMConfig
from src.core.llm.prompts import TESTING_SYSTEM_PROMPT


class TestingAgent(Agent):
    """
    Automated test generation agent.

    Generates pytest-format tests for functions and classes.
    """

    def __init__(self, llm_provider=None):
        super().__init__(agent_id="agent-testing", role=AgentRole.TESTING, llm_provider=llm_provider)
        self.llm_client = LLMClient()

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Generate comprehensive tests for given code.

        Creates:
        - Unit tests
        - Edge case tests
        - Integration tests (if applicable)
        - Pytest fixtures
        """

        # Extract code to test
        code_to_test = problem.metadata.get("code", problem.context)
        module_name = problem.metadata.get("module_name", "module")
        file_path = problem.metadata.get("file_path", "unknown")

        # Build test generation prompt
        user_prompt = f"""
        **MODULE:** {module_name}
        **FILE:** {file_path}
        
        **CODE TO TEST:**
        ```python
        {code_to_test}
        ```
        
        **TASK:**
        Generate comprehensive pytest tests:
        
        1. Unit tests for each function/method
        2. Edge cases and error scenarios
        3. Happy path and unhappy path
        4. Fixtures if needed
        5. Proper assertions
        6. Descriptive test names
        
        **Test File Path:** tests/test_{module_name}.py
        
        Ensure tests are runnable, practical, and follow pytest conventions.
        """

        # Configure LLM
        config = LLMConfig(
            model="gpt-4-turbo-preview",
            temperature=0.2,  # Slightly higher for test creativity
            json_mode=True,
            timeout=60.0,
        )

        if not self.llm_client.api_key:
            return self._fallback_result("Missing API Key for Testing.")

        # Generate tests
        raw_json = await self.llm_client.generate_json(
            system_prompt=TESTING_SYSTEM_PROMPT, user_prompt=user_prompt, config=config
        )

        # Parse response
        analysis = raw_json.get("analysis", "Tests generated successfully")
        test_files = raw_json.get("test_files", [])
        recommendations = raw_json.get("recommendations", [])
        confidence = raw_json.get("confidence_score", 0.85)

        # Convert to FileChange objects
        file_changes = []
        for test_file in test_files:
            file_changes.append(
                FileChange(
                    path=test_file.get("path", f"tests/test_{module_name}.py"),
                    content=test_file.get("content", ""),
                    action="CREATE",
                )
            )

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=recommendations,
            concerns=[],
            confidence=confidence,
            file_changes=file_changes,
        )
