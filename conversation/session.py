"""
Conversation Session Management
--------------------------------

Infrastructure for stateful multi-turn conversations in COC.

Responsibilities:
- Create and manage conversation sessions
- Store conversation history
- Track entities and context
- Manage session lifecycle
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import sqlite3
import json
from pathlib import Path

from ..kb.schemas import uid


class SessionStatus(Enum):
    """Session lifecycle states"""
    ACTIVE = "active"
    WAITING_CLARIFICATION = "waiting_clarification"
    WAITING_APPROVAL = "waiting_approval"
    CLOSED = "closed"
    EXPIRED = "expired"


class DialogueState(Enum):
    """Conversation phase tracking"""
    GREETING = "greeting"
    UNDERSTANDING = "understanding"
    CLARIFYING = "clarifying"
    CONFIRMING = "confirming"
    EXECUTING = "executing"
    REPORTING = "reporting"


@dataclass
class Message:
    """Single message in conversation"""
    message_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(
            message_id=data["message_id"],
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class PendingAction:
    """Action awaiting user approval"""
    action_id: str
    intent_type: str
    description: str
    risk_level: str
    parameters: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "intent_type": self.intent_type,
            "description": self.description,
            "risk_level": self.risk_level,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PendingAction':
        return cls(
            action_id=data["action_id"],
            intent_type=data["intent_type"],
            description=data["description"],
            risk_level=data["risk_level"],
            parameters=data["parameters"],
            created_at=datetime.fromisoformat(data["created_at"])
        )


@dataclass
class ConversationContext:
    """Full conversation state"""
    messages: List[Message] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)
    pending_action: Optional[PendingAction] = None
    dialogue_state: DialogueState = DialogueState.GREETING
    last_intent: Optional[str] = None
    clarification_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "messages": [m.to_dict() for m in self.messages],
            "entities": self.entities,
            "pending_action": self.pending_action.to_dict() if self.pending_action else None,
            "dialogue_state": self.dialogue_state.value,
            "last_intent": self.last_intent,
            "clarification_history": self.clarification_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        return cls(
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            entities=data.get("entities", {}),
            pending_action=PendingAction.from_dict(data["pending_action"]) if data.get("pending_action") else None,
            dialogue_state=DialogueState(data.get("dialogue_state", "greeting")),
            last_intent=data.get("last_intent"),
            clarification_history=data.get("clarification_history", [])
        )


@dataclass
class ConversationSession:
    """Complete conversation session"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    status: SessionStatus
    context: ConversationContext = field(default_factory=ConversationContext)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "status": self.status.value,
            "context": self.context.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSession':
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            status=SessionStatus(data["status"]),
            context=ConversationContext.from_dict(data.get("context", {}))
        )


class SessionManager:
    """
    Manages conversation sessions with SQLite persistence.
    
    Similar to ObservabilityLedger pattern.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / ".icgl" / "sessions.db")
        
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                status TEXT NOT NULL,
                context_json TEXT NOT NULL
            )
        """)
        
        # Index for user lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_user_id 
            ON sessions(user_id)
        """)
        
        # Index for active sessions
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_status 
            ON sessions(status)
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, user_id: str) -> ConversationSession:
        """Create new conversation session"""
        now = datetime.utcnow()
        session = ConversationSession(
            session_id=f"session_{uid()}",
            user_id=user_id,
            created_at=now,
            last_activity=now,
            status=SessionStatus.ACTIVE,
            context=ConversationContext()
        )
        
        self._save_session(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieve session by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, user_id, created_at, last_activity, status, context_json
            FROM sessions
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return ConversationSession(
            session_id=row[0],
            user_id=row[1],
            created_at=datetime.fromisoformat(row[2]),
            last_activity=datetime.fromisoformat(row[3]),
            status=SessionStatus(row[4]),
            context=ConversationContext.from_dict(json.loads(row[5]))
        )
    
    def update_session(self, session: ConversationSession):
        """Update existing session"""
        session.last_activity = datetime.utcnow()
        self._save_session(session)
    
    def _save_session(self, session: ConversationSession):
        """Persist session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions 
            (session_id, user_id, created_at, last_activity, status, context_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.user_id,
            session.created_at.isoformat(),
            session.last_activity.isoformat(),
            session.status.value,
            json.dumps(session.context.to_dict())
        ))
        
        conn.commit()
        conn.close()
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add message to conversation history"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        message = Message(
            message_id=f"msg_{uid()}",
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        session.context.messages.append(message)
        self.update_session(session)
        
        # Async Semantic Indexing
        try:
            # Avoid circular import at top level
            from ..memory.service import get_memory_service
            import asyncio
            
            # Fire and forget
            service = get_memory_service()
            asyncio.create_task(
                service.remember_interaction(
                    session_id=session_id, 
                    role=role, 
                    content=content, 
                    metadata=metadata
                )
            )
        except Exception as e:
            # Should not block the user
            print(f"⚠️ Memory indexing failed: {e}")
            
        return message
    
    def get_user_sessions(self, user_id: str, status: Optional[SessionStatus] = None) -> List[ConversationSession]:
        """Get all sessions for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT session_id, user_id, created_at, last_activity, status, context_json
                FROM sessions
                WHERE user_id = ? AND status = ?
                ORDER BY last_activity DESC
            """, (user_id, status.value))
        else:
            cursor.execute("""
                SELECT session_id, user_id, created_at, last_activity, status, context_json
                FROM sessions
                WHERE user_id = ?
                ORDER BY last_activity DESC
            """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            ConversationSession(
                session_id=row[0],
                user_id=row[1],
                created_at=datetime.fromisoformat(row[2]),
                last_activity=datetime.fromisoformat(row[3]),
                status=SessionStatus(row[4]),
                context=ConversationContext.from_dict(json.loads(row[5]))
            )
            for row in rows
        ]
    
    def close_session(self, session_id: str):
        """Mark session as closed"""
        session = self.get_session(session_id)
        if session:
            session.status = SessionStatus.CLOSED
            self.update_session(session)
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """Remove old inactive sessions"""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Mark as expired
        cursor.execute("""
            UPDATE sessions
            SET status = ?
            WHERE last_activity < ? AND status = ?
        """, (SessionStatus.EXPIRED.value, cutoff.isoformat(), SessionStatus.ACTIVE.value))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Message]:
        """Get message history for session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session.context.messages
        if limit:
            messages = messages[-limit:]
        
        return messages


# Global session manager instance
_session_manager: Optional[SessionManager] = None

def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
