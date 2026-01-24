"""
Session management for advanced conversation flows.
Stub for ICGL conversation/session logic.
"""

from datetime import datetime
from enum import Enum
from typing import List


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"


class ConversationSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_id = f"session-{user_id}"
        self.status: SessionStatus = SessionStatus.ACTIVE

        self.created_at = datetime.utcnow().isoformat()
        # context holds session-scoped metadata used by server logic
        self.context: dict = {
            "last_intent": None,
            "clarification_history": [],
        }
        # simple message history
        self.messages: List[dict] = []

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "context": self.context,
            "history": self.messages,  # Support 'history' as requested in checklist
        }


# Stub manager
class SessionManager:
    def __init__(self):
        self._sessions: dict[str, ConversationSession] = {}

    def create_session(self, user_id: str) -> ConversationSession:
        s = ConversationSession(user_id)
        self._sessions[s.session_id] = s
        return s

    def get_session(self, session_id: str) -> ConversationSession:
        # Fallback to create if missing? No, better return None or a clean stub if requested.
        # But for 'history' call stability, returning a stub helps.
        if session_id not in self._sessions:
            # Create ephemeral session if it doesn't exist to prevent AttributeError
            return ConversationSession(
                session_id.split("-")[-1] if "-" in session_id else "anonymous"
            )
        return self._sessions[session_id]

    def close_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[dict]:
        s = self.get_session(session_id)
        return s.messages[-limit:]

    def add_message(self, session_id: str, role: str, content: str) -> None:
        s = self.get_session(session_id)
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "id": f"msg-{int(datetime.utcnow().timestamp() * 1000)}",
        }
        s.messages.append(msg)

    def update_session(self, session: ConversationSession) -> None:
        self._sessions[session.session_id] = session


def get_session_manager():
    return SessionManager()
