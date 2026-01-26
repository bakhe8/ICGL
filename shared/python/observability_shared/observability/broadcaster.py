import asyncio
from typing import Any, Set


class Broadcaster:
    """
    Simple async broadcaster: يحتفظ بقائمة المشتركين (WebSockets) ويرسل لهم الرسائل.
    """

    def __init__(self):
        self._subscribers: Set[Any] = set()
        self._internal_observers: Set[Any] = set()

    def subscribe(self, websocket) -> bool:
        self._subscribers.add(websocket)
        return True

    def unsubscribe(self, websocket) -> bool:
        if websocket in self._subscribers:
            self._subscribers.remove(websocket)
        return True

    async def broadcast(self, message: Any) -> None:
        # 1. UI Broadcast (WebSockets)
        dead = []
        for ws in list(self._subscribers):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.unsubscribe(ws)

        # 2. Internal Agent Broadcast (Silent Monitoring)
        # Assuming internal_observers are callables (async function pointers)
        for callback in list(self._internal_observers):
            try:
                # Fire and forget / Silent
                asyncio.create_task(callback(message))
            except Exception as e:
                print(f"⚠️ Internal observer failed: {e}")

    def subscribe_internal(self, callback) -> None:
        """Allow agents to listen silently."""
        self._internal_observers.add(callback)

    def unsubscribe_internal(self, callback) -> None:
        if callback in self._internal_observers:
            self._internal_observers.remove(callback)

    def broadcast_nowait(self, message: Any) -> None:
        """جدولة الإرسال دون حجب الخيط الحالي."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.broadcast(message))
        except Exception:
            pass


_global_broadcaster = None


def get_broadcaster():
    global _global_broadcaster
    if _global_broadcaster is None:
        _global_broadcaster = Broadcaster()
    return _global_broadcaster
