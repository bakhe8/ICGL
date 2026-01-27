from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ArchitectOutput:
    analysis: str = ""
    recommendations: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    file_changes: List[Dict[str, Any]] = field(default_factory=list)
    intent_contract: Optional[Dict[str, Any]] = None
    risks_structured: List[Dict[str, Any]] = field(default_factory=list)
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    effort: Dict[str, Any] = field(default_factory=dict)
    execution_plan: Optional[str] = None
    clarity_needed: bool = False
    clarity_question: Optional[str] = None
    trigger: Optional[str] = None
    impact: Optional[str] = None
    required_agents: List[str] = field(default_factory=list)
    summoning_rationale: Optional[str] = None


@dataclass
class SpecialistOutput:
    analysis: str = ""
    recommendations: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_changes: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0  # Builder uses this instead of confidence sometimes


ARCHITECT_SYSTEM_PROMPT = """
You are the **Lead Architect Agent** of the ICGL (Integrated Consensus Governance Layer).
Your mission is to analyze proposals for structural integrity, technical debt, and architectural alignment.

**Directives:**
1. **P-CORE-01 Strategic Optionality**: Prioritize designs that keep doors open. Avoid vendor lock-in or premature optimization.
2. **P-ARCH-01 Cohesion & Coupling**: Ensure high cohesion within modules and loose coupling between them.
3. **Institutional Memory**: Integrate lessons from the Knowledge Steward to avoid past mistakes.

**Output Schema:**
- analysis: Deep structural reasoning.
- recommendations: Specific, actionable architectural changes.
- risks_structured: Formal risk assessment (likelihood/impact).
- intent_contract: Technical constraints and success criteria for implementation.
"""

BUILDER_SYSTEM_PROMPT = """
You are the **Builder Agent** of the ICGL.
Your goal is to transform architectural intent into high-quality code.

**CRITICAL: File Modification vs Creation**
- IF the context shows existing file content -> PRESERVE all code except what needs changing.
- IF creating new file -> Generate complete fresh code.
- ALWAYS output the FULL file content in the "content" field.

**Directives:**
1. **Surgical Edits**: Change ONLY what's requested, preserve comments and structure.
2. **Strict Schema**: Output ONLY valid JSON.
3. **Safety**: Ensure paths are relative to project root.
"""

TESTING_SYSTEM_PROMPT = """
You are the **Testing Agent** of the ICGL system.
Your mission is to generate comprehensive, production-ready tests using pytest.
Focus on unit tests, edge cases, and regression prevention.
"""

VERIFICATION_SYSTEM_PROMPT = """
You are the **Verification Agent** of the ICGL system.
Perform deep analysis beyond syntax checking: Security, Quality, Type Safety, and Performance.
"""

DOCUMENTATION_SYSTEM_PROMPT = """
You are the **Documentation Agent** of the ICGL system.
Create COMPREHENSIVE, PRODUCTION-READY documentation covering installation, API, and architecture.
"""

SPECIALIST_SYSTEM_PROMPT = """
You are a **Specialist Agent** of the ICGL system.
Your mission is to provide expert analysis from your specific perspective.
"""

FAILURE_SYSTEM_PROMPT = """
You are the **Failure Agent** of the ICGL system.
Your mission is to perform a Pre-Mortem on every proposal. 
Ask: "How will this fail?" Scan for edge cases, security holes, and operational fragility.
"""


class JSONParser:
    @staticmethod
    def parse(text: str) -> dict:
        """Robustly parse JSON from LLM output."""
        import json
        import re

        try:
            # Look for JSON block
            match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                text = match.group(1)

            # Basic cleanup
            text = text.strip()
            return json.loads(text)
        except Exception:
            # Fallback: try to find anything that looks like a dict
            try:
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            except Exception:
                pass
            return {}

    @staticmethod
    def parse_architect_output(data: Any) -> ArchitectOutput:
        """Parses LLM output into ArchitectOutput dataclass."""
        if isinstance(data, str):
            data = JSONParser.parse(data)

        if not isinstance(data, dict):
            return ArchitectOutput(analysis=str(data))

        return ArchitectOutput(
            analysis=data.get("analysis", ""),
            recommendations=data.get("recommendations", []),
            risks_structured=data.get("risks_structured", []),
            alternatives=data.get("alternatives", []),
            effort=data.get("effort", {}),
            execution_plan=data.get("execution_plan"),
            clarity_needed=data.get("clarity_needed", False),
            clarity_question=data.get("clarity_question"),
            trigger=data.get("trigger"),
            impact=data.get("impact"),
            required_agents=data.get("required_agents", []),
            summoning_rationale=data.get("summoning_rationale"),
            intent_contract=data.get("intent_contract"),
            confidence_score=float(data.get("confidence_score", 0.0) or data.get("confidence", 0.0)),
        )

    @staticmethod
    def parse_specialist_output(data: Any) -> SpecialistOutput:
        """Parses LLM output into SpecialistOutput dataclass."""
        if isinstance(data, str):
            data = JSONParser.parse(data)

        if not isinstance(data, dict):
            return SpecialistOutput(analysis=str(data))

        return SpecialistOutput(
            analysis=data.get("analysis", ""),
            recommendations=data.get("recommendations", []),
            concerns=data.get("concerns", []),
            confidence=float(data.get("confidence", 0.0) or data.get("confidence_score", 0.0)),
            metadata=data.get("metadata", {}),
            file_changes=data.get("file_changes", []),
            confidence_score=float(data.get("confidence_score", 0.0) or data.get("confidence", 0.0)),
        )


def build_architect_user_prompt(title: str, context: str, decision: str) -> str:
    return f"""
PROPOSAL TITLE: {title}
CONTEXT: {context}
PROPOSED DECISION: {decision}

Analyze the architectural impact of this decision.
Identify risks, suggest optimal patterns, and define a technical intent contract for implementation.
Output in JSON.
"""


def build_builder_user_prompt(title: str, context: str, intent: Optional[str] = None) -> str:
    return f"""
TASK: {title}
CONTEXT: {context}
TECHNICAL INTENT: {intent or "General improvement"}

Generate the code implementation for this task.
Ensure full file content is provided for each changed file.
"""


def build_sentinel_user_prompt(title: str, context: str) -> str:
    return f"Analyze the following for operational risk: {title}\nContext: {context}"


def build_policy_user_prompt(title: str, context: str) -> str:
    return f"Audit the following for core purpose compliance: {title}\nContext: {context}"


# Aliases just in case
build_architect_prompt = build_architect_user_prompt
