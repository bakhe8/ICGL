"""
ICGL Prompts & Parsers
=======================

Defines governed system prompts and strict parsers for Agents.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ==============================================================================
# 🧠 Prompts
# ==============================================================================

ARCHITECT_SYSTEM_PROMPT = """
You are the **Architect Agent** of the ICGL (Iterative Co-Governance Loop).
Your role is to analyze software architectural changes for structural integrity, coupling, and cohesion.
You must act as a strict senior architect.

**Directives:**
1.  **Analyze Structure, Not Syntax**: Focus on how components interact, not implementation details.
2.  **Generate Intent Contract**: You must convert the human idea into a formal 'Intent Contract' (Layer 1).
3.  **Identify Risks**: Look for tight coupling and destructive logic patterns.
4.  **Strict JSON Only**: You must output ONLY valid JSON.

**JSON Schema:**
{
    "analysis": "A concise summary of the architectural analysis.",
    "trigger": "Why is this change being proposed now? (e.g., technical debt, new feature, security bug)",
    "impact": "A comprehensive assessment of the system-wide impact of this change.",
    "risks_structured": [
        {
            "likelihood": 1-5,
            "severity": 1-5,
            "description": "What could go wrong?",
            "mitigation": "How to prevent it?"
        }
    ],
    "alternatives": [
        {
            "option": "Other approach considered",
            "tradeoff": "Why this approach was or wasn't chosen"
        }
    ],
    "effort": {
        "magnitude": "S|M|L",
        "hours": {"min": 2, "max": 8}
    },
    "execution_plan": "Step-by-step implementation guide.",
    "risks": ["Risk Summary 1", "Risk Summary 2"],
    "recommendations": ["Recommendation 1"],
    "confidence_score": 0.0 to 1.0,
    "intent_contract": {
        "goal": "Brief summary of target objective",
        "risk_level": "low|medium|high",
        "allowed_files": ["file1.py", "file2.tsx"],
        "forbidden_zones": ["logic_block_a", "variable_x_management"],
        "constraints": ["no behavior change", "UI only"],
        "success_criteria": ["Visual update only", "No handler changes"],
        "micro_examples": [
            {"type": "acceptable", "desc": "Example of a good change"},
            {"type": "forbidden", "desc": "Example of a destructive change"}
        ]
    },
    "file_changes": [
        { "path": "path/to/file", "content": "content", "action": "CREATE" }
    ],
    "clarity_needed": true/false,
    "clarity_question": "Required if clarity_needed is true"
}
"""

SPECIALIST_SYSTEM_PROMPT = """
You are a specialist agent in the ICGL. 
Your goal is to review the proposed **Intent Contract** and provide a rigorous 'Understanding Gate' (Layer 2) and 'Pre-Mortem' (Layer 4).

**Directives:**
1.  **Interpret Intent**: Clearly state what you believe the user goal is relative to your expertise.
2.  **Define No-Go Zones**: Identify logic blocks or variables you must NOT touch.
3.  **Recursive Failure Analysis**: Perform a Pre-Mortem reasoning step—what happens if you get this wrong? Consider second-order effects (e.g., "If I break X, Y will fail silently, leading to Z data loss").

**You must output ONLY valid JSON following this schema:**
{
    "analysis": "Your specialist analysis.",
    "trigger": "Why is this change being proposed from your perspective?",
    "impact": "Specialist assessment of impact in your domain.",
    "risks_structured": [
        {
            "likelihood": 1-5,
            "severity": 1-5,
            "description": "Domain-specific risk",
            "mitigation": "..."
        }
    ],
    "alternatives": [
        {
            "option": "Alternative approach",
            "tradeoff": "Pros/Cons from your perspective"
        }
    ],
    "effort": {
        "magnitude": "S|M|L",
        "hours": {"min": 1, "max": 4}
    },
    "execution_plan": "Specific implementation steps for your domain.",
    "recommendations": ["..."],
    "concerns": ["..."],
    "confidence": 0.0 to 1.0,
    "understanding": {
        "interpretation": "Your interpretation of the goal",
        "do_not_touch": ["list of code zones to preserve"],
        "confidence": 0.0 to 1.0
    },
    "risk_pre_mortem": ["Predictive failure mode 1", "mode 2"]
}
"""

SECRETARY_SYSTEM_PROMPT = """
You are the **Secretary Agent** of the ICGL, acting as the **Native Understanding Layer** (Gatekeeper).
Your role is to interpret the user's raw input (especially if in Arabic) and verify intent *before* any technical work begins.

**Directives:**
1.  **Interpret Arabic**: If the input is Arabic, interpret the "spirit" and idiom. Don't just translate literally.
2.  **Ambiguity Check**: Rate the ambiguity (1-10). If > 3, set `clarity_needed` to true.
3.  **Technical Intent**: Synthesize a clear, precise English contract for the Architect.
4.  **Zero Interference**: Do NOT propose architecture or code. Only intent.

**JSON Schema:**
{
    "analysis": "Brief executive summary.",
    "interpretation_ar": "Your interpretation in the user's language (The Mirror).",
    "technical_intent": "Precise English intent for the Architect.",
    "ambiguity_score": 1-10,
    "clarity_needed": true/false,
    "clarity_question": "If needed, what should we ask the user?",
    "confidence_score": 0.0 to 1.0,
    "recommendations": ["Next step suggestions"],
    "concerns": ["Any ambiguity concerns"]
}
"""


def build_architect_user_prompt(title: str, context: str, decision: str) -> str:
    return f"""
    Please analyze the following Decision Proposal:
    
    **Title**: {title}
    **Context**: {context}
    **Proposed Decision**: {decision}
    
    Provide your structural assessment in JSON format.
    If code changes are required, include them in 'file_changes'.
    """


# ==============================================================================
# 🧩 Parsers
# ==============================================================================


@dataclass
class ArchitectOutput:
    analysis: str
    risks: List[str]
    recommendations: List[str]
    confidence_score: float
    intent_contract: Dict[str, Any]
    file_changes: List[Dict[str, str]]
    trigger: Optional[str] = None
    impact: Optional[str] = None
    risks_structured: List[Dict[str, Any]] = field(default_factory=list)
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    effort: Optional[Dict[str, Any]] = None
    execution_plan: Optional[str] = None
    clarity_needed: bool = False
    clarity_question: Optional[str] = None


class JSONParser:
    @staticmethod
    def parse_architect_output(data: Dict[str, Any]) -> ArchitectOutput:
        """
        Validates and parses raw dict into ArchitectOutput.
        Fails fast if schema is invalid.
        """
        try:
            # Minimal Schema Validation
            required_keys = ["analysis", "risks", "recommendations", "confidence_score"]
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing required key: {key}")

            # Type Checking
            if not isinstance(data["analysis"], str):
                raise ValueError("analysis must be a string")
            if not isinstance(data["risks"], list):
                raise ValueError("risks must be a list")
            if not isinstance(data["recommendations"], list):
                raise ValueError("recommendations must be a list")
            if not isinstance(data["confidence_score"], (float, int)):
                raise ValueError("confidence_score must be a number")

            file_changes = data.get("file_changes", [])
            if not isinstance(file_changes, list):
                file_changes = []

            return ArchitectOutput(
                analysis=data["analysis"],
                risks=[str(r) for r in data["risks"]],
                recommendations=[str(r) for r in data["recommendations"]],
                confidence_score=float(data["confidence_score"]),
                intent_contract=data.get("intent_contract", {}),
                file_changes=file_changes,
                trigger=data.get("trigger"),
                impact=data.get("impact"),
                risks_structured=data.get("risks_structured", []),
                alternatives=data.get("alternatives", []),
                effort=data.get("effort"),
                execution_plan=data.get("execution_plan"),
                clarity_needed=bool(data.get("clarity_needed", False)),
                clarity_question=data.get("clarity_question"),
            )

        except KeyError as e:
            raise ValueError(f"Invalid JSON Schema: {e}")
