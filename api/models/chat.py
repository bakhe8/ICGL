from pydantic import BaseModel
from typing import Optional, List

class FreeChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    paths: Optional[List[str]] = None
    extra_context: Optional[str] = None
    auto_execute: Optional[bool] = False
    actor: Optional[str] = None

class AITerminalRequest(BaseModel):
    cmd: str
    path: Optional[str] = None
    lines: Optional[int] = 20
    content: Optional[str] = None

class AIWriteRequest(BaseModel):
    path: str
    content: str
    mode: Optional[str] = "w"

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    text: str
    session_id: str
