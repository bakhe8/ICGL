"""
Entity Tracker
--------------

Extracts and tracks entities across conversation turns.

Responsibilities:
- Extract entities (agents, policies, channels, etc.) from messages
- Track entity salience (recency and relevance)
- Resolve coreferences ("it" → last_channel_id)
- Update conversation context with entities
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .session import ConversationContext, Message
from core.llm import get_llm


class EntityType(Enum):
    """Types of entities to track"""
    AGENT = "agent"
    POLICY = "policy"
    CHANNEL = "channel"
    ACTION = "action"
    TIME_REFERENCE = "time_reference"
    KB_TOPIC = "kb_topic"


@dataclass
class Entity:
    """Tracked entity with metadata"""
    entity_id: str
    entity_type: EntityType
    value: str
    first_mentioned: datetime
    last_mentioned: datetime
    mention_count: int = 1
    salience_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_mention(self):
        """Update when entity is mentioned again"""
        self.last_mentioned = datetime.utcnow()
        self.mention_count += 1
        # Boost salience on re-mention
        self.salience_score = min(1.0, self.salience_score * 1.2)
    
    def decay_salience(self, decay_factor: float = 0.9):
        """Reduce salience over time"""
        self.salience_score *= decay_factor


class EntityTracker:
    """
    Tracks entities across conversation.
    
    Uses LLM to extract entities and maintains salience scores
    for intelligent coreference resolution.
    """
    
    def __init__(self):
        self.llm = get_llm()
    
    def extract_entities(
        self,
        message: str,
        context: ConversationContext
    ) -> Dict[EntityType, List[Entity]]:
        """
        Extract entities from message using LLM.
        
        Returns dictionary of entity_type → entities
        """
        # Build prompt for LLM
        prompt = self._build_extraction_prompt(message, context)
        
        # Get LLM to extract entities
        llm_response = self.llm.generate(
            prompt,
            max_tokens=300,
            temperature=0.3  # Low temperature for precision
        )
        
        # Parse LLM response
        extracted = self._parse_entity_response(llm_response)
        
        # Create Entity objects
        entities_by_type: Dict[EntityType, List[Entity]] = {}
        now = datetime.utcnow()
        
        for entity_type, values in extracted.items():
            entities = []
            for value in values:
                entity = Entity(
                    entity_id=f"{entity_type.value}_{value}",
                    entity_type=entity_type,
                    value=value,
                    first_mentioned=now,
                    last_mentioned=now,
                    mention_count=1,
                    salience_score=1.0
                )
                entities.append(entity)
            
            if entities:
                entities_by_type[entity_type] = entities
        
        return entities_by_type
    
    def _build_extraction_prompt(
        self,
        message: str,
        context: ConversationContext
    ) -> str:
        """Build prompt for entity extraction"""
        
        prompt = """Extract entities from this message in a conversation about code governance.

Message: "{message}"

Extract the following types of entities (if present):
- AGENT: Agent names (e.g., "architect", "security", "planner")
- POLICY: Policy names (e.g., "collaborative", "read_only", "business_hours")
- CHANNEL: Channel references (e.g., "channel_abc123", "the channel")
- ACTION: Actions mentioned (e.g., "bind", "create", query", "analyze")
- TIME: Time references (e.g., "today", "this week", "9 AM")
- TOPIC: Knowledge base topics (e.g., "authentication", "API design")

Format response as JSON:
{{
  "agents": ["agent1", "agent2"],
  "policies": ["policy1"],
  "channels": [],
  "actions": ["action1"],
  "times": [],
  "topics": []
}}

Only include non-empty arrays. Be precise."""
        
        return prompt.format(message=message)
    
    def _parse_entity_response(self, response: str) -> Dict[EntityType, List[str]]:
        """Parse LLM entity extraction response"""
        import json
        import re
        
        # Try to extract JSON from response
        json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
        if not json_match:
            return {}
        
        try:
            data = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return {}
        
        # Map to EntityType
        mapping = {
            'agents': EntityType.AGENT,
            'policies': EntityType.POLICY,
            'channels': EntityType.CHANNEL,
            'actions': EntityType.ACTION,
            'times': EntityType.TIME_REFERENCE,
            'topics': EntityType.KB_TOPIC
        }
        
        result = {}
        for key, entity_type in mapping.items():
            if key in data and isinstance(data[key], list):
                result[entity_type] = data[key]
        
        return result
    
    def resolve_coreferences(
        self,
        message: str,
        context: ConversationContext
    ) -> str:
        """
        Resolve pronouns and references to specific entities.
        
        Returns message with pronouns replaced.
        """
        message_lower = message.lower()
        
        # Get most salient entities by type
        salient = self._get_salient_entities(context)
        
        # Simple pronoun resolution
        replacements = {}
        
        # "it" → most recent channel or topic
        if ' it ' in f' {message_lower} ' or message_lower.startswith('it '):
            if EntityType.CHANNEL in salient and salient[EntityType.CHANNEL]:
                replacements['it'] = salient[EntityType.CHANNEL][0].value
            elif EntityType.KB_TOPIC in salient and salient[EntityType.KB_TOPIC]:
                replacements['it'] = salient[EntityType.KB_TOPIC][0].value
        
        # "them" → most recent agents
        if ' them ' in f' {message_lower} ' or message_lower.endswith(' them'):
            if EntityType.AGENT in salient and len(salient[EntityType.AGENT]) >= 2:
                agents = [e.value for e in salient[EntityType.AGENT][:2]]
                replacements['them'] = f"{agents[0]} and {agents[1]}"
        
        # "that policy" → most recent policy
        if 'that policy' in message_lower:
            if EntityType.POLICY in salient and salient[EntityType.POLICY]:
                replacements['that policy'] = f"the {salient[EntityType.POLICY][0].value} policy"
        
        # Apply replacements
        resolved = message
        for pronoun, replacement in replacements.items():
            # Case-insensitive replacement
            import re
            resolved = re.sub(
                rf'\b{pronoun}\b',
                replacement,
                resolved,
                flags=re.IGNORECASE
            )
        
        return resolved
    
    def _get_salient_entities(
        self,
        context: ConversationContext
    ) -> Dict[EntityType, List[Entity]]:
        """Get most salient entities by type"""
        
        # Flatten all entities from context
        all_entities: Dict[EntityType, List[Entity]] = {}
        
        for entity_type_str, entity_list in context.entities.items():
            try:
                entity_type = EntityType(entity_type_str)
            except ValueError:
                continue
            
            if isinstance(entity_list, list):
                # Assuming stored as Entity objects (simplified)
                all_entities[entity_type] = entity_list
        
        # Sort by salience
        for entity_type in all_entities:
            all_entities[entity_type] = sorted(
                all_entities[entity_type],
                key=lambda e: (e.salience_score, e.last_mentioned),
                reverse=True
            )
        
        return all_entities
    
    def update_context(
        self,
        context: ConversationContext,
        new_entities: Dict[EntityType, List[Entity]]
    ):
        """
        Update conversation context with newly extracted entities.
        
        Merges with existing entities and updates salience.
        """
        # Decay existing entities
        for entity_type_str, entity_list in context.entities.items():
            if isinstance(entity_list, list):
                for entity in entity_list:
                    if hasattr(entity, 'decay_salience'):
                        entity.decay_salience(0.95)
        
        # Merge new entities
        for entity_type, entities in new_entities.items():
            type_key = entity_type.value
            
            if type_key not in context.entities:
                context.entities[type_key] = []
            
            existing_values = {
                e.value if hasattr(e, 'value') else e
                for e in context.entities[type_key]
            }
            
            for entity in entities:
                if entity.value in existing_values:
                    # Update existing entity
                    for existing in context.entities[type_key]:
                        if hasattr(existing, 'value') and existing.value == entity.value:
                            existing.update_mention()
                            break
                else:
                    # Add new entity
                    context.entities[type_key].append(entity)
        
        # Limit entities per type to top 10 by salience
        for type_key in context.entities:
            if isinstance(context.entities[type_key], list):
                context.entities[type_key] = sorted(
                    context.entities[type_key],
                    key=lambda e: e.salience_score if hasattr(e, 'salience_score') else 0,
                    reverse=True
                )[:10]
    
    def get_entity_summary(self, context: ConversationContext) -> str:
        """Generate human-readable entity summary"""
        summary_parts = []
        
        for entity_type_str, entity_list in context.entities.items():
            if not entity_list:
                continue
            
            values = [
                e.value if hasattr(e, 'value') else str(e)
                for e in entity_list[:5]  # Top 5
            ]
            
            if values:
                summary_parts.append(f"{entity_type_str}: {', '.join(values)}")
        
        return " | ".join(summary_parts) if summary_parts else "No entities tracked"


# Global entity tracker
_entity_tracker: Optional[EntityTracker] = None

def get_entity_tracker() -> EntityTracker:
    """Get global entity tracker instance"""
    global _entity_tracker
    if _entity_tracker is None:
        _entity_tracker = EntityTracker()
    return _entity_tracker
