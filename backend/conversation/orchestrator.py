from .composer import ResponseComposer
from .dialogue_manager import DialogueManager
from .intent_resolver import IntentResolver
from .session import SessionManager


class ConversationOrchestrator:
    """
    Routes conversation flows: Parse -> Manage State -> Execute -> Compose.
    """

    def __init__(self, session_manager: SessionManager):
        self.resolver = IntentResolver()
        self.dialogue = DialogueManager()
        self.composer = ResponseComposer()
        self.sessions = session_manager

    async def handle(self, message: str, session_id: str) -> dict:
        session = self.sessions.get_session(session_id)

        # 1. Resolve Intent
        intent = await self.resolver.resolve(message, session.context)

        # 2. Determine Next Step (Dialogue State)
        plan = self.dialogue.determine_next_step(session, intent)

        if plan["action"] == "clarify":
            response = self.composer.compose_clarification(plan["message"])
            return {"message": response, "session": session.to_dict()}

        # 3. Execution (bridge to real logic based on intent)
        # This part usually happens in the chat orchestrator,
        # but here we provide the structure for structured dialogue results.

        return {
            "intent": intent.dict(),
            "action": plan["action"],
            "session_id": session_id,
        }
