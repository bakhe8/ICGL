"""
ICGL Chat Schemas
=================

Data models for conversational interface.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4


class ChatContext(BaseModel):
    """User context for chat requests."""
    open_files: List[str] = Field(default_factory=list)
    selection: str = ""
    mode: str = "auto"
    human_id: str = "user"


class ChatRequest(BaseModel):
    """Incoming chat message from user."""
    message: str = Field(..., description="User's message")
    session_id: str = Field(default_factory=lambda: f"session-{uuid4().hex[:8]}")
    context: Optional[ChatContext] = Field(default_factory=ChatContext)


class MessageBlock(BaseModel):
    """Rich content block in a message."""
    type: Literal["analysis", "alerts", "actions", "adr", "metrics", "text", "memory"]
    data: Dict[str, Any]
    collapsed: bool = True
    title: Optional[str] = None


class ChatMessage(BaseModel):
    """Single message in conversation."""
    role: Literal["user", "system", "assistant"]
    content: str = ""
    text: Optional[str] = None
    blocks: List[MessageBlock] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    messages: List[ChatMessage]
    state: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)


# Intent types

class Intent(BaseModel):
    """Base intent class."""
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeIntent(Intent):
    """Intent to analyze a proposal."""
    type: str = "analyze"
    title: str
    context: str
    decision: str
    mode: str = "explore"


class RefactorIntent(Intent):
    """Intent to refactor documentation."""
    type: str = "refactor"
    target: str = "docs"


class QueryIntent(Intent):
    """Intent to query knowledge base."""
    type: str = "query"
    query_type: str  # "risks", "adrs", "policies"
    filters: Dict[str, Any] = Field(default_factory=dict)


class SignIntent(Intent):
    """Intent to sign a decision."""
    type: str = "sign"
    adr_id: str
    action: str  # "APPROVE", "REJECT", "MODIFY"
    rationale: str


class HelpIntent(Intent):
    """Intent to get help."""
    type: str = "help"
    topic: Optional[str] = None
