"""
Consensus AI — Observability Storage
====================================
Persistent SQLite storage for the Observability Ledger.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


_ledger_instance: "SQLiteLedger" | None = None


class SQLiteLedger:
    def __init__(self, db_path: str = "data/observability.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Events Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                user_id TEXT,
                trace_id TEXT,
                payload TEXT,
                timestamp TEXT
            )
        """)

        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trace_id ON events(trace_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")

        conn.commit()
        conn.close()

    def log(
        self,
        event_type,
        user_id: str,
        trace_id: str,
        input_payload: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Logs an event to SQLite."""
        timestamp = datetime.utcnow().isoformat()
        payload_str = json.dumps(input_payload or {})
        evt_type_str = getattr(event_type, "value", str(event_type))

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO events (event_type, user_id, trace_id, payload, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """,
            (evt_type_str, user_id, trace_id, payload_str, timestamp),
        )
        conn.commit()
        conn.close()

        return {
            "event_type": evt_type_str,
            "user_id": user_id,
            "trace_id": trace_id,
            "payload": input_payload or {},
            "timestamp": timestamp,
        }

    def get_stats(self) -> Dict[str, int]:
        """Returns basic stats."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT trace_id) FROM events")
        trace_count = cursor.fetchone()[0]
        conn.close()
        return {
            "trace_count": trace_count,
            "event_count": event_count,
        }

    def get_recent_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent unique traces (reconstructed from events)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Group by trace_id to get latest timestamp for that trace
        cursor.execute(
            """
            SELECT trace_id, MAX(timestamp) as last_seen
            FROM events
            GROUP BY trace_id
            ORDER BY last_seen DESC
            LIMIT ?
        """,
            (limit,),
        )
        rows = cursor.fetchall()

        # To match previous interface, we might want to return a list of events per trace
        # But the original get_recent_traces returned a list of lists of events (traces)
        # Let's reconstruct them.
        traces = []
        for trace_id, _ in rows:
            traces.append(self.get_trace(trace_id))

        conn.close()
        return traces

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Returns all events for a specific trace_id."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM events WHERE trace_id = ? ORDER BY id ASC", (trace_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        events = []
        for row in rows:
            events.append(
                {
                    "event_type": row["event_type"],
                    "user_id": row["user_id"],
                    "trace_id": row["trace_id"],
                    "payload": json.loads(row["payload"]),
                    "timestamp": row["timestamp"],
                }
            )
        return events

    def query_events(
        self, trace_id=None, session_id=None, adr_id=None, event_type=None, limit=100
    ) -> List[Dict[str, Any]]:
        """Query events with filters."""
        query = "SELECT * FROM events WHERE 1=1"
        params = []

        if trace_id:
            query += " AND trace_id = ?"
            params.append(trace_id)

        if event_type:
            query += " AND event_type = ?"
            params.append(getattr(event_type, "value", str(event_type)))

        # session_id and adr_id are inside payload JSON in this schema,
        # so we can't efficiently index them without schema migration or generated columns.
        # For now, we fetch and filter in python if those params are present,
        # or use JSON_EXTRACT if sqlite supports it (most modern do).

        # Let's try basic SQL filtering for columns we have, then Python filter for payload specific.
        # Note: SQLite JSON support depends on compilation. Assuming basic python filter for safety/portability.

        query += " ORDER BY id DESC LIMIT ?"
        # Fetch more to allow for post-filtering
        params.append(limit * 5 if (session_id or adr_id) else limit)

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            evt = {
                "event_type": row["event_type"],
                "user_id": row["user_id"],
                "trace_id": row["trace_id"],
                "payload": json.loads(row["payload"]),
                "timestamp": row["timestamp"],
            }

            # Post-filter for payload fields
            if session_id and evt["payload"].get("session_id") != session_id:
                continue
            if adr_id and evt["payload"].get("adr_id") != adr_id:
                continue

            results.append(evt)
            if len(results) >= limit:
                break

        return results


def init_observability(db_path: str = "data/observability.db") -> None:
    global _ledger_instance
    _ledger_instance = SQLiteLedger(db_path)


def get_ledger() -> SQLiteLedger:
    global _ledger_instance
    if _ledger_instance is None:
        _ledger_instance = SQLiteLedger("data/observability.db")
    return _ledger_instance
