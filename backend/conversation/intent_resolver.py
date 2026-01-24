from ..chat.intent_parser import IntentParser
from ..chat.schemas import Intent


class IntentResolver:
    """
    Bridges natural language parsing with session-aware semantic resolution.
    """

    def __init__(self):
        self.parser = IntentParser()

    async def resolve(self, message: str, session_context: dict) -> Intent:
        """
        Parses intent and enriches it with session context (e.g. pending clarifications).
        """
        intent = self.parser.parse(message)

        # If we have a pending clarification in context, try to map the message to it
        if session_context.get("awaiting_clarification"):
            # logic to handle 'yes/no' or specific parameter filling
            pass

        return intent
