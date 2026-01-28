from __future__ import annotations

"""
Consensus AI — SQLite Storage Backend
======================================

Persistent storage layer for the Knowledge Base using SQLite.

Features:
- CRUD operations for all entity types
- Automatic schema creation
- JSON serialization for complex fields
- Version tracking
"""

import json  # noqa: E402
import sqlite3  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import TYPE_CHECKING, Any, Dict, List, Optional  # noqa: E402

if TYPE_CHECKING:
    from .schemas import RoadmapItem

from typing import TYPE_CHECKING  # noqa: E402

from .schemas import (  # noqa: E402
    ADR,
    ID,
    AgentManifestEntry,
    AgentMetric,
    Concept,
    HumanDecision,
    InterventionLog,
    LearningLog,
    Policy,
    SentinelSignal,
    SigningRequest,
)


class StorageBackend:
    """
    SQLite-based persistent storage for Knowledge Base.

    Usage:
        storage = StorageBackend("data/kb.db")
        storage.save_concept(concept)
        concept = storage.load_concept("concept-authority")
    """

    def __init__(self, db_path: str = "data/kb.db"):
        """
        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a new database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        """Creates database tables if they don't exist."""
        with self._get_connection() as conn:
            conn.executescript("""
                -- Concepts table
                CREATE TABLE IF NOT EXISTS concepts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    definition TEXT NOT NULL,
                    invariants TEXT NOT NULL,  -- JSON array
                    anti_patterns TEXT NOT NULL,  -- JSON array
                    owner TEXT DEFAULT 'HUMAN',
                    version TEXT DEFAULT '1.0.0',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                -- Policies table
                CREATE TABLE IF NOT EXISTS policies (
                    id TEXT PRIMARY KEY,
                    code TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    rule TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    enforced_by TEXT NOT NULL,  -- JSON array
                    created_at TEXT NOT NULL
                );
                
                -- Sentinel Signals table
                CREATE TABLE IF NOT EXISTS signals (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    detection_hint TEXT NOT NULL,
                    introduced_in_cycle INTEGER NOT NULL
                );

                -- Signing Requests table
                CREATE TABLE IF NOT EXISTS signing_requests (
                    id TEXT PRIMARY KEY,
                    adr_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    proposed_by TEXT NOT NULL,
                    status TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    actions TEXT NOT NULL,  -- JSON array
                    timestamp TEXT NOT NULL
                );

                -- Agent Manifest table
                CREATE TABLE IF NOT EXISTS agent_manifest (
                    id TEXT PRIMARY KEY,
                    file TEXT NOT NULL,
                    role TEXT NOT NULL,
                    capabilities TEXT NOT NULL,  -- JSON array
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                -- Analysis Synthesis State table
                CREATE TABLE IF NOT EXISTS synthesis_states (
                    adr_id TEXT PRIMARY KEY,
                    state_data TEXT NOT NULL,  -- JSON blob
                    updated_at TEXT NOT NULL
                );
                
                -- ADRs table
                CREATE TABLE IF NOT EXISTS adrs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    context TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    consequences TEXT NOT NULL,  -- JSON array
                    related_policies TEXT NOT NULL,  -- JSON array
                    sentinel_signals TEXT NOT NULL,  -- JSON array
                    human_decision_id TEXT,
                    created_at TEXT NOT NULL
                );
                
                -- Human Decisions table
                CREATE TABLE IF NOT EXISTS human_decisions (
                    id TEXT PRIMARY KEY,
                    adr_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    signed_by TEXT NOT NULL,
                    signature_hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (adr_id) REFERENCES adrs(id)
                );
                
                -- Learning Logs table
                CREATE TABLE IF NOT EXISTS learning_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle INTEGER NOT NULL,
                    summary TEXT NOT NULL,
                    new_policies TEXT NOT NULL,  -- JSON array
                    new_signals TEXT NOT NULL,  -- JSON array
                    new_concepts TEXT NOT NULL,  -- JSON array
                    notes TEXT NOT NULL
                );
                
                -- Roadmap Items table
                CREATE TABLE IF NOT EXISTS roadmap_items (
                    id TEXT PRIMARY KEY,
                    cycle INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    goals TEXT NOT NULL, -- JSON array
                    governed_by_adr TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                -- Interventions table
                CREATE TABLE IF NOT EXISTS interventions (
                    id TEXT PRIMARY KEY,
                    adr_id TEXT NOT NULL,
                    original_recommendation TEXT NOT NULL,
                    human_action TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    diff_summary TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (adr_id) REFERENCES adrs(id)
                );

                -- Agent Metrics table
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    success INTEGER NOT NULL,
                    error_code TEXT,
                    timestamp TEXT NOT NULL
                );

                -- Merkle Sovereign Ledger
                CREATE TABLE IF NOT EXISTS merkle_ledger (
                    node_index INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_hash TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );

                -- Schema version tracking
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );
                
                -- Insert initial version if not exists
                INSERT OR IGNORE INTO schema_version (version, applied_at)
                VALUES (1, datetime('now'));
            """)
            conn.commit()

    # =========================================================================
    # Roadmap Operations
    # =========================================================================

    def save_roadmap_item(self, item: "RoadmapItem") -> None:
        """Saves or updates a roadmap item."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO roadmap_items 
                (id, cycle, title, status, goals, governed_by_adr, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item.id,
                    item.cycle,
                    item.title,
                    item.status,
                    json.dumps(item.goals),
                    item.governed_by_adr,
                    item.created_at,
                    item.updated_at,
                ),
            )
            conn.commit()

    def load_all_roadmap_items(self) -> List["RoadmapItem"]:
        """Loads all roadmap items."""
        # Local import to avoid circular dependency at runtime; also
        # provide a TYPE_CHECKING import so static checkers recognize the name.
        if TYPE_CHECKING:
            from .schemas import RoadmapItem  # type: ignore
        from .schemas import RoadmapItem

        items: List["RoadmapItem"] = []
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM roadmap_items ORDER BY cycle"):
                item = RoadmapItem(
                    id=row["id"],
                    cycle=row["cycle"],
                    title=row["title"],
                    status=row["status"],
                    goals=json.loads(row["goals"]),
                    governed_by_adr=row["governed_by_adr"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                items.append(item)
        return items

    # =========================================================================
    # Concept Operations
    # =========================================================================

    def save_concept(self, concept: Concept) -> None:
        """Saves or updates a concept."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO concepts 
                (id, name, definition, invariants, anti_patterns, owner, version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    concept.id,
                    concept.name,
                    concept.definition,
                    json.dumps(concept.invariants),
                    json.dumps(concept.anti_patterns),
                    concept.owner,
                    concept.version,
                    concept.created_at,
                    concept.updated_at,
                ),
            )
            conn.commit()

    def load_concept(self, concept_id: ID) -> Optional[Concept]:
        """Loads a concept by ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,)).fetchone()
            if row:
                return Concept(
                    id=row["id"],
                    name=row["name"],
                    definition=row["definition"],
                    invariants=json.loads(row["invariants"]),
                    anti_patterns=json.loads(row["anti_patterns"]),
                    owner=row["owner"],
                    version=row["version"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            return None

    def load_all_concepts(self) -> Dict[ID, Concept]:
        """Loads all concepts."""
        concepts = {}
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM concepts"):
                concept = Concept(
                    id=row["id"],
                    name=row["name"],
                    definition=row["definition"],
                    invariants=json.loads(row["invariants"]),
                    anti_patterns=json.loads(row["anti_patterns"]),
                    owner=row["owner"],
                    version=row["version"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                concepts[concept.id] = concept
        return concepts

    # =========================================================================
    # Policy Operations
    # =========================================================================

    def save_policy(self, policy: Policy) -> None:
        """Saves or updates a policy."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO policies 
                (id, code, title, rule, severity, enforced_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    policy.id,
                    policy.code,
                    policy.title,
                    policy.rule,
                    policy.severity,
                    json.dumps(policy.enforced_by),
                    policy.created_at,
                ),
            )
            conn.commit()

    def load_all_policies(self) -> Dict[ID, Policy]:
        """Loads all policies."""
        policies = {}
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM policies"):
                policy = Policy(
                    id=row["id"],
                    code=row["code"],
                    title=row["title"],
                    rule=row["rule"],
                    severity=row["severity"],
                    enforced_by=json.loads(row["enforced_by"]),
                    created_at=row["created_at"],
                )
                policies[policy.id] = policy
        return policies

    # =========================================================================
    # Signal Operations
    # =========================================================================

    def save_signal(self, signal: SentinelSignal) -> None:
        """Saves or updates a sentinel signal."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO signals 
                (id, name, description, category, detection_hint, default_action, introduced_in_cycle)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    signal.id,
                    signal.name,
                    signal.description,
                    signal.category,
                    signal.detection_hint,
                    signal.default_action,
                    signal.introduced_in_cycle,
                ),
            )
            conn.commit()

    def load_all_signals(self) -> Dict[ID, SentinelSignal]:
        """Loads all sentinel signals."""
        signals = {}
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM signals"):
                signal = SentinelSignal(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    category=row["category"],
                    detection_hint=row["detection_hint"],
                    default_action=row["default_action"],
                    introduced_in_cycle=row["introduced_in_cycle"],
                )
                signals[signal.id] = signal
        return signals

    # =========================================================================
    # ADR Operations
    # =========================================================================

    def save_adr(self, adr: ADR) -> None:
        """Saves or updates an ADR."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO adrs 
                (id, title, status, context, decision, consequences, 
                 related_policies, sentinel_signals, human_decision_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    adr.id,
                    adr.title,
                    adr.status,
                    adr.context,
                    adr.decision,
                    json.dumps(adr.consequences),
                    json.dumps(adr.related_policies),
                    json.dumps(adr.sentinel_signals),
                    adr.human_decision_id,
                    adr.created_at,
                ),
            )
            conn.commit()

    def load_all_adrs(self) -> Dict[ID, ADR]:
        """Loads all ADRs."""
        adrs = {}
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM adrs"):
                adr = ADR(
                    id=row["id"],
                    title=row["title"],
                    status=row["status"],
                    context=row["context"],
                    decision=row["decision"],
                    consequences=json.loads(row["consequences"]),
                    related_policies=json.loads(row["related_policies"]),
                    sentinel_signals=json.loads(row["sentinel_signals"]),
                    human_decision_id=row["human_decision_id"],
                    created_at=row["created_at"],
                )
                adrs[adr.id] = adr
        return adrs

    # =========================================================================
    # Human Decision Operations
    # =========================================================================

    def save_human_decision(self, decision: HumanDecision) -> None:
        """Saves a human decision."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO human_decisions 
                (id, adr_id, action, rationale, signed_by, signature_hash, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    decision.id,
                    decision.adr_id,
                    decision.action,
                    decision.rationale,
                    decision.signed_by,
                    decision.signature_hash,
                    decision.timestamp,
                ),
            )
            conn.commit()

    def load_all_human_decisions(self) -> Dict[ID, HumanDecision]:
        """Loads all human decisions."""
        decisions = {}
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM human_decisions"):
                decision = HumanDecision(
                    id=row["id"],
                    adr_id=row["adr_id"],
                    action=row["action"],
                    rationale=row["rationale"],
                    signed_by=row["signed_by"],
                    signature_hash=row["signature_hash"],
                    timestamp=row["timestamp"],
                )
                decisions[decision.id] = decision
        return decisions

    # =========================================================================
    # Learning Log Operations
    # =========================================================================

    def save_learning_log(self, log: LearningLog) -> None:
        """Saves a learning log entry."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO learning_logs 
                (cycle, summary, new_policies, new_signals, new_concepts, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    log.cycle,
                    log.summary,
                    json.dumps(log.new_policies),
                    json.dumps(log.new_signals),
                    json.dumps(log.new_concepts),
                    log.notes,
                ),
            )
            conn.commit()

    def load_all_learning_logs(self) -> List[LearningLog]:
        """Loads all learning logs."""
        logs = []
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM learning_logs ORDER BY cycle"):
                log = LearningLog(
                    cycle=row["cycle"],
                    summary=row["summary"],
                    new_policies=json.loads(row["new_policies"]),
                    new_signals=json.loads(row["new_signals"]),
                    new_concepts=json.loads(row["new_concepts"]),
                    notes=row["notes"],
                )
                logs.append(log)
        return logs

    # =========================================================================
    # Observability Operations
    # =========================================================================

    def save_intervention(self, log: "InterventionLog") -> None:
        """Saves a human intervention log."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO interventions 
                (id, adr_id, original_recommendation, human_action, reason, diff_summary, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    log.id,
                    log.adr_id,
                    log.original_recommendation,
                    log.human_action,
                    log.reason,
                    log.diff_summary,
                    log.timestamp,
                ),
            )
            conn.commit()

    def load_all_interventions(self) -> List["InterventionLog"]:
        """Loads all interventions."""
        from .schemas import InterventionLog

        interventions = []
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM interventions ORDER BY timestamp DESC"):
                interventions.append(
                    InterventionLog(
                        id=row["id"],
                        adr_id=row["adr_id"],
                        original_recommendation=row["original_recommendation"],
                        human_action=row["human_action"],
                        reason=row["reason"],
                        diff_summary=row["diff_summary"],
                        timestamp=row["timestamp"],
                    )
                )
        return interventions

    def save_agent_metric(self, metric: "AgentMetric") -> None:
        """Saves an agent performance metric."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO agent_metrics 
                (agent_id, role, task_type, latency_ms, confidence_score, success, error_code, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metric.agent_id,
                    metric.role,
                    metric.task_type,
                    metric.latency_ms,
                    metric.confidence_score,
                    1 if metric.success else 0,
                    metric.error_code,
                    metric.timestamp,
                ),
            )
            conn.commit()

    def append_merkle_node(self, node_hash: str, prev_hash: str, payload: str, timestamp: str) -> int:
        """Appends a node to the Merkle Sovereign Ledger."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO merkle_ledger (node_hash, prev_hash, payload, timestamp)
                VALUES (?, ?, ?, ?)
            """,
                (node_hash, prev_hash, payload, timestamp),
            )
            conn.commit()
            return int(cursor.lastrowid) if cursor.lastrowid is not None else -1

    def load_merkle_ledger(self) -> List[dict]:
        """Loads the entire Merkle ledger for verification."""
        ledger = []
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM merkle_ledger ORDER BY node_index ASC"):
                ledger.append(dict(row))
        return ledger

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def save_signing_request(self, request: SigningRequest):
        """Persists a signing request to the database."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO signing_requests 
                (id, adr_id, title, description, proposed_by, status, risk_level, actions, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.id,
                    request.adr_id,
                    request.title,
                    request.description,
                    request.proposed_by,
                    request.status,
                    request.risk_level,
                    json.dumps(request.actions),
                    request.timestamp,
                ),
            )

    def load_all_signing_requests(self) -> Dict[str, SigningRequest]:
        """Loads all signing requests from the database."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM signing_requests")
            rows = cursor.fetchall()
            requests = {}
            for row in rows:
                requests[row["id"]] = SigningRequest(
                    id=row["id"],
                    adr_id=row["adr_id"],
                    title=row["title"],
                    description=row["description"],
                    proposed_by=row["proposed_by"],
                    status=row["status"],
                    risk_level=row["risk_level"],
                    actions=json.loads(row["actions"]),
                    timestamp=row["timestamp"],
                )
            return requests

    def save_agent_entry(self, entry: AgentManifestEntry):
        """Persists an agent manifest entry to the database."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO agent_manifest 
                (id, file, role, capabilities, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.id,
                    entry.file,
                    entry.role,
                    json.dumps(entry.capabilities),
                    entry.status,
                    entry.created_at,
                ),
            )

    def load_all_agent_entries(self) -> Dict[str, AgentManifestEntry]:
        """Loads all agent manifest entries from the database."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM agent_manifest")
            rows = cursor.fetchall()
            entries = {}
            for row in rows:
                entries[row["id"]] = AgentManifestEntry(
                    id=row["id"],
                    file=row["file"],
                    role=row["role"],
                    capabilities=json.loads(row["capabilities"]),
                    status=row["status"],
                    created_at=row["created_at"],
                )
            return entries

    def save_synthesis_state(self, adr_id: str, state_data: Dict[str, Any]):
        """Persists an analysis synthesis state to the database."""
        from .schemas import now

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO synthesis_states (adr_id, state_data, updated_at)
                VALUES (?, ?, ?)
                """,
                (adr_id, json.dumps(state_data), now()),
            )

    def load_all_synthesis_states(self) -> Dict[str, Any]:
        """Loads all synthesis states from the database."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM synthesis_states")
            rows = cursor.fetchall()
            states = {}
            for row in rows:
                states[row["adr_id"]] = json.loads(row["state_data"])
            return states

    def get_stats(self) -> Dict[str, int]:
        """Returns counts for all entity types."""
        with self._get_connection() as conn:
            return {
                "concepts": conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0],
                "policies": conn.execute("SELECT COUNT(*) FROM policies").fetchone()[0],
                "signals": conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0],
                "adrs": conn.execute("SELECT COUNT(*) FROM adrs").fetchone()[0],
                "human_decisions": conn.execute("SELECT COUNT(*) FROM human_decisions").fetchone()[0],
                "learning_logs": conn.execute("SELECT COUNT(*) FROM learning_logs").fetchone()[0],
                "signing_requests": conn.execute("SELECT COUNT(*) FROM signing_requests").fetchone()[0],
                "agents": conn.execute("SELECT COUNT(*) FROM agent_manifest").fetchone()[0],
                "synthesis_states": conn.execute("SELECT COUNT(*) FROM synthesis_states").fetchone()[0],
            }

    def clear_all(self) -> None:
        """Clears all data (use with caution!)."""
        with self._get_connection() as conn:
            conn.executescript("""
                DELETE FROM learning_logs;
                DELETE FROM human_decisions;
                DELETE FROM adrs;
                DELETE FROM signals;
                DELETE FROM policies;
                DELETE FROM concepts;
                DELETE FROM signing_requests;
                DELETE FROM agent_manifest;
                DELETE FROM synthesis_states;
            """)
            conn.commit()
