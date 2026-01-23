import asyncio
from typing import Any, Set


class Broadcaster:
    """
    Simple async broadcaster: يحتفظ بقائمة المشتركين (WebSockets) ويرسل لهم الرسائل.
    """

    def __init__(self):
        self._subscribers: Set[Any] = set()

    def subscribe(self, websocket) -> bool:
        self._subscribers.add(websocket)
        return True

    def unsubscribe(self, websocket) -> bool:
        if websocket in self._subscribers:
            self._subscribers.remove(websocket)
        return True

    async def broadcast(self, message: Any) -> None:
        dead = []
        for ws in list(self._subscribers):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.unsubscribe(ws)

    def broadcast_nowait(self, message: Any) -> None:
        """جدولة الإرسال دون حجب الخيط الحالي."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.broadcast(message))
        except Exception:
            pass


def get_broadcaster():
    return Broadcaster()
