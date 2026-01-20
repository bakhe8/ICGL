import asyncio
from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from utils.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.websocket("/ws/scp")
async def scp_stream(websocket: WebSocket):
    """
    Minimal SCP (Sentinel Control Plane) websocket stub.
    Keeps the UI stream alive and emits periodic heartbeat events.
    """
    await websocket.accept()
    logger.info("SCP WebSocket connected")

    async def send_event(payload: Dict[str, Any]) -> bool:
        # Returns False when send fails or socket is not open.
        if websocket.client_state.name != "CONNECTED":
            return False
        try:
            await websocket.send_json(payload)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error(f"SCP WebSocket send failed: {exc}")
            return False

    try:
        ok = await send_event(
            {
                "type": "alert",
                "id": "scp-welcome",
                "timestamp": asyncio.get_event_loop().time(),
                "message": "SCP stream initialized",
                "source": "SCP",
                "severity": "info",
            }
        )
        if not ok:
            return

        while True:
            await asyncio.sleep(10)
            ok = await send_event(
                {
                    "type": "alert",
                    "id": f"heartbeat-{int(asyncio.get_event_loop().time())}",
                    "timestamp": asyncio.get_event_loop().time(),
                    "message": "SCP heartbeat",
                    "source": "SCP",
                    "severity": "info",
                }
            )
            if not ok:
                break
    except WebSocketDisconnect:
        logger.info("SCP WebSocket disconnected")
    except Exception as exc:  # noqa: BLE001
        logger.error(f"SCP WebSocket loop error: {exc}")
    finally:
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close()
