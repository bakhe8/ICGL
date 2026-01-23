"""
ICGL Network - Specialized Agents
=================================

Defines specialized agents for specific domain tasks.
"""

from typing import List

from .base import Agent, AgentResult, AgentRole, FileChange, Problem


class CodeSpecialist(Agent):
    """
    The Code Specialist: Generates precise, verified code changes.

    Role: BUILDER (Specialized)
    Output: Structured FileChange objects.
    Constraint: CANNOT write to disk directly. Proposals only.
    """

    def __init__(self, agent_id: str = "agent-coder-01"):
        super().__init__(agent_id, AgentRole.SPECIALIST)

    def get_system_prompt(self) -> str:
        return (
            "You are an Elite Software Engineer for the ICGL system.\n"
            "Your Goal: Translate high-level architectural requirements into precise code implementation.\n"
            "Capabilities: You can propose file creations or modifications.\n"
            "Constraints:\n"
            "1. Output MUST be valid Python/TypeScript code.\n"
            "2. Follow strict type safety.\n"
            "3. Do not assume file existence; check context.\n"
            "4. RESPONSE FORMAT: You must enclose code in ```python or ```typescript blocks.\n"
            "5. To modify a file, use the format:\n"
            "   FILE: path/to/file.py\n"
            "   ```python\n"
            "   code content\n"
            "   ```"
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Generates code based on the problem statement.
        """
        # 1. Construct Prompt
        prompt = (
            f"TASK: {problem.title}\n"
            f"CONTEXT: {problem.context}\n"
            f"Please generate the necessary code changes."
        )

        # 2. Ask LLM
        response_text = await self._ask_llm(prompt)

        # 3. Parse Response into FileChanges
        # Simple parser for now (robust parser would use structured output)
        changes = self._parse_file_blocks(response_text)

        analysis = "Generated implementation plan based on requirements."
        if not changes:
            analysis += " (No code blocks detected - providing conceptual guide)."

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis + f"\n\n{response_text}",  # Keep raw text for context
            confidence=0.9,
            recommendations=["Review generated code", "Run unit tests"],
            concerns=["Requires manual review of logic"],
            file_changes=changes,
            trigger="Code generation requested for idea.",
            impact="Proposes specific file changes to implement the idea.",
        )

    def _parse_file_blocks(self, text: str) -> List[FileChange]:
        """
        Extracts file paths and content from LLM output.
        Heuristic: Look for "FILE: <path>" followed by code block.
        """
        changes = []
        lines = text.split("\n")
        current_file = None
        current_code = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("FILE:"):
                current_file = line.strip().split("FILE:")[1].strip()
                continue

            if line.strip().startswith("```") and not in_code_block:
                in_code_block = True
                current_code = []
                continue

            if line.strip().startswith("```") and in_code_block:
                in_code_block = False
                if current_file:
                    changes.append(
                        FileChange(
                            path=current_file, content="\n".join(current_code), mode="w"
                        )
                    )
                    current_file = None
                continue

            if in_code_block:
                current_code.append(line)

        return changes
