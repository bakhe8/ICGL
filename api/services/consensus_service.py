from typing import Optional, Dict, Any
from datetime import datetime
import json

from api.repositories.policy_repo import PolicyRepository
from api.repositories.adr_repo import AdrRepository
from api.repositories.learning_repo import LearningRepository
from api.repositories.decision_repo import DecisionRepository
from api.dependencies import root_dir
from utils.logging_config import get_logger

logger = get_logger(__name__)

from api.repositories.metadata_repo import MetadataRepository

class ConsensusService:
    def __init__(self):
        self.policy_repo = PolicyRepository()
        self.adr_repo = AdrRepository()
        self.learning_repo = LearningRepository()
        self.metadata_repo = MetadataRepository()
        self.decision_repo = DecisionRepository()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self.metadata_repo.get_value(key, default)

    def save_metadata(self, key: str, value: Any):
        self.metadata_repo.set_value(key, value)
        # In Phase 9, we can inject Services for Sentinel/HDAL here

    def _persist_adr_file(self, adr: Dict[str, Any]) -> None:
        """
        Persist ADR as an individual JSON file for traceability (Phase 14.2 requirement).
        """
        adr_dir = root_dir / "data" / "kb" / "adrs"
        adr_dir.mkdir(parents=True, exist_ok=True)
        adr_path = adr_dir / f"{adr['id']}.json"
        adr_path.write_text(json.dumps(adr, indent=2, default=str), encoding="utf-8")

    def propose_adr(self, title: str, context: str, decision: str, reason: Optional[str] = None, impact: Optional[str] = None) -> dict:
        """Creates a new ADR proposal."""
        new_adr = {
            "id": f"ADR-{int(datetime.utcnow().timestamp())}",
            "title": title,
            "status": "PROPOSED",
            "context": context,
            "decision": decision,
            "reason": reason,
            "impact": impact,
            "created_at": datetime.utcnow().isoformat(),
            "related_policies": [],
            "sentinel_signals": []
        }
        self.adr_repo.add(new_adr)
        logger.info(f"New ADR Proposed: {new_adr['id']}")
        self._persist_adr_file(new_adr)
        return new_adr

    def check_policy_compliance(self, adr_id: str) -> dict:
        """Mock Policy Check - In future, integrates real PolicyEnforcer logic."""
        adr = self.adr_repo.find_by_id(adr_id)
        if not adr:
            return {"status": "error", "message": "ADR not found"}
        
        # Simple heuristic check
        status = "PASS"
        issues = []
        if "policy" in adr["title"].lower():
             # Example logic
             pass
        
        return {"status": status, "issues": issues}

    def register_policy(self, code: str, title: str, rule: str, severity: str = "HIGH"):
        policy = {
            "id": f"pol-{code.lower()}",
            "code": code,
            "title": title,
            "rule": rule,
            "severity": severity,
            "created_at": datetime.utcnow().isoformat()
        }
        return self.policy_repo.save_policy(policy)

    def create_policy_draft(self, code: str, title: str, content: str) -> dict:
        draft = {
             "code": code,
             "title": title,
             "content": content,
             "status": "DRAFT",
             "created_at": datetime.utcnow().isoformat()
        }
        return self.policy_repo.save_draft(draft)

    def find_policy_conflicts(self, content: str) -> list:
        # Simple keyword matching for now
        conflicts = []
        all_policies = self.policy_repo.get_all()
        content_lower = content.lower()
        for p in all_policies:
            # Primitive checking: if policy title words appear in content
            words = p.get("title", "").lower().split()
            if any(w in content_lower for w in words if len(w) > 4):
                 conflicts.append(f"Potential conflict with {p.get('code')}: {p.get('title')}")
        return conflicts

    def register_decision(self, proposal_id: str, decision: str, rationale: str, signed_by: str = "operator") -> dict:
        """
        Register a human/agent decision on an ADR, update ADR status, and persist a decision log.
        """
        record = {
            "id": f"DEC-{int(datetime.utcnow().timestamp())}",
            "proposal_id": proposal_id,
            "decision": decision,
            "rationale": rationale,
            "signed_by": signed_by,
            "created_at": datetime.utcnow().isoformat()
        }
        self.decision_repo.add(record)

        # Update ADR status to mirror decision outcome
        adr = self.adr_repo.find_by_id(proposal_id)
        if adr:
            status_map = {
                "approved": "ACCEPTED",
                "rejected": "REJECTED",
                "deferred": "CONDITIONAL",
                "pending": adr.get("status", "PROPOSED")
            }
            adr["status"] = status_map.get(decision, adr.get("status", "PROPOSED"))
            adr["human_decision_id"] = signed_by
            adr["decision_rationale"] = rationale
            adr["updated_at"] = datetime.utcnow().isoformat()

            # Persist ADR update in both aggregate file and per-ADR file
            adrs = self.adr_repo.get_all()
            for idx, existing in enumerate(adrs):
                if existing.get("id") == proposal_id:
                    adrs[idx] = adr
                    break
            self.adr_repo._save_data(adrs)
            self._persist_adr_file(adr)

        logger.info(f"Decision registered for {proposal_id}: {decision}")
        return record
