"""
ICGL Chat Schemas
=================

Data models for conversational interface.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


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


class ToolCall(BaseModel):
    """Tool execution record."""

    cmd: str
    path: Optional[str] = None
    status: str = "pending"
    output: Optional[str] = None
    proposed: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    messages: List[ChatMessage]
    text: Optional[str] = None
    blocked_commands: List[ToolCall] = Field(default_factory=list)
    executed: List[ToolCall] = Field(default_factory=list)
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
