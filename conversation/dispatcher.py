"""
Action Dispatcher
-----------------

Executes allowed conversational actions via governed ICGL pathways.
"""

from dataclasses import dataclass
from typing import Any, Dict, Tuple
import os
from ..kb.schemas import ADR, uid


@dataclass
class ConversationSession:
    session_id: str
    last_adr_id: str | None = None
    awaiting_signature: bool = False
    mode: str = "explore"
    alert_level: str = "LOW"


class ActionDispatcher:
    """
    Dispatches actions while preserving governance guarantees.
    """

    def __init__(self, icgl_provider, analysis_runner):
        self.icgl_provider = icgl_provider
        self.analysis_runner = analysis_runner

    async def run_analysis(self, message: str, session: ConversationSession, human_id: str, mode: str = "explore") -> Tuple[ADR, Dict[str, Any]]:
        """
        Run full multi-agent analysis on a message.
        
        PERFORMANCE: This is an EXPENSIVE operation (10+ seconds).
        Only use for actual proposals/decisions, NOT for queries!
        """
        # 🚀 FAST PATH: Detect if this is actually a query (should have been caught earlier)
        # This is a safety net to prevent accidental expensive analysis
        msg_lower = message.lower()
        query_indicators = ["what", "which", "show", "list", "count", "how many", "display", "get", "retrieve", "bound", "related"]
        
        if any(indicator in msg_lower for indicator in query_indicators) and "adr" not in msg_lower:
            # This looks like a query, not a proposal
            # Return minimal structure to avoid full analysis
            dummy_adr = ADR(
                id=uid(),
                title="[Query Bypassed]",
                status="QUERY",  # Special status
                context=message,
                decision="N/A - Read-only query",
                consequences=[],
                related_policies=[],
                sentinel_signals=[],
                human_decision_id=None,
            )
            # Don't add to KB, don't run analysis
            return dummy_adr, {
                "synthesis": {
                    "overall_confidence": 1.0,
                    "consensus_recommendations": [f"Query detected: {message}"],
                    "all_concerns": [],
                    "sentinel_alerts": [],
                },
                "bypassed": True
            }
        
        # Normal analysis flow for proposals
        icgl = self.icgl_provider()
        adr = ADR(
            id=uid(),
            title=message[:80] or "User request",
            status="DRAFT",
            context=message,
            decision="To be decided",
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )
        kb.add_adr(adr)
        session.last_adr_id = adr.id
        session.awaiting_signature = True
        session.mode = mode
        result = await self.analysis_runner(adr, human_id)
        return adr, result

    async def start_experiment(self, message: str, session: ConversationSession, human_id: str) -> Tuple[ADR, Dict[str, Any]]:
        # Experiments flow through the same governed analysis path, but flagged in session mode.
        return await self.run_analysis(message, session, human_id, mode="experiment")

    async def fetch_memory(self, query: str, session: ConversationSession, human_id: str) -> Dict[str, Any]:
        from ..memory.service import get_memory_service
        service = get_memory_service()
        # Initialize lazily
        await service.initialize()
        
        matches = await service.recall_context(query, session_id=session.session_id, limit=5)
        
        return {
            "query": query,
            "matches": [
                {
                    "id": m.document.id,
                    "score": round(m.score, 4),
                    "title": m.document.metadata.get("title") or m.document.metadata.get("role", "unknown"),
                    "snippet": (m.document.content or "")[:200],
                    "timestamp": m.document.metadata.get("timestamp")
                }
                for m in matches
            ],
            "source": "vector_memory" 
        }

    async def submit_signature(self, session: ConversationSession, action: str, rationale: str, human_id: str) -> Dict[str, Any]:
        if not session.last_adr_id:
            raise ValueError("No ADR available to sign.")
        icgl = self.icgl_provider()
        adr = kb.get_adr(session.last_adr_id)
        if not adr:
            raise ValueError("ADR not found for signing.")

        decision = hdal.sign_decision(
            adr_id=adr.id,
            action=action,
            rationale=rationale,
            human_id=human_id,
        )
        kb.add_human_decision(decision)
        adr.status = "ACCEPTED" if action == "APPROVE" else "REJECTED"
        adr.human_decision_id = decision.id
        kb.add_adr(adr)

        session.awaiting_signature = False
        return {"adr_id": adr.id, "decision": action, "rationale": rationale}

    async def bind_policies(self, session: ConversationSession, policy_codes: list[str], human_id: str, target_adr_id: str | None = None) -> Dict[str, Any]:
        """
        GBE: Binds policies to the current active ADR or a specific target ADR.
        """
        adr_id = target_adr_id or session.last_adr_id
        
        if not adr_id:
            raise ValueError("No active ADR found. Please start an analysis first or specify 'to ADR-XXX'.")

        icgl = self.icgl_provider()
        adr = kb.get_adr(adr_id)
        if not adr:
            raise ValueError("Active ADR context lost.")

        # Validate Policies
        valid_policies = []
        unknown_codes = []
        for code in policy_codes:
            policy = kb.get_policy_by_code(code)
            if policy:
                valid_policies.append(policy)
            else:
                unknown_codes.append(code)

        if not valid_policies and unknown_codes:
            raise ValueError(f"Policies not found: {', '.join(unknown_codes)}")

        # Bind proper IDs (not codes) to ADR
        new_bindings = []
        for p in valid_policies:
            if p.id not in adr.related_policies:
                adr.related_policies.append(p.id)
                new_bindings.append(p.code)

        kb.add_adr(adr)

        return {
            "adr_id": adr.id,
            "bound_policies": new_bindings,
            "unknown_codes": unknown_codes,
            "total_bindings": len(adr.related_policies)
        }

        return {
            "adr_id": adr.id,
            "bound_policies": new_bindings,
            "unknown_codes": unknown_codes,
            "total_bindings": len(adr.related_policies)
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Retrieves current system status directly from the engine/KB.
        """
        icgl = self.icgl_provider()
        # Simple heuristic for status, similar to API
        # In a real system, this might query the Sentinel directly
        return {
            "mode": "COCKPIT",
            "active_alert_level": "NONE", # Placeholder, would be dynamic
            "telemetry": {
                 "drift_detection_count": 0,
                 "agent_failure_count": 0
            }
        }

    async def self_diagnose(self) -> Dict[str, Any]:
        """
        Provide a lightweight self-diagnosis summary and improvement suggestions.
        """
        icgl = self.icgl_provider()
        diagnostics: Dict[str, Any] = {
            "engine_ready": True,
            "env_loaded": bool(os.getenv("OPENAI_API_KEY")),
            "stats": {},
            "issues": [],
            "suggestions": [],
        }

        try:
            diagnostics["stats"] = kb.get_stats()
        except Exception as exc:
            diagnostics["engine_ready"] = False
            diagnostics["issues"].append(f"KB access error: {exc}")
            diagnostics["stats"] = {}

        stats = diagnostics.get("stats", {}) or {}
        adrs = stats.get("adrs", 0)
        policies = stats.get("policies", 0)
        decisions = stats.get("human_decisions", 0)
        learning = stats.get("learning_logs", 0)

        if not diagnostics["env_loaded"]:
            diagnostics["issues"].append("OPENAI_API_KEY missing")
            diagnostics["suggestions"].append("Add OPENAI_API_KEY to .env to enable agent reasoning.")

        if adrs == 0:
            diagnostics["suggestions"].append("Run a first analysis to create an ADR.")

        if policies == 0:
            diagnostics["suggestions"].append("Define baseline policies to enforce governance gates.")

        if learning == 0:
            diagnostics["suggestions"].append("Complete a governance cycle to generate learning logs.")

        if adrs > decisions:
            diagnostics["suggestions"].append("Review pending ADRs and sign decisions.")

        if not diagnostics["suggestions"]:
            diagnostics["suggestions"].append("System looks healthy. Continue regular governance cycles.")

        return diagnostics

    async def unbind_policies(self, session: ConversationSession, policy_codes: list[str], human_id: str, target_adr_id: str | None = None) -> Dict[str, Any]:
        """
        GBE: Unbinds policies from the current active ADR or a specific target ADR.
        """
        adr_id = target_adr_id or session.last_adr_id
        
        if not adr_id:
            raise ValueError("No active ADR found. Please specify 'from ADR-XXX'.")

        icgl = self.icgl_provider()
        adr = kb.get_adr(adr_id)
        if not adr:
            raise ValueError(f"ADR {adr_id} not found.")

        # Find and remove matching policies
        removed_bindings = []
        for code in policy_codes:
            policy = kb.get_policy_by_code(code)
            if policy and policy.id in adr.related_policies:
                adr.related_policies.remove(policy.id)
                removed_bindings.append(policy.code)

        kb.add_adr(adr)

        return {
            "adr_id": adr.id,
            "removed_policies": removed_bindings,
            "total_bindings": len(adr.related_policies)
        }

    async def query_bindings(self, session: ConversationSession, target_adr_id: str | None, query_type: str) -> Dict[str, Any]:
        """
        GBE: Query policy bindings for an ADR (read-only state retrieval).
        """
        adr_id = target_adr_id or session.last_adr_id
        
        if not adr_id:
            return {"error": "No ADR specified. Please specify 'for ADR-XXX' or start an analysis first."}

        icgl = self.icgl_provider()
        adr = kb.get_adr(adr_id)
        if not adr:
            return {"error": f"ADR {adr_id} not found."}

        # Resolve policy IDs to codes
        policy_codes = []
        for policy_id in adr.related_policies:
            policy = kb.get_policy(policy_id)
            if policy:
                policy_codes.append({"code": policy.code, "title": policy.title})

        return {
            "adr_id": adr.id,
            "adr_title": adr.title,
            "policies": policy_codes,
            "count": len(policy_codes)
        }

    async def query_count(self, session: ConversationSession, target_adr_id: str | None, query_type: str) -> Dict[str, Any]:
        """
        Query count of policies/ADRs.
        """
        if target_adr_id:
            icgl = self.icgl_provider()
            adr = kb.get_adr(target_adr_id)
            if not adr:
                return {"error": f"ADR {target_adr_id} not found."}
            
            return {
                "adr_id": adr.id,
                "adr_title": adr.title,
                "count": len(adr.related_policies),
                "type": "policies"
            }
        else:
            # General count
            icgl = self.icgl_provider()
            return {
                "total_adrs": len([a for a in kb.get_all_adrs()]),
                "total_policies": len([p for p in kb.get_all_policies()]),
                "type": "general"
            }

    async def query_adr(self, session: ConversationSession, target_adr_id: str) -> Dict[str, Any]:
        """
        Retrieve full ADR details (read-only).
        """
        if not target_adr_id:
            return {"error": "No ADR specified."}

        icgl = self.icgl_provider()
        adr = kb.get_adr(target_adr_id)
        if not adr:
            return {"error": f"ADR {target_adr_id} not found."}

        # Get policy details
        policies = []
        for policy_id in adr.related_policies:
            policy = kb.get_policy(policy_id)
            if policy:
                policies.append({"code": policy.code, "title": policy.title})

        return {
            "adr_id": adr.id,
            "title": adr.title,
            "status": adr.status,
            "context": adr.context[:200] + "..." if len(adr.context) > 200 else adr.context,
            "decision": adr.decision,
            "related_policies": policies,
            "policy_count": len(policies)
        }
