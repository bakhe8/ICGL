from typing import Any, Dict

from .session import ConversationSession


class DialogueManager:
    """
    Tracks conversation state and manages clarification loops.
    """

    def __init__(self):
        pass

    def determine_next_step(
        self, session: ConversationSession, intent: Any
    ) -> Dict[str, Any]:
        """
        Decides if we need more info (clarify) or can proceed to execution.
        """
        # Example logic: if intent is 'sign' but no ADR ID found and no 'latest' context
        if (
            intent.type == "sign"
            and intent.adr_id == "latest"
            and not session.context.get("last_adr_id")
        ):
            session.context["awaiting_clarification"] = "adr_id"
            return {
                "action": "clarify",
                "message": "Which Proposal (ADR) would you like to sign? Please provide an ID or reference a recent analysis.",
            }

        return {"action": "execute", "intent": intent}
