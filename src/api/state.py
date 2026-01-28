from typing import List

from fastapi import WebSocket

from src.core.utils.logging_config import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected WebSocket clients."""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Broadcast error: {e}")
                dead_connections.append(connection)

        for conn in dead_connections:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


# Singletons for the entire API application
manager = ConnectionManager()
scp_manager = ConnectionManager()
chat_ws_manager = ConnectionManager()

# Shared synthesis context (REMOVED - now persistent in KB)
# active_synthesis: Dict[str, Any] = {}
