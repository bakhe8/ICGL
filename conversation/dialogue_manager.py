"""
Dialogue Manager
----------------

Manages conversation flow and dialogue state for COC.

Responsibilities:
- Track conversation phase (greeting, understanding, clarifying, etc.)
- Detect follow-ups and topic switches
- Determine when clarification is needed
- Maintain conversation coherence
- Manage multi-turn dialogues
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from .session import ConversationSession, ConversationContext, DialogueState, Message
from .intent_decomposer import DecomposedPlan, IntentStep


@dataclass
class DialogueTransition:
    """Represents a state transition in the dialogue"""
    from_state: DialogueState
    to_state: DialogueState
    reason: str
    timestamp: datetime


class DialogueManager:
    """
    Manages conversation flow and state transitions.
    
    Determines what phase the conversation is in and what should happen next.
    """
    
    def __init__(self):
        self.transition_history: List[DialogueTransition] = []
    
    def get_current_state(self, session: ConversationSession) -> DialogueState:
        """Determine current dialogue state"""
        return session.context.dialogue_state
    
    def update_state(
        self,
        session: ConversationSession,
        new_state: DialogueState,
        reason: str
    ) -> DialogueTransition:
        """Transition to a new dialogue state"""
        old_state = session.context.dialogue_state
        
        transition = DialogueTransition(
            from_state=old_state,
            to_state=new_state,
            reason=reason,
            timestamp=datetime.utcnow()
        )
        
        session.context.dialogue_state = new_state
        self.transition_history.append(transition)
        
        return transition
    
    def is_first_message(self, session: ConversationSession) -> bool:
        """Check if this is the first user message"""
        return len(session.context.messages) == 0
    
    def is_follow_up(self, message: str, context: ConversationContext) -> bool:
        """
        Detect if message is a follow-up to previous conversation.
        
        Indicators:
        - Pronouns ("it", "that", "them")
        - Continuation words ("also", "and", "additionally")
        - Reference to previous entities
        - Short responses to questions ("yes", "the first one")
        """
        message_lower = message.lower().strip()
        
        # Empty context = can't be follow-up
        if not context.messages:
            return False
        
        # Check for pronouns
        pronouns = ['it', 'that', 'this', 'them', 'those', 'these', 'he', 'she', 'they']
        if any(f' {pronoun} ' in f' {message_lower} ' or message_lower.startswith(f'{pronoun} ') 
               for pronoun in pronouns):
            return True
        
        # Check for continuation words
        continuation_words = ['also', 'additionally', 'and', 'furthermore', 'moreover']
        if any(message_lower.startswith(word) for word in continuation_words):
            return True
        
        # Check for short confirmations
        confirmations = ['yes', 'yeah', 'yep', 'ok', 'okay', 'sure', 'fine', 
                        'the first one', 'the second', 'option 1', 'option 2']
        if message_lower in confirmations:
            return True
        
        # Check if message is very short (likely answer to question)
        if len(message.split()) <= 3 and context.dialogue_state == DialogueState.CLARIFYING:
            return True
        
        return False
    
    def detect_topic_switch(self, message: str, context: ConversationContext) -> bool:
        """Detect if user is switching to a new topic"""
        message_lower = message.lower().strip()
        
        # Explicit switches
        switch_phrases = [
            'actually', 'wait', 'instead', 'never mind', 'forget that',
            'new topic', 'different question', 'change of plans'
        ]
        
        if any(phrase in message_lower for phrase in switch_phrases):
            return True
        
        # If last intent was different category and message is long
        if context.last_intent and len(message.split()) > 5:
            # Check if new message has completely different verbs/actions
            # (Simplified heuristic)
            last_intent_keywords = {'bind', 'query', 'create', 'analyze', 'review'}
            
            if context.last_intent in ['BIND_POLICIES', 'UNBIND_POLICIES'] and \
               not any(kw in message_lower for kw in ['bind', 'unbind', 'policy']):
                return True
        
        return False
    
    def should_clarify(
        self,
        intent: Any,  # IntentStep or str
        context: ConversationContext
    ) -> bool:
        """
        Determine if clarification is needed.
        
        Reasons for clarification:
        - Ambiguous intent
        - Missing required entities
        - Multiple possible interpretations
        - High-risk action without explicit confirmation
        """
        # If intent decomposer detected ambiguity
        if isinstance(intent, DecomposedPlan):
            if intent.requires_clarification:
                return True
            
            # Check for missing entities in steps
            for step in intent.steps:
                if self._has_missing_entities(step):
                    return True
        
        # Check if we're in a clarification loop (max 3 attempts)
        if len(context.clarification_history) >= 3:
            return False  # Give up, assume user knows what they're doing
        
        # If high-risk and no recent confirmation
        if hasattr(intent, 'risk_level'):
            if intent.risk_level in ['high', 'extreme']:
                # Check if user explicitly confirmed
                recent_messages = context.messages[-3:] if len(context.messages) >= 3 else context.messages
                confirmations = ['yes', 'confirm', 'approve', 'proceed', 'go ahead']
                
                if not any(any(conf in msg.content.lower() for conf in confirmations) 
                          for msg in recent_messages if msg.role == 'user'):
                    return True
        
        return False
    
    def _has_missing_entities(self, step: IntentStep) -> bool:
        """Check if step is missing required entities"""
        # Common required entities by intent
        required_entities = {
            'BIND_POLICIES': ['agents', 'policy'],
            'CREATE_CHANNEL': ['from_agent', 'to_agent'],
            'QUERY_KB': ['query_term'],
            'RUN_ANALYSIS': ['topic']
        }
        
        intent_type = step.intent_type
        if intent_type not in required_entities:
            return False
        
        required = required_entities[intent_type]
        step_params = step.parameters or {}
        
        # Check if any required entity is missing or empty
        for entity in required:
            if entity not in step_params or not step_params[entity]:
                return True
        
        return False
    
    def needs_approval(self, intent: Any) -> bool:
        """Check if action requires human approval"""
        # High-risk intents always need approval
        high_risk_intents = [
            'UNBIND_POLICIES',
            'FORCE_ANALYSIS',
            'OVERRIDE_SENTINEL'
        ]
        
        if isinstance(intent, str):
            return intent in high_risk_intents
        
        if isinstance(intent, DecomposedPlan):
            # Check if any step is high-risk
            return any(step.risk_level in ['high', 'extreme'] for step in intent.steps)
        
        if hasattr(intent, 'risk_level'):
            return intent.risk_level in ['high', 'extreme']
        
        return False
    
    def get_next_action(
        self,
        session: ConversationSession,
        user_message: str,
        intent: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Determine what the system should do next.
        
        Returns a dictionary with:
        - action: "greet", "clarify", "confirm", "execute", "respond"
        - dialogue_state: next state
        - reason: why this action
        - details: additional context
        """
        context = session.context
        
        # First message = greeting
        if self.is_first_message(session):
            return {
                "action": "greet",
                "dialogue_state": DialogueState.GREETING,
                "reason": "first_message",
                "details": {"be_friendly": True}
            }
        
        # Topic switch = reset and understand
        if self.detect_topic_switch(user_message, context):
            return {
                "action": "acknowledge_switch",
                "dialogue_state": DialogueState.UNDERSTANDING,
                "reason": "topic_switch",
                "details": {"previous_topic": context.last_intent}
            }
        
        # Follow-up in clarifying state = process clarification
        if context.dialogue_state == DialogueState.CLARIFYING and self.is_follow_up(user_message, context):
            return {
                "action": "process_clarification",
                "dialogue_state": DialogueState.UNDERSTANDING,
                "reason": "clarification_response",
                "details": {"original_question": context.clarification_history[-1] if context.clarification_history else None}
            }
        
        # Intent needs clarification
        if intent and self.should_clarify(intent, context):
            return {
                "action": "clarify",
                "dialogue_state": DialogueState.CLARIFYING,
                "reason": "ambiguous_or_incomplete",
                "details": {"intent": intent}
            }
        
        # High-risk action needs approval
        if intent and self.needs_approval(intent):
            return {
                "action": "confirm",
                "dialogue_state": DialogueState.CONFIRMING,
                "reason": "high_risk_action",
                "details": {"intent": intent, "risk_level": getattr(intent, 'risk_level', 'high')}
            }
        
        # Ready to execute
        if intent:
            return {
                "action": "execute",
                "dialogue_state": DialogueState.EXECUTING,
                "reason": "intent_clear",
                "details": {"intent": intent}
            }
        
        # Default: try to understand
        return {
            "action": "understand",
            "dialogue_state": DialogueState.UNDERSTANDING,
            "reason": "processing_message",
            "details": {}
        }
    
    def summarize_context(self, context: ConversationContext, max_messages: int = 10) -> str:
        """
        Create a summary of conversation context for LLM.
        
        Used to inject context into intent resolution.
        """
        summary_parts = []
        
        # Recent messages
        recent = context.messages[-max_messages:] if len(context.messages) > max_messages else context.messages
        if recent:
            summary_parts.append("## Recent Conversation")
            for msg in recent:
                summary_parts.append(f"{msg.role.upper()}: {msg.content}")
        
        # Active entities
        if context.entities:
            summary_parts.append("\n## Mentioned Entities")
            for entity_type, values in context.entities.items():
                if values:
                    summary_parts.append(f"- {entity_type}: {values}")
        
        # Pending action
        if context.pending_action:
            summary_parts.append(f"\n## Pending Action")
            summary_parts.append(f"- Type: {context.pending_action.intent_type}")
            summary_parts.append(f"- Description: {context.pending_action.description}")
            summary_parts.append(f"- Risk: {context.pending_action.risk_level}")
        
        # Current state
        summary_parts.append(f"\n## Dialogue State: {context.dialogue_state.value}")
        
        if context.last_intent:
            summary_parts.append(f"## Last Intent: {context.last_intent}")
        
        return "\n".join(summary_parts)
    
    def clear_context_for_new_topic(self, context: ConversationContext):
        """Clear context when switching topics"""
        # Keep messages but clear entities and pending actions
        context.entities = {}
        context.pending_action = None
        context.clarification_history = []
        context.dialogue_state = DialogueState.UNDERSTANDING


# Global dialogue manager instance
_dialogue_manager: Optional[DialogueManager] = None

def get_dialogue_manager() -> DialogueManager:
    """Get global dialogue manager instance"""
    global _dialogue_manager
    if _dialogue_manager is None:
        _dialogue_manager = DialogueManager()
    return _dialogue_manager
