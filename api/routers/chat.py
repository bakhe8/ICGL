import os
import json
import asyncio
import subprocess
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any

from api.dependencies import logger, _safe_workspace_path, _detect_intent
from api.models.chat import FreeChatRequest, AITerminalRequest, AIWriteRequest, ChatRequest, ChatResponse

from api.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["Chat"])
chat_service = ChatService()

@router.post("/free_chat")
async def free_chat(req: FreeChatRequest):
    """
    Sovereign Thinking Loop: Simple free-form chat for the owner.
    Delegates to ChatService for processing.
    """
    try:
        return await chat_service.process_free_chat(
            message=req.message,
            session_id=req.session_id,
            paths=req.paths,
            extra_context=req.extra_context,
            auto_execute=req.auto_execute or False,
            actor=req.actor
        )
    except Exception as e:
        logger.error(f"Free chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/terminal")
async def ai_terminal(payload: AITerminalRequest):
    """Restricted terminal for AI workspace."""
    try:
        workdir = _safe_workspace_path(payload.path or ".")
        proc = subprocess.run(
            payload.cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(workdir),
            timeout=payload.lines or 20
        )
        output = proc.stdout or proc.stderr or "Executed"
        return {"output": output}
    except Exception as e:
        logger.error(f"Terminal execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file/write")
async def write_ai_file(payload: AIWriteRequest):
    target_file = _safe_workspace_path(payload.path)
    with open(target_file, payload.mode or "w", encoding="utf-8") as f:
        f.write(payload.content)
    return {"status": "success", "file": payload.path}
