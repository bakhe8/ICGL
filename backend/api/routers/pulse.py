import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from backend.core.bus import get_bus

router = APIRouter()
bus = get_bus()

# Global set of active queues for broadcasting
active_connections = set()


async def broadcast_event(msg):
    """
    Callback that pushes bus messages to all active SSE queues.
    """
    dead_queues = set()
    for queue in active_connections:
        try:
            # We only push a simplified version for the UI to save bandwidth
            data = {
                "id": msg.id,
                "topic": msg.topic,
                "sender": msg.sender,
                "timestamp": msg.timestamp * 1000,  # JS ms
                "priority": msg.priority.name,
            }
            await queue.put(data)
        except Exception:
            dead_queues.add(queue)

    # Cleanup
    for q in dead_queues:
        active_connections.remove(q)


# Register the broadcaster once
bus.subscribe_all(broadcast_event)


@router.get("/stream")
async def sse_endpoint(request: Request):
    """
    Server-Sent Events endpoint for the Nervous System Monitor.
    """
    queue = asyncio.Queue()
    active_connections.add(queue)

    async def event_generator() -> AsyncGenerator:
        try:
            while True:
                if await request.is_disconnected():
                    break

                # Wait for next event
                data = await queue.get()
                yield {"event": "pulse", "data": json.dumps(data)}
        except asyncio.CancelledError:
            pass
        finally:
            active_connections.remove(queue)

    return EventSourceResponse(event_generator())
