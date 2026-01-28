from typing import Any, List

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []


class ChatResponse(BaseModel):
    messages: List[Any] = []
    metadata: dict = {}
