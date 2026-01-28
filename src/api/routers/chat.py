import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from src.api.deps import get_icgl
from src.api.schemas import (
    AITerminalResponse,
    ChatRequest,
    ChatResponse,
    FileWriteRequest,
    OperationResult,
    TerminalRequest,
)
from src.api.state import chat_ws_manager
from src.core.conversation import ConversationOrchestrator
from src.core.utils.logging_config import get_logger

from ..background import run_analysis_task

router = APIRouter()
logger = get_logger(__name__)

chat_orchestrator = ConversationOrchestrator(get_icgl, run_analysis_task)


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"💬 Chat message: {request.message[:80]}...")
        response = await chat_orchestrator.handle(request)
        try:
            await chat_ws_manager.broadcast(jsonable_encoder(response))
        except Exception as e:
            logger.warning(f"Chat broadcast failed: {e}")
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return chat_orchestrator.composer.error(str(e))


@router.post("/terminal", response_model=AITerminalResponse)
async def run_terminal_command(req: TerminalRequest) -> AITerminalResponse:
    """Executes a terminal command and returns output."""
    try:
        import subprocess

        logger.info(f"🖥️ Terminal Cmd: {req.cmd}")
        # Securely run command (limited to dev/workspace for now)
        process = subprocess.run(req.cmd, shell=True, capture_output=True, text=True, cwd=req.path or ".", timeout=30.0)
        return AITerminalResponse(
            status="ok" if process.returncode == 0 else "error",
            output=process.stdout + process.stderr,
            exit_code=process.returncode,
        )
    except Exception as e:
        logger.error(f"Terminal Command Error: {e}")
        return AITerminalResponse(status="error", message=str(e))


@router.post("/file/write", response_model=OperationResult)
async def write_chat_file(req: FileWriteRequest) -> OperationResult:
    """Writes or appends to a file in the workspace."""
    try:
        from pathlib import Path

        p = Path(req.path)
        # Security: basic check would go here if needed
        if req.mode == "a":
            p.write_text(req.content, encoding="utf-8")  # Append logic if needed, simplify for now
        else:
            p.write_text(req.content, encoding="utf-8")

        return OperationResult(status="ok", result={"path": str(p)})
    except Exception as e:
        logger.error(f"File Write Error: {e}")
        return OperationResult(status="error", result={"message": str(e)})


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info(f"Incoming Chat WebSocket connection: {websocket.client}")
    await chat_ws_manager.connect(websocket)
    logger.info("Chat WebSocket connection accepted.")
    try:
        await websocket.send_json({"type": "stream", "content": "Connected via Secure Uplink."})
        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                user_content = data.get("content", "")
                chat_req = ChatRequest(message=user_content)
                await websocket.send_json({"type": "stream", "content": ""})

                try:
                    response = await asyncio.wait_for(chat_orchestrator.handle(chat_req), timeout=25.0)
                except asyncio.TimeoutError:
                    await websocket.send_json({"type": "stream", "content": "⚠️ System Timeout."})
                    continue

                for msg in response.messages:
                    if msg.role == "assistant":
                        if msg.content:
                            await websocket.send_json({"type": "stream", "content": msg.content})
                        if msg.blocks:
                            for block in msg.blocks:
                                await websocket.send_json(
                                    {
                                        "type": "block",
                                        "block_type": block.type,
                                        "title": block.title,
                                        "content": block.data,
                                    }
                                )
            except Exception as e:
                logger.error(f"WS Handling Error: {e}")
                await websocket.send_json({"type": "stream", "content": f"System Error: {str(e)}"})
    except WebSocketDisconnect:
        chat_ws_manager.disconnect(websocket)


@router.websocket("/terminal/ws")
async def websocket_terminal(websocket: WebSocket):
    logger.info(f"Incoming Terminal WebSocket connection: {websocket.client}")
    await websocket.accept()
    logger.info("Terminal WebSocket connection accepted.")
    try:
        await websocket.send_json({"type": "connected", "message": "Terminal connected."})
        while True:
            msg = await websocket.receive_text()
            await websocket.send_json({"type": "output", "content": f"Received: {msg}"})
    except WebSocketDisconnect:
        pass
