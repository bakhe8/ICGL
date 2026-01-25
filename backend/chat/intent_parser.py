"""
ICGL Intent Parser
==================

Parses natural language messages into structured intents using robust regex patterns.
"""

import re
from typing import Optional

from .schemas import (
    AnalyzeIntent,
    GreetIntent,
    HelpIntent,
    Intent,
    QueryIntent,
    RefactorIntent,
    SignIntent,
)


class IntentParser:
    """
    Advanced Intent Parser for ICGL.
    Uses regex patterns to extract structured metadata from natural language.
    """

    PATTERNS = {
        "analyze": r"\b(analyze|review|evaluate|assess|check|audit)\b",
        "refactor": r"\b(refactor|improve|rewrite|optimize|clean)\b",
        "query": r"\b(show|list|get|find|search|where is|tell me about)\b",
        "sign": r"\b(sign|approve|reject|modify|conclude|finaliz[ez])\b",
        "help": r"\b(help|how|explain|tutorial|guide|usage)\b",
        "greet": r"\b(hi|hello|hey|greetings|welcome|مرحبا|سلام|يا|اهلا)\b",
    }

    def parse(self, message: str) -> Intent:
        """Parse user message into intent with prioritized pattern matching."""
        msg_clean = message.lower().strip()

        # 1. Sign Intent (High Priority for safety/governance)
        if re.search(self.PATTERNS["sign"], msg_clean):
            return self._parse_sign(message)

        # 2. Refactor Intent
        if re.search(self.PATTERNS["refactor"], msg_clean):
            return self._parse_refactor(message)

        # 3. Query Intent
        if re.search(self.PATTERNS["query"], msg_clean):
            return self._parse_query(message)

        # 4. Analyze Intent
        if re.search(self.PATTERNS["analyze"], msg_clean) or ("proposal" in msg_clean):
            return self._parse_analyze(message)

        # 5. Help Intent
        if re.search(self.PATTERNS["help"], msg_clean):
            topic = self._extract_topic(msg_clean)
            return HelpIntent(topic=topic)

        # 6. Greet Intent
        if re.search(self.PATTERNS["greet"], msg_clean):
            return GreetIntent()

        # Default: If message is very short, don't trigger heavy analysis
        if len(msg_clean.split()) < 3:
            return HelpIntent()

        # Default: treat as exploration analysis
        return AnalyzeIntent(
            title="General Exploration",
            context=message,
            decision="Awaiting context analysis",
            mode="explore",
        )

    def _parse_analyze(self, message: str) -> AnalyzeIntent:
        """Extract analysis intent with title and mode extraction."""
        # Extract title from quotes or after specific keywords
        quote_match = re.search(r'"([^"]+)"', message)
        about_match = re.search(
            r"(?:about|for|on)\s+(.+?)(?:\.|$|,)", message, re.IGNORECASE
        )

        title = (
            quote_match.group(1)
            if quote_match
            else (about_match.group(1).strip() if about_match else "Active Proposal")
        )

        # Determine mode
        mode = "explore"
        if re.search(r"\b(decide|judge|vote)\b", message.lower()):
            mode = "decide"
        elif re.search(r"\b(experiment|test|simulate)\b", message.lower()):
            mode = "experiment"

        return AnalyzeIntent(
            title=title.strip(), context=message, decision="In Analysis", mode=mode
        )

    def _parse_refactor(self, message: str) -> RefactorIntent:
        """Determine refactor target based on keywords."""
        target = "docs"
        if re.search(r"\b(code|function|logic|script|module)\b", message.lower()):
            target = "code"
        return RefactorIntent(target=target)

    def _parse_query(self, message: str) -> QueryIntent:
        """Extract query type and optional filters."""
        msg = message.lower()
        query_type = "general"
        filters = {}

        if re.search(r"\b(risk|alert|danger|issue|warning)\b", msg):
            query_type = "risks"
        elif re.search(r"\b(adr|decision|history|archive)\b", msg):
            query_type = "adrs"
        elif re.search(r"\b(policy|rule|constraint|governance)\b", msg):
            query_type = "policies"
        elif re.search(r"\b(agent|manifest|capability)\b", msg):
            query_type = "agents"

        # Basic ID filter extraction: "id=X" or "id: X"
        id_match = re.search(r"id[:=]\s*(\w+)", msg)
        if id_match:
            filters["id"] = id_match.group(1)

        return QueryIntent(query_type=query_type, filters=filters)

    def _parse_sign(self, message: str) -> SignIntent:
        """Extract signing parameters (Action + ADR ID)."""
        msg = message.lower()

        action = "APPROVE"
        if "reject" in msg:
            action = "REJECT"
        elif re.search(r"\b(modify|change|edit)\b", msg):
            action = "MODIFY"

        # Extract ADR ID: "adr-123", "ADR_123", "#123"
        id_match = re.search(r"(?:adr[-_]?)?#?(\w+)", msg)
        adr_id = id_match.group(1) if id_match else "latest"

        return SignIntent(adr_id=adr_id, action=action, rationale=message)

    def _extract_topic(self, msg: str) -> Optional[str]:
        """Identify specific help topic."""
        for topic in ["analyze", "refactor", "sign", "policy", "orchestrator"]:
            if topic in msg:
                return topic
        return None
