"""
Clarification Handler
--------------------

Intelligent clarification question generation for COC.

Detects ambiguity and generates targeted questions to resolve it.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .intent_decomposer import DecomposedPlan, IntentStep
from .session import ConversationContext
from ..kb.llm import get_llm


class AmbiguityType(Enum):
    """Types of ambiguity that need clarification"""
    MISSING_ENTITY = "missing_entity"
    AMBIGUOUS_REFERENCE = "ambiguous_reference"
    MULTIPLE_OPTIONS = "multiple_options"
    UNCLEAR_INTENT = "unclear_intent"
    INCOMPLETE_PARAMS = "incomplete_params"


@dataclass
class Ambiguity:
    """Detected ambiguity in user message"""
    type: AmbiguityType
    description: str
    missing_info: List[str]
    suggestions: List[str] = None
    context: Dict[str, Any] = None


@dataclass
class ClarificationQuestion:
    """Generated clarification question"""
    question_id: str
    question_text: str
    ambiguity_type: AmbiguityType
    expected_entity: str
    options: Optional[List[str]] = None
    follow_up: bool = False


class ClarificationHandler:
    """
    Generates intelligent clarification questions.
    
    Uses LLM to understand what information is missing and formulate
    clear, specific questions.
    """
    
    def __init__(self):
        self.llm = get_llm()
    
    def detect_ambiguity(
        self,
        intent: Any,
        context: ConversationContext
    ) -> Optional[Ambiguity]:
        """
        Detect what information is ambiguous or missing.
        
        Returns Ambiguity object describing the problem.
        """
        # Check for missing entities
        if isinstance(intent, DecomposedPlan):
            for step in intent.steps:
                missing = self._find_missing_entities(step)
                if missing:
                    return Ambiguity(
                        type=AmbiguityType.MISSING_ENTITY,
                        description=f"Missing required information for {step.intent_type}",
                        missing_info=missing,
                        context={"step": step.to_dict()}
                    )
        
        # Check for ambiguous references
        if self._has_ambiguous_pronouns(context):
            return Ambiguity(
                type=AmbiguityType.AMBIGUOUS_REFERENCE,
                description="Unclear what 'it', 'that', or 'them' refers to",
                missing_info=["specific_reference"],
                context={"recent_entities": self._get_recent_entities(context)}
            )
        
        # Check intent decomposer results
        if isinstance(intent, DecomposedPlan) and intent.requires_clarification:
            return Ambiguity(
                type=AmbiguityType.UNCLEAR_INTENT,
                description="Multiple possible interpretations",
                missing_info=["specific_intent"],
                context={"possible_intents": intent.ambiguities}
            )
        
        return None
    
    def generate_question(
        self,
        ambiguity: Ambiguity,
        context: ConversationContext
    ) -> ClarificationQuestion:
        """
        Generate a specific clarification question.
        
        Uses LLM to create natural, targeted questions.
        """
        from ..kb.schemas import uid
        
        # Build prompt for LLM
        prompt = self._build_clarification_prompt(ambiguity, context)
        
        # Get LLM to generate question
        llm_response = self.llm.generate(
            prompt,
            max_tokens=200,
            temperature=0.7
        )
        
        question_text = llm_response.strip()
        
        # Extract options if multiple choice
        options = None
        if ambiguity.type == AmbiguityType.MULTIPLE_OPTIONS:
            options = ambiguity.suggestions or self._extract_options(ambiguity)
        
        return ClarificationQuestion(
            question_id=f"clarif_{uid()}",
            question_text=question_text,
            ambiguity_type=ambiguity.type,
            expected_entity=ambiguity.missing_info[0] if ambiguity.missing_info else "unknown",
            options=options,
            follow_up=len(context.clarification_history) > 0
        )
    
    def _build_clarification_prompt(
        self,
        ambiguity: Ambiguity,
        context: ConversationContext
    ) -> str:
        """Build LLM prompt for question generation"""
        
        base_prompt = """You are ICGL, a helpful AI assistant for code governance.
The user said something that needs clarification.

Recent conversation:
{conversation}

Problem: {problem}
Missing information: {missing}

Generate ONE clear, specific question to get the missing information.
Be friendly and conversational. Don't ask multiple questions at once.

Question:"""
        
        # Get recent messages
        recent_msgs = context.messages[-5:] if len(context.messages) > 5 else context.messages
        conversation = "\n".join([
            f"{msg.role.upper()}: {msg.content}"
            for msg in recent_msgs
        ])
        
        return base_prompt.format(
            conversation=conversation,
            problem=ambiguity.description,
            missing=", ".join(ambiguity.missing_info)
        )
    
    def _find_missing_entities(self, step: IntentStep) -> List[str]:
        """Find missing required entities in intent step"""
        required_by_intent = {
            'BIND_POLICIES': ['agents', 'policy_name'],
            'CREATE_CHANNEL': ['from_agent', 'to_agent'],
            'QUERY_KB': ['query'],
            'RUN_ANALYSIS': ['scope'],
            'QUERY_BINDINGS': [],
            'QUERY_COUNT': [],
        }
        
        intent_type = step.intent_type
        if intent_type not in required_by_intent:
            return []
        
        required = required_by_intent[intent_type]
        params = step.parameters or {}
        
        missing = []
        for entity in required:
            if entity not in params or not params[entity]:
                missing.append(entity)
        
        return missing
    
    def _has_ambiguous_pronouns(self, context: ConversationContext) -> bool:
        """Check if last message has unclear pronouns"""
        if not context.messages:
            return False
        
        last_user_msg = None
        for msg in reversed(context.messages):
            if msg.role == "user":
                last_user_msg = msg
                break
        
        if not last_user_msg:
            return False
        
        content_lower = last_user_msg.content.lower()
        pronouns = ['it', 'that', 'them', 'those', 'these']
        
        # Has pronoun but no clear antecedent
        if any(f' {p} ' in f' {content_lower} ' for p in pronouns):
            # Check if there are recent entities to refer to
            if not context.entities or all(not v for v in context.entities.values()):
                return True
        
        return False
    
    def _get_recent_entities(self, context: ConversationContext) -> Dict[str, Any]:
        """Get recently mentioned entities"""
        return context.entities or {}
    
    def _extract_options(self, ambiguity: Ambiguity) -> List[str]:
        """Extract multiple choice options from ambiguity"""
        if ambiguity.context and 'possible_intents' in ambiguity.context:
            return ambiguity.context['possible_intents']
        
        if ambiguity.context and 'recent_entities' in ambiguity.context:
            entities = ambiguity.context['recent_entities']
            # Flatten entity values
            options = []
            for values in entities.values():
                if isinstance(values, list):
                    options.extend(values)
                else:
                    options.append(str(values))
            return options[:5]  # Max 5 options
        
        return []
    
    def parse_clarification_response(
        self,
        question: ClarificationQuestion,
        response: str,
        context: ConversationContext
    ) -> Dict[str, Any]:
        """
        Parse user's response to clarification question.
        
        Returns resolved entity/value.
        """
        response_lower = response.lower().strip()
        
        # If multiple choice, match to option
        if question.options:
            # Direct match
            for i, option in enumerate(question.options):
                if response_lower == option.lower():
                    return {
                        "entity_type": question.expected_entity,
                        "value": option,
                        "confidence": "high"
                    }
            
            # Ordinal match ("first", "second", "option 1")
            ordinals = {
                'first': 0, '1': 0, 'one': 0,
                'second': 1, '2': 1, 'two': 1,
                'third': 2, '3': 2, 'three': 2,
            }
            
            for word, idx in ordinals.items():
                if word in response_lower and idx < len(question.options):
                    return {
                        "entity_type": question.expected_entity,
                        "value": question.options[idx],
                        "confidence": "high"
                    }
        
        # Free-form response
        return {
            "entity_type": question.expected_entity,
            "value": response,
            "confidence": "medium"
        }
    
    def should_give_up(self, context: ConversationContext) -> bool:
        """
        Determine if we should stop asking clarifying questions.
        
        Give up after 3 attempts to avoid annoying the user.
        """
        return len(context.clarification_history) >= 3


# Global clarification handler
_clarification_handler: Optional[ClarificationHandler] = None

def get_clarification_handler() -> ClarificationHandler:
    """Get global clarification handler instance"""
    global _clarification_handler
    if _clarification_handler is None:
        _clarification_handler = ClarificationHandler()
    return _clarification_handler
