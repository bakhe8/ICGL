"""
Session management for advanced conversation flows.
Stub for ICGL conversation/session logic.
"""
from typing import Optional, List
from enum import Enum
from datetime import datetime


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
            "context": self.context,
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
        return self._sessions.get(session_id, ConversationSession("stub"))

    def close_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def get_user_sessions(self, user_id: str, status: Optional[SessionStatus] = None) -> List[ConversationSession]:
        if status:
            return [s for s in self._sessions.values() if s.user_id == user_id and s.status == status]
        return [s for s in self._sessions.values() if s.user_id == user_id]

    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[dict]:
        s = self.get_session(session_id)
        return s.messages[-limit:]

    def add_message(self, session_id: str, role: str, content: str) -> None:
        s = self.get_session(session_id)
        msg = {"role": role, "content": content, "timestamp": datetime.utcnow().isoformat()}
        s.messages.append(msg)

    def update_session(self, session: ConversationSession) -> None:
        self._sessions[session.session_id] = session


def get_session_manager():
    return SessionManager()
