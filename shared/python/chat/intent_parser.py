"""
ICGL Intent Parser
==================

Parses natural language messages into structured intents.
"""

import re
from typing import Optional
from .schemas import (
    Intent, AnalyzeIntent, RefactorIntent, QueryIntent, 
    SignIntent, HelpIntent
)


class IntentParser:
    """Parses user messages into actionable intents."""
    
    def parse(self, message: str) -> Intent:
        """
        Parse user message into intent.
        
        Args:
            message: User's natural language input
            
        Returns:
            Parsed intent
        """
        msg = message.lower().strip()
        
        # Analyze intent
        if any(word in msg for word in ["analyze", "review", "evaluate", "assess"]):
            return self._parse_analyze(message)
        
        # Refactor intent
        if any(word in msg for word in ["refactor", "improve", "rewrite"]):
            return self._parse_refactor(message)
        
        # Query intent
        if any(word in msg for word in ["show", "list", "what", "find", "search"]):
            return self._parse_query(message)
        
        # Sign intent
        if any(word in msg for word in ["sign", "approve", "reject", "modify"]):
            return self._parse_sign(message)
        
        # Help intent
        if any(word in msg for word in ["help", "how", "explain"]):
            return HelpIntent(topic=self._extract_topic(message))
        
        # Default: treat as analyze with message as context
        return AnalyzeIntent(
            title="User Query",
            context=message,
            decision="Awaiting analysis",
            mode="explore"
        )
    
    def _parse_analyze(self, message: str) -> AnalyzeIntent:
        """Extract analysis intent parameters."""
        # Try to extract proposal components
        title = self._extract_title(message) or "Proposal Analysis"
        context = message
        decision = "To be determined"
        
        # Check for mode keywords
        mode = "explore"
        if "decide" in message.lower():
            mode = "decide"
        elif "experiment" in message.lower():
            mode = "experiment"
        
        return AnalyzeIntent(
            title=title,
            context=context,
            decision=decision,
            mode=mode
        )
    
    def _parse_refactor(self, message: str) -> RefactorIntent:
        """Extract refactor intent parameters."""
        target = "docs"  # default
        
        if "code" in message.lower():
            target = "code"
        elif"doc" in message.lower():
            target = "docs"
        
        return RefactorIntent(target=target)
    
    def _parse_query(self, message: str) -> QueryIntent:
        """Extract query intent parameters."""
        msg = message.lower()
        
        # Determine query type
        if any(word in msg for word in ["risk", "alert", "danger"]):
            query_type = "risks"
        elif any(word in msg for word in ["adr", "decision"]):
            query_type = "adrs"
        elif any(word in msg for word in ["policy", "rule"]):
            query_type = "policies"
        else:
            query_type = "general"
        
        return QueryIntent(
            query_type=query_type,
            filters={}
        )
    
    def _parse_sign(self, message: str) -> SignIntent:
        """Extract signing intent parameters."""
        msg = message.lower()
        
        # Determine action
        if "approve" in msg:
            action = "APPROVE"
        elif "reject" in msg:
            action = "REJECT"
        elif "modify" in msg:
            action = "MODIFY"
        else:
            action = "APPROVE"  # default
        
        # Extract ADR ID if present
        adr_id_match = re.search(r'adr[_-]?(\w+)', msg)
        adr_id = adr_id_match.group(0) if adr_id_match else "latest"
        
        return SignIntent(
            adr_id=adr_id,
            action=action,
            rationale=message
        )
    
    def _extract_title(self, message: str) -> Optional[str]:
        """Try to extract a title from message."""
        # Look for quoted strings
        quote_match = re.search(r'"([^"]+)"', message)
        if quote_match:
            return quote_match.group(1)
        
        # Look for "about X" or "for X"
        about_match = re.search(r'(?:about|for)\s+(.+?)(?:\.|$)', message, re.IGNORECASE)
        if about_match:
            return about_match.group(1).strip()
        
        return None
    
    def _extract_topic(self, message: str) -> Optional[str]:
        """Extract help topic from message."""
        msg = message.lower()
        
        if "analyze" in msg or "proposal" in msg:
            return "analyze"
        elif "refactor" in msg or "docs" in msg:
            return "refactor"
        elif "sign" in msg or "decision" in msg:
            return "signing"
        
        return None
