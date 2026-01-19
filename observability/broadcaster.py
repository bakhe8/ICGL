"""
Event Broadcaster
-----------------

WebSocket broadcaster for real-time event streaming to SCP dashboard.
"""

from typing import List, Set
from fastapi import WebSocket
from datetime import datetime

from ..observability.events import ObservabilityEvent


class EventBroadcaster:
    """
    Broadcasts observability events to WebSocket subscribers in real-time.
    
    Integration: Hook into ObservabilityLedger.log() to broadcast all events.
    """
    
    def __init__(self):
        self.subscribers: Set[WebSocket] = set()
    
    def subscribe(self, websocket: WebSocket):
        """Add WebSocket subscriber"""
        self.subscribers.add(websocket)
        print(f"📡 New SCP subscriber connected. Total: {len(self.subscribers)}")
    
    def unsubscribe(self, websocket: WebSocket):
        """Remove WebSocket subscriber"""
        self.subscribers.discard(websocket)
        print(f"📡 SCP subscriber disconnected. Total: {len(self.subscribers)}")
    
    async def broadcast_event(self, event: ObservabilityEvent):
        """
        Broadcast event to all connected subscribers.
        
        Automatically removes dead connections.
        """
        if not self.subscribers:
            return
        
        event_dict = event.to_dict()
        dead_connections = set()
        
        for websocket in self.subscribers:
            try:
                await websocket.send_json({
                    "type": "event",
                    "data": event_dict
                })
            except Exception as e:
                print(f"⚠️ Failed to send to subscriber: {e}")
                dead_connections.add(websocket)
        
        # Clean up dead connections
        for ws in dead_connections:
            self.unsubscribe(ws)
    
    async def broadcast_channel_update(self, channel_id: str, status: str, message_count: int, violations: int):
        """Broadcast channel status update"""
        if not self.subscribers:
            return
        
        update = {
            "type": "channel_update",
            "data": {
                "channel_id": channel_id,
                "status": status,
                "message_count": message_count,
                "violations": violations,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        dead_connections = set()
        for websocket in self.subscribers:
            try:
                await websocket.send_json(update)
            except Exception:
                dead_connections.add(websocket)
        
        for ws in dead_connections:
            self.unsubscribe(ws)


# Global broadcaster instance
_broadcaster = EventBroadcaster()

def get_broadcaster() -> EventBroadcaster:
    """Get global event broadcaster"""
    return _broadcaster
