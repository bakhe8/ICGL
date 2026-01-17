"""
Intent Decomposer
-----------------

LLM-powered intent understanding and decomposition.
Transforms natural language into structured execution plans.

CRITICAL: This layer ONLY understands and plans - it does NOT execute.
All execution goes through GBE/ICGL/Sentinel/HDAL for governance.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import json
from ..llm.client import LLMClient, LLMConfig


@dataclass
class IntentStep:
    """Represents a single step in an execution plan."""
    type: str  # bind_policy, unbind_policy, query_binding_state, run_analysis, etc.
    params: Dict[str, Any]
    risk_level: str  # low, medium, high
    requires_approval: bool = False


@dataclass
class DecomposedPlan:
    """A structured plan decomposed from natural language."""
    intents: List[IntentStep]
    confidence: float
    requires_clarification: bool = False
    clarification_question: Optional[str] = None
    suggested_sequence: Optional[List[int]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intents": [asdict(i) for i in self.intents],
            "confidence": self.confidence,
            "requires_clarification": self.requires_clarification,
            "clarification_question": self.clarification_question,
            "suggested_sequence": self.suggested_sequence
        }


class IntentDecomposer:
    """
    Uses LLM to decompose natural language into structured execution plans.
    
    Responsibilities:
    - Understand user intent
    - Decompose complex/compound intents
    - Annotate risk levels
    - Detect ambiguity
    
    NOT Responsible For:
    - Execution (that's GBE's job)
    - State mutation
    - Policy validation
    """
    
    SYSTEM_PROMPT = """You are an intent parser for the ICGL governance system. Your job is to understand user requests and decompose them into structured execution plans.

AVAILABLE INTENT TYPES:
- bind_policy: Bind a policy to an ADR (params: codes, target_adr)
- unbind_policy: Remove a policy binding (params: codes, target_adr)
- query_binding_state: Query what policies are bound to an ADR (params: target)
- query_count: Count policies/ADRs (params: target, query_type)
- query_adr: Retrieve ADR details (params: target)
- run_analysis: Create and analyze a new decision (params: mode)
- self_diagnose: Ask the system to diagnose itself and suggest improvements (params: none)
- ack_recommendations: Accept/reject diagnostic recommendations (params: action)
- conversational: General question/conversation (params: message)
- approve: Approve a decision (params: adr_id)
- reject: Reject a decision (params: adr_id)

RISK LEVELS:
- low: Read-only queries (query_*, conversational)
- low: Diagnostics (self_diagnose)
- medium: State changes that are reversible (bind_policy)
- high: Irreversible actions (unbind_policy, approve, reject)

RULES:
1. Extract ALL intents from the message (may be multiple)
2. Annotate risk_level for each intent
3. Set requires_approval=true for high-risk intents
4. If the user's request is ambiguous or lacks required information, set requires_clarification=true and provide a clarification_question
5. Use suggested_sequence to order multi-step intents logically
6. Extract EXACT entity IDs (e.g., ADR-001, P-CORE-01) from the message
7. Output ONLY valid JSON, no other text

CRITICAL: You do NOT execute anything. You only understand and plan.

OUTPUT SCHEMA (JSON):
{
  "intents": [
    {
      "type": "bind_policy",
      "params": {"codes": "P-CORE-01", "target_adr": "ADR-001"},
      "risk_level": "medium",
      "requires_approval": false
    }
  ],
  "confidence": 0.95,
  "requires_clarification": false,
  "clarification_question": null,
  "suggested_sequence": [0]
}"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.config = LLMConfig(
            model="gpt-4-turbo-preview",
            temperature=0.0,
            max_tokens=1500,
            json_mode=True
        )
    
    async def decompose(self, message: str) -> DecomposedPlan:
        """
        Decompose natural language message into structured plan.
        
        Args:
            message: User's natural language request
            
        Returns:
            DecomposedPlan with structured intents
            
        Raises:
            RuntimeError: If LLM fails or returns invalid JSON
        """
        try:
            user_prompt = f"USER MESSAGE: {message}\n\nOUTPUT (JSON):"
            
            response = await self.llm_client.generate_json(
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=user_prompt,
                config=self.config
            )
            
            # Validate and construct DecomposedPlan
            intents_data = response.get("intents", [])
            intents = [
                IntentStep(
                    type=intent["type"],
                    params=intent.get("params", {}),
                    risk_level=intent.get("risk_level", "medium"),
                    requires_approval=intent.get("requires_approval", False)
                )
                for intent in intents_data
            ]
            
            plan = DecomposedPlan(
                intents=intents,
                confidence=response.get("confidence", 0.0),
                requires_clarification=response.get("requires_clarification", False),
                clarification_question=response.get("clarification_question"),
                suggested_sequence=response.get("suggested_sequence", list(range(len(intents))))
            )
            
            return plan
            
        except Exception as e:
            # Fallback: treat as conversational if LLM fails
            return DecomposedPlan(
                intents=[
                    IntentStep(
                        type="conversational",
                        params={"message": message},
                        risk_level="low",
                        requires_approval=False
                    )
                ],
                confidence=0.0,
                requires_clarification=False
            )
    
    def validate_plan(self, plan: DecomposedPlan) -> tuple[bool, Optional[str]]:
        """
        Validate that the plan conforms to governance rules.
        
        Returns:
            (is_valid, error_message)
        """
        if not plan.intents:
            return False, "Plan contains no intents"
        
        for intent in plan.intents:
            if not intent.type:
                return False, "Intent missing type"
            
            # Validate required params for each type
            if intent.type in ["bind_policy", "unbind_policy"]:
                if "codes" not in intent.params:
                    return False, f"{intent.type} requires 'codes' parameter"
            
            if intent.type in ["query_binding_state", "query_adr"]:
                if "target" not in intent.params:
                    return False, f"{intent.type} requires 'target' parameter"

            if intent.type == "self_diagnose" and intent.params:
                return False, "self_diagnose should not include params"

            if intent.type == "ack_recommendations":
                if "action" not in intent.params:
                    return False, "ack_recommendations requires 'action' parameter"
        
        return True, None
