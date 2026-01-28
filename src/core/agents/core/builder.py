"""
Consensus AI — Builder Agent
============================

Specialized agent for Cycle 7 (Physical Construction) and Cycle 9 (Runtime Integration).
Translates a human decision into concrete FileChange objects.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List

from src.core.agents.core.base import Agent, AgentResult, AgentRole, Problem
from src.core.kb.schemas import FileChange as AgentFileChange
from src.core.llm.client import LLMClient, LLMConfig
from src.core.llm.prompts import BUILDER_SYSTEM_PROMPT, JSONParser


class BuilderAgent(Agent):
    def __init__(self, llm_provider=None):
        super().__init__(agent_id="agent-builder", role=AgentRole.BUILDER, llm_provider=llm_provider)
        self.llm_client = LLMClient()

    def _learn_patterns(self, target_file_path: str) -> dict:
        """Learn coding patterns from existing files in the target directory."""
        try:
            target_path = Path(target_file_path)
            target_dir = target_path.parent if target_path.suffix else target_path

            pattern_hints: Dict[str, Any] = {
                "common_imports": [],
                "naming_style": "unknown",
                "has_docstrings": False,
            }

            if not target_dir.exists():
                return pattern_hints

            python_files = list(target_dir.glob("*.py"))[:3]

            for file_path in python_files:
                try:
                    content = file_path.read_text(encoding="utf-8")

                    import_lines: List[str] = [
                        line.strip() for line in content.split("\n") if line.strip().startswith(("import ", "from "))
                    ]
                    pattern_hints["common_imports"].extend(import_lines[:5])

                    if '"""' in content or "'''" in content:
                        pattern_hints["has_docstrings"] = True

                except Exception:
                    continue

            pattern_hints["common_imports"] = list(set(pattern_hints["common_imports"]))[:10]

            return pattern_hints
        except Exception as e:
            return {"error": str(e)}

    def _verify_output(self, file_changes) -> tuple[bool, list[str]]:
        """Verify generated code for syntax validity."""
        issues = []

        for fc in file_changes:
            if fc.get("action") == "DELETE":
                continue

            content = fc.get("content", "")
            file_path = fc.get("path", "unknown")

            if not file_path.endswith(".py"):
                continue

            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(f"{file_path}: Syntax error at line {e.lineno}: {e.msg}")
            except Exception as e:
                issues.append(f"{file_path}: Parse error: {str(e)}")

        is_valid = len(issues) == 0
        return is_valid, issues

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        decision = problem.metadata.get("decision", "N/A")

        # STEP 1: Learn patterns from target files
        target_files = problem.metadata.get("target_files", [])
        pattern_hints = {}
        if target_files:
            pattern_hints = self._learn_patterns(target_files[0])

        pattern_text = ""
        if pattern_hints and "error" not in pattern_hints:
            imports_text = "\n".join(pattern_hints.get("common_imports", [])[:5])
            pattern_text = f"""
**CODING PATTERNS FROM EXISTING FILES:**
Common imports: {imports_text}
Has docstrings: {pattern_hints.get("has_docstrings", False)}

Follow these patterns in your generated code.
"""

        user_prompt = f"""
        **PROPOSED DECISION**: {decision}
        **CONTEXT**: {problem.context}
        {pattern_text}
        
        Translate this decision into concrete code changes or file creations.
        If the decision doesn't require filesystem changes, return empty list.
        """

        config = LLMConfig(model="gpt-4-turbo-preview", temperature=0.0, json_mode=True)

        if not self.llm_client.api_key:
            return self._fallback_result("Missing API Key for Builder.")

        # STEP 2: Generate code (with retry on verification failure)
        max_attempts = 2
        verification_issues = []

        for attempt in range(max_attempts):
            raw_json, usage = await self.llm_client.generate_json(
                system_prompt=BUILDER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                config=config,
            )

            # Update Budget Tracking
            current_tokens = problem.metadata.get("total_tokens", 0)
            problem.metadata["total_tokens"] = current_tokens + usage.get("total_tokens", 0)
            problem.metadata["last_agent_tokens"] = usage.get("total_tokens", 0)

            parsed = JSONParser.parse_specialist_output(raw_json)

            # STEP 3: Verify output
            file_changes_list = parsed.file_changes if isinstance(parsed.file_changes, list) else []
            is_valid, issues = self._verify_output(file_changes_list)

            if is_valid:
                break  # Success!

            verification_issues = issues

            # Retry with error feedback
            if attempt < max_attempts - 1:
                user_prompt += "\n\n**PREVIOUS ATTEMPT HAD ERRORS:**\n"
                user_prompt += "\n".join(f"- {issue}" for issue in issues)
                user_prompt += "\n\nPlease fix these errors and try again."

        # Map parsed file change dicts into Agent's FileChange dataclass
        file_changes_objs: List[AgentFileChange] = []
        for fc in file_changes_list:
            raw_action = (fc.get("action", "CREATE") or "CREATE").upper()
            # Map action semantics to FileChange.action (CREATE|UPDATE|DELETE)
            action_type = "UPDATE"
            if raw_action == "CREATE":
                action_type = "CREATE"
            elif raw_action == "DELETE":
                action_type = "DELETE"

            file_changes_objs.append(
                AgentFileChange(path=fc.get("path", ""), content=fc.get("content", ""), action=action_type)  # type: ignore
            )

        # Add verification report to references (AgentResult has no 'metadata' field)
        verification_note = f"verification_passed={len(verification_issues) == 0}; issues={len(verification_issues)}"
        pattern_note = f"pattern_hints_used={bool(pattern_hints)}"

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=(getattr(parsed, "analysis", "")),
            recommendations=["Apply code changes as requested."],
            concerns=verification_issues if verification_issues else [],
            confidence=getattr(parsed, "confidence_score", 0.0),
            file_changes=file_changes_objs,
            references=[verification_note, pattern_note],
        )
