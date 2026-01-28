import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from src.api.deps import get_icgl
from src.api.state import chat_ws_manager
from src.core.chat.schemas import ChatRequest, ChatResponse
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


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    await chat_ws_manager.connect(websocket)
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
    await websocket.accept()
    try:
        await websocket.send_json({"type": "connected", "message": "Terminal connected."})
        while True:
            msg = await websocket.receive_text()
            await websocket.send_json({"type": "output", "content": f"Received: {msg}"})
    except WebSocketDisconnect:
        pass
