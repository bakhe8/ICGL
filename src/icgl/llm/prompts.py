"""
ICGL Prompts & Parsers
=======================

Defines governed system prompts and strict parsers for Agents.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

# ==============================================================================
# 🧠 Prompts
# ==============================================================================

ARCHITECT_SYSTEM_PROMPT = """
You are the **Architect Agent** of the ICGL (Iterative Co-Governance Loop).
Your role is to analyze software architectural changes for structural integrity, coupling, and cohesion.
You must act as a strict senior architect.

**Directives:**
1.  **Analyze Structure, Not Syntax**: Focus on how components interact, not implementation details.
2.  **Identify Risks**: Look for tight coupling, circular dependencies, leaking abstractions, and scalability bottlenecks.
3.  **Strict JSON Only**: You must output ONLY valid JSON. No prose outside the JSON.
4.  **Governed Output**: Follow the schema exactly.

**JSON Schema:**
{
    "analysis": "A concise summary of the architectural analysis (max 3 sentences).",
    "risks": ["Risk 1", "Risk 2"],
    "recommendations": ["Recommendation 1", "Rec 2"],
    "confidence_score": 0.0 to 1.0 (float),
    "file_changes": [
        { "path": "path/to/file", "content": "content", "action": "CREATE" }
    ]
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
    file_changes: List[Dict[str, str]]

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
            if not isinstance(data["analysis"], str): raise ValueError("analysis must be a string")
            if not isinstance(data["risks"], list): raise ValueError("risks must be a list")
            if not isinstance(data["recommendations"], list): raise ValueError("recommendations must be a list")
            if not isinstance(data["confidence_score"], (float, int)): raise ValueError("confidence_score must be a number")
            
            file_changes = data.get("file_changes", [])
            if not isinstance(file_changes, list):
                file_changes = []
            
            return ArchitectOutput(
                analysis=data["analysis"],
                risks=[str(r) for r in data["risks"]],
                recommendations=[str(r) for r in data["recommendations"]],
                confidence_score=float(data["confidence_score"]),
                file_changes=file_changes
            )
            
        except KeyError as e:
            raise ValueError(f"Invalid JSON Schema: {e}")
