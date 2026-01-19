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

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import asdict

from .schemas import (
    ID, Concept, Policy, SentinelSignal, ADR, HumanDecision, LearningLog, Procedure, OperationalRequest
)


class StorageBackend:
    """
    SQLite-based persistent storage for Knowledge Base.
    
    Usage:
        storage = StorageBackend("data/kb.db")
        storage.save_concept(concept)
        concept = storage.load_concept("concept-authority")
    """
    
    def __init__(self, db_path: str = "data/sovereign.db"):
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
                    default_action TEXT NOT NULL,
                    introduced_in_cycle INTEGER NOT NULL
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

                -- Procedures table
                CREATE TABLE IF NOT EXISTS procedures (
                    id TEXT PRIMARY KEY,
                    code TEXT NOT NULL,
                    title TEXT NOT NULL,
                    type TEXT NOT NULL,
                    steps TEXT NOT NULL, -- JSON array
                    required_tools TEXT NOT NULL, -- JSON array
                    version TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                -- Operational Requests table
                CREATE TABLE IF NOT EXISTS operational_requests (
                    id TEXT PRIMARY KEY,
                    requester_id TEXT NOT NULL,
                    target_department TEXT NOT NULL,
                    requirement TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    urgency TEXT NOT NULL,
                    expected_output TEXT,
                    risk_level TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_data TEXT,
                    governance_adr_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
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

                -- Proposals table
                CREATE TABLE IF NOT EXISTS proposals (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    proposal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    requester TEXT,
                    executive_brief TEXT,
                    impact TEXT,
                    details TEXT
                );

                -- System Metadata table (replacing JSON state files)
                CREATE TABLE IF NOT EXISTS system_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                -- Agent Logs table (replacing archivist_events.jsonl)
                CREATE TABLE IF NOT EXISTS agent_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    policy_code TEXT,
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
            conn.execute("""
                INSERT OR REPLACE INTO roadmap_items 
                (id, cycle, title, status, goals, governed_by_adr, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id,
                item.cycle,
                item.title,
                item.status,
                json.dumps(item.goals),
                item.governed_by_adr,
                item.created_at,
                item.updated_at
            ))
            conn.commit()

    def load_all_roadmap_items(self) -> List["RoadmapItem"]:
        """Loads all roadmap items."""
        from .schemas import RoadmapItem # Local import to avoid circular dependency if any
        items = []
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
                    updated_at=row["updated_at"]
                )
                items.append(item)
        return items    
    # =========================================================================
    # Concept Operations
    # =========================================================================
    
    def save_concept(self, concept: Concept) -> None:
        """Saves or updates a concept."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO concepts 
                (id, name, definition, invariants, anti_patterns, owner, version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                concept.id,
                concept.name,
                concept.definition,
                json.dumps(concept.invariants),
                json.dumps(concept.anti_patterns),
                concept.owner,
                concept.version,
                concept.created_at,
                concept.updated_at
            ))
            conn.commit()
    
    def load_concept(self, concept_id: ID) -> Optional[Concept]:
        """Loads a concept by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM concepts WHERE id = ?", (concept_id,)
            ).fetchone()
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
                    updated_at=row["updated_at"]
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
                    updated_at=row["updated_at"]
                )
                concepts[concept.id] = concept
        return concepts
    
    # =========================================================================
    # Policy Operations
    # =========================================================================
    
    def save_policy(self, policy: Policy) -> None:
        """Saves or updates a policy."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO policies 
                (id, code, title, rule, severity, enforced_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                policy.id,
                policy.code,
                policy.title,
                policy.rule,
                policy.severity,
                json.dumps(policy.enforced_by),
                policy.created_at
            ))
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
                    created_at=row["created_at"]
                )
                policies[policy.id] = policy
        return policies
    
    # =========================================================================
    # Signal Operations
    # =========================================================================
    
    def save_signal(self, signal: SentinelSignal) -> None:
        """Saves or updates a sentinel signal."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO signals 
                (id, name, description, category, detection_hint, default_action, introduced_in_cycle)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                signal.id,
                signal.name,
                signal.description,
                signal.category,
                signal.detection_hint,
                signal.default_action,
                signal.introduced_in_cycle
            ))
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
                    introduced_in_cycle=row["introduced_in_cycle"]
                )
                signals[signal.id] = signal
        return signals
    
    # =========================================================================
    # ADR Operations
    # =========================================================================
    
    def save_adr(self, adr: ADR) -> None:
        """Saves or updates an ADR."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO adrs 
                (id, title, status, context, decision, consequences, 
                related_policies, sentinel_signals, human_decision_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                adr.id,
                adr.title,
                adr.status,
                adr.context,
                adr.decision,
                json.dumps(adr.consequences),
                json.dumps(adr.related_policies),
                json.dumps(adr.sentinel_signals),
                adr.human_decision_id,
                adr.created_at
            ))
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
                    created_at=row["created_at"]
                )
                adrs[adr.id] = adr
        return adrs

    def delete_adr(self, adr_id: ID) -> None:
        """Deletes an ADR and any linked human decisions."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM human_decisions WHERE adr_id = ?", (adr_id,))
            conn.execute("DELETE FROM adrs WHERE id = ?", (adr_id,))
            conn.commit()
    
    # =========================================================================
    # Human Decision Operations
    # =========================================================================
    
    def save_human_decision(self, decision: HumanDecision) -> None:
        """Saves a human decision."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO human_decisions 
                (id, adr_id, action, rationale, signed_by, signature_hash, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                decision.id,
                decision.adr_id,
                decision.action,
                decision.rationale,
                decision.signed_by,
                decision.signature_hash,
                decision.timestamp
            ))
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
                    timestamp=row["timestamp"]
                )
                decisions[decision.id] = decision
        return decisions
    
    # =========================================================================
    # Learning Log Operations
    # =========================================================================
    
    def save_learning_log(self, log: LearningLog) -> None:
        """Saves a learning log entry."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO learning_logs 
                (cycle, summary, new_policies, new_signals, new_concepts, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                log.cycle,
                log.summary,
                json.dumps(log.new_policies),
                json.dumps(log.new_signals),
                json.dumps(log.new_concepts),
                log.notes
            ))
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
                    notes=row["notes"]
                )
                logs.append(log)
        return logs

    # =========================================================================
    # Procedure Operations
    # =========================================================================

    def save_procedure(self, procedure: Procedure) -> None:
        """Saves or updates a procedure."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO procedures
                (id, code, title, type, steps, required_tools, version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                procedure.id,
                procedure.code,
                procedure.title,
                procedure.type,
                json.dumps(procedure.steps),
                json.dumps(procedure.required_tools),
                procedure.version,
                procedure.created_at,
                procedure.updated_at
            ))
            conn.commit()

    def load_all_procedures(self) -> Dict[ID, Procedure]:
        """Loads all procedures."""
        procedures: Dict[ID, Procedure] = {}
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM procedures"):
                proc = Procedure(
                    id=row["id"],
                    code=row["code"],
                    title=row["title"],
                    type=row["type"],
                    steps=json.loads(row["steps"]),
                    required_tools=json.loads(row["required_tools"]),
                    version=row["version"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                procedures[proc.id] = proc
        return procedures

    # =========================================================================
    # Operational Request Operations
    # =========================================================================

    def save_operational_request(self, request: OperationalRequest) -> None:
        """Saves or updates an operational request."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO operational_requests
                (id, requester_id, target_department, requirement, rationale, urgency,
                expected_output, risk_level, status, response_data, governance_adr_id,
                created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.id,
                request.requester_id,
                request.target_department,
                request.requirement,
                request.rationale,
                request.urgency,
                request.expected_output,
                request.risk_level,
                request.status,
                request.response_data,
                request.governance_adr_id,
                request.created_at,
                request.updated_at
            ))
            conn.commit()

    def load_all_operational_requests(self) -> Dict[ID, OperationalRequest]:
        """Loads all operational requests."""
        requests: Dict[ID, OperationalRequest] = {}
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM operational_requests"):
                req = OperationalRequest(
                    id=row["id"],
                    requester_id=row["requester_id"],
                    target_department=row["target_department"],
                    requirement=row["requirement"],
                    rationale=row["rationale"],
                    urgency=row["urgency"],
                    expected_output=row["expected_output"],
                    risk_level=row["risk_level"],
                    status=row["status"],
                    response_data=row["response_data"],
                    governance_adr_id=row["governance_adr_id"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                requests[req.id] = req
        return requests
    
    # =========================================================================
    # Proposal Operations
    # =========================================================================

    def save_proposal(self, proposal: "Proposal") -> None:
        """Saves or updates a proposal."""
        from .schemas import Proposal # Local import
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO proposals 
                (id, agent_id, proposal, status, timestamp, requester, executive_brief, impact, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                proposal.id,
                proposal.agent_id,
                proposal.proposal,
                proposal.status,
                proposal.timestamp,
                proposal.requester,
                proposal.executive_brief,
                proposal.impact,
                proposal.details
            ))
            conn.commit()

    def load_all_proposals(self) -> List["Proposal"]:
        """Loads all proposals."""
        from .schemas import Proposal # Local import
        proposals = []
        with self._get_connection() as conn:
            for row in conn.execute("SELECT * FROM proposals ORDER BY timestamp"):
                prop = Proposal(
                    id=row["id"],
                    agent_id=row["agent_id"],
                    proposal=row["proposal"],
                    status=row["status"],
                    timestamp=row["timestamp"],
                    requester=row["requester"],
                    executive_brief=row["executive_brief"],
                    impact=row["impact"],
                    details=row["details"]
                )
                proposals.append(prop)
        return proposals

    # =========================================================================
    # Metadata & Logs Operations
    # =========================================================================

    def save_metadata(self, key: str, value: Any) -> None:
        """Saves metadata as JSON string."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO system_metadata (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, json.dumps(value), datetime.utcnow().isoformat()))
            conn.commit()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Loads metadata and parses JSON."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT value FROM system_metadata WHERE key = ?", (key,)).fetchone()
            if row:
                return json.loads(row["value"])
            return default

    def delete_metadata(self, key: str) -> None:
        """Deletes a metadata key."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM system_metadata WHERE key = ?", (key,))
            conn.commit()

    def save_agent_log(self, agent_id: str, event_type: str, payload: Dict[str, Any], policy_code: Optional[str] = None) -> None:
        """Saves a structured agent log entry."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO agent_logs (agent_id, event_type, policy_code, payload, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (agent_id, event_type, policy_code, json.dumps(payload), datetime.utcnow().isoformat()))
            conn.commit()

    def get_recent_agent_logs(self, agent_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent agent logs."""
        logs = []
        query = "SELECT * FROM agent_logs"
        params = []
        if agent_id:
            query += " WHERE agent_id = ?"
            params.append(agent_id)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            for row in conn.execute(query, params):
                logs.append({
                    "agent_id": row["agent_id"],
                    "event_type": row["event_type"],
                    "policy_code": row["policy_code"],
                    "payload": json.loads(row["payload"]),
                    "timestamp": row["timestamp"]
                })
        return logs

    # =========================================================================
    # Utility Methods
    # =========================================================================
    
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
                "metadata_keys": conn.execute("SELECT COUNT(*) FROM system_metadata").fetchone()[0],
                "agent_logs": conn.execute("SELECT COUNT(*) FROM agent_logs").fetchone()[0],
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
                DELETE FROM system_metadata;
                DELETE FROM agent_logs;
            """)
            conn.commit()
