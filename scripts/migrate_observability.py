#!/usr/bin/env python3
"""Quick DB migration helper for observability ledger.

Usage:
  python scripts/migrate_observability.py
  python scripts/migrate_observability.py --db path/to/observability.db

This script will:
- Create `events` table if missing
- Add `session_id` column if missing (default 'unknown')
- Create common indexes (best-effort)
"""

import argparse
import sqlite3
import sys
from pathlib import Path

SCHEMA_SQL = """
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
"""

INDEXES = [
    ("idx_trace", "CREATE INDEX IF NOT EXISTS idx_trace ON events(trace_id)"),
    ("idx_session", "CREATE INDEX IF NOT EXISTS idx_session ON events(session_id)"),
    ("idx_adr", "CREATE INDEX IF NOT EXISTS idx_adr ON events(adr_id)"),
    ("idx_timestamp", "CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp DESC)"),
    ("idx_type", "CREATE INDEX IF NOT EXISTS idx_type ON events(event_type)"),
]


def migrate(db_path: Path) -> int:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        # Ensure table exists
        conn.execute(SCHEMA_SQL)

        # Check columns
        cursor = conn.execute("PRAGMA table_info(events)")
        cols = [r[1] for r in cursor.fetchall()]
        if "session_id" not in cols:
            print("- session_id column missing: adding column...")
            conn.execute("ALTER TABLE events ADD COLUMN session_id TEXT NOT NULL DEFAULT 'unknown'")
        else:
            print("- session_id column exists")

        # Ensure adr_id exists (older DBs may lack it)
        if "adr_id" not in cols:
            print("- adr_id column missing: adding column...")
            conn.execute("ALTER TABLE events ADD COLUMN adr_id TEXT")
        else:
            print("- adr_id column exists")

        # Create indexes best-effort
        for name, sql in INDEXES:
            try:
                conn.execute(sql)
            except Exception:
                # Ignore index creation errors on odd schemas
                pass

        conn.commit()
        print(f"Migration OK: {db_path}")
        return 0
    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        return 2
    finally:
        conn.close()


def main():
    p = Path(__file__).resolve()
    default_db = p.parent.parent / "data" / "observability.db"

    parser = argparse.ArgumentParser(description="Migrate observability DB schema")
    parser.add_argument("--db", type=Path, default=default_db, help="Path to observability.db")
    args = parser.parse_args()

    rc = migrate(args.db)
    sys.exit(rc)


if __name__ == "__main__":
    main()
