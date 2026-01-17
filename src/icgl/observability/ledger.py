"""
Observability Ledger
--------------------

Append-only event store for complete system observability.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from .events import ObservabilityEvent, EventType
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class ObservabilityLedger:
    """
    Append-only event store for full system observability.
    
    Design Principles:
    - Write-optimized (append-only, no updates/deletes)
    - Queryable by trace_id, session_id, adr_id, time range
    - Minimal performance overhead
    - Persistent across restarts
    """
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"📊 Observability Ledger initialized at {self.db_path}")
    
    def _init_db(self):
        """Initialize SQLite schema with optimized indexes"""
        conn = sqlite3.connect(str(self.db_path))
        
        # Main events table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                trace_id TEXT NOT NULL,
                span_id TEXT NOT NULL,
                parent_span_id TEXT,
                session_id TEXT NOT NULL,
                adr_id TEXT,
                actor_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                action TEXT NOT NULL,
                target TEXT,
                input_payload TEXT,
                output_payload TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                duration_ms INTEGER,
                tags TEXT
            )
        """)
        
        # Indexes for common query patterns
        conn.execute("CREATE INDEX IF NOT EXISTS idx_trace ON events(trace_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON events(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_adr ON events(adr_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON events(event_type)")
        
        conn.commit()
        conn.close()
    
    def log(self, event: ObservabilityEvent) -> None:
        """
        Append event to ledger.
        
        This is write-optimized and should have minimal overhead.
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("""
                INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.event_type.value,
                event.timestamp.isoformat(),
                event.trace_id,
                event.span_id,
                event.parent_span_id,
                event.session_id,
                event.adr_id,
                event.actor_type,
                event.actor_id,
                event.action,
                event.target,
                json.dumps(event.input_payload) if event.input_payload else None,
                json.dumps(event.output_payload) if event.output_payload else None,
                event.status,
                event.error_message,
                event.duration_ms,
                json.dumps(event.tags)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Failed to log event {event.event_id}: {e}")
    
    def get_trace(self, trace_id: str) -> List[ObservabilityEvent]:
        """
        Retrieve all events for a trace (for replay).
        
        Returns events in chronological order.
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT * FROM events 
            WHERE trace_id = ? 
            ORDER BY timestamp ASC
        """, (trace_id,))
        
        events = [self._row_to_event(row) for row in cursor.fetchall()]
        conn.close()
        return events
    
    def get_recent_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of recent traces with metadata"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT 
                trace_id,
                MIN(timestamp) as start_time,
                MAX(timestamp) as end_time,
                COUNT(*) as event_count,
                MAX(adr_id) as adr_id,
                MAX(session_id) as session_id
            FROM events
            GROUP BY trace_id
            ORDER BY start_time DESC
            LIMIT ?
        """, (limit,))
        
        traces = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return traces
    
    def query_events(
        self,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        adr_id: Optional[str] = None,
        event_type: Optional[EventType] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ObservabilityEvent]:
        """Query events with filters"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        conditions = []
        params = []
        
        if trace_id:
            conditions.append("trace_id = ?")
            params.append(trace_id)
        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)
        if adr_id:
            conditions.append("adr_id = ?")
            params.append(adr_id)
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type.value)
        if since:
            conditions.append("timestamp >= ?")
            params.append(since.isoformat())
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"""
            SELECT * FROM events 
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        params.append(limit)
        
        cursor = conn.execute(query, params)
        events = [self._row_to_event(row) for row in cursor.fetchall()]
        conn.close()
        return events
    
    def _row_to_event(self, row: sqlite3.Row) -> ObservabilityEvent:
        """Convert database row to ObservabilityEvent"""
        return ObservabilityEvent(
            event_id=row["event_id"],
            event_type=EventType(row["event_type"]),
            timestamp=datetime.fromisoformat(row["timestamp"]),
            trace_id=row["trace_id"],
            span_id=row["span_id"],
            parent_span_id=row["parent_span_id"],
            session_id=row["session_id"],
            adr_id=row["adr_id"],
            actor_type=row["actor_type"],
            actor_id=row["actor_id"],
            action=row["action"],
            target=row["target"],
            input_payload=json.loads(row["input_payload"]) if row["input_payload"] else None,
            output_payload=json.loads(row["output_payload"]) if row["output_payload"] else None,
            status=row["status"],
            error_message=row["error_message"],
            duration_ms=row["duration_ms"],
            tags=json.loads(row["tags"]) if row["tags"] else {}
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ledger statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(DISTINCT trace_id) as total_traces,
                COUNT(DISTINCT session_id) as total_sessions,
                MIN(timestamp) as oldest_event,
                MAX(timestamp) as newest_event
            FROM events
        """)
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total_events": row[0],
            "total_traces": row[1],
            "total_sessions": row[2],
            "oldest_event": row[3],
            "newest_event": row[4],
            "db_size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0
        }
