"""
Conversation Intent Resolver
----------------------------

Hybrid intent resolution:
- Fast path: Simple commands (help, status) use pattern matching
- LLM path: Complex queries use IntentDecomposer
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, Union
import re

try:
    from .intent_decomposer import IntentDecomposer, DecomposedPlan
    DECOMPOSER_AVAILABLE = True
except ImportError:
    DECOMPOSER_AVAILABLE = False
    DecomposedPlan = None


@dataclass
class ResolvedIntent:
    """Represents a resolved intent and suggested action."""
    type: str
    params: Dict[str, str]


class IntentResolver:
    """
    Hybrid intent resolver with LLM fallback.
    
    Fast path: Pattern matching for simple commands
    LLM path: Decomposition for complex/ambiguous queries
    """
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm and DECOMPOSER_AVAILABLE
        self.decomposer = IntentDecomposer() if self.use_llm else None

    async def resolve_async(self, message: str) -> Union[ResolvedIntent, DecomposedPlan]:
        """
        Resolve intent using hybrid approach.
        
        Returns:
            ResolvedIntent for simple commands (fast path)
            DecomposedPlan for complex queries (LLM path)
        """
        msg = message.lower()

        # Explicit action tokens should bypass LLM
        if msg.strip() in ["approve_recommendations", "reject_recommendations"]:
            action = "APPROVE" if "approve" in msg else "REJECT"
            return ResolvedIntent(type="ack_recommendations", params={"action": action})

        # PRIORITY 1: Recommendation acknowledgement (non-ADR approval)
        if any(phrase in msg for phrase in [
            "approve recommendations", "reject recommendations",
            "approve recommendation", "reject recommendation",
            "accept recommendations", "decline recommendations",
            "وافق على التوصيات", "ارفض التوصيات", "قبول التوصيات", "رفض التوصيات"
        ]):
            action = "APPROVE" if any(k in msg for k in ["approve", "accept", "وافق", "قبول"]) else "REJECT"
            return ResolvedIntent(type="ack_recommendations", params={"action": action})

        # PRIORITY 2: Explicit user decisions (highest - always check first)
        if any(word in msg for word in ["approve", "reject", "sign", "consent"]):
            action = "submit_signature"
            decision = "APPROVE" if "approve" in msg else "REJECT" if "reject" in msg else "APPROVE"
            return ResolvedIntent(type=action, params={"action": decision, "rationale": message})

        # Prefer LLM decomposition when available for better intent understanding
        if self.use_llm and self.decomposer:
            try:
                plan = await self.decomposer.decompose(message)
                is_valid, error = self.decomposer.validate_plan(plan)
                if is_valid:
                    return plan
            except Exception:
                pass

        # PRIORITY 2: System commands (instant responses)
        if msg.strip() in ["status", "system status", "health", "metrics"]:
            return ResolvedIntent(type="view_status", params={})

        if any(phrase in msg for phrase in [
            "self diagnose", "self-diagnose", "diagnose", "diagnostics", "health check",
            "improve", "improvement", "improvements", "suggest improvements", "improve yourself",
            "تشخيص", "شخص", "تقييم", "تحسين", "تحسينات", "اقترح"
        ]):
            return ResolvedIntent(type="self_diagnose", params={})

        if any(cmd in msg for cmd in ["help", "commands", "menu", "what can you do", "usage"]):
            return ResolvedIntent(type="show_help", params={})

        # 3A: Unbinding commands (Prioritized to avoid 'bind' substring match)
        if any(word in msg for word in ["unbind", "unlink", "detach", "remove", "disconnect"]) and ("policy" in msg or "policies" in msg or "p-" in msg):
            codes = re.findall(r"(P-[A-Z]+-\d+)", message.upper())
            target_match = re.search(r"(ADR-[\w-]+)", message.upper())
            
            if codes:
                params = {"codes": ",".join(codes)}
                if target_match:
                    params["target_adr"] = target_match.group(1)
                return ResolvedIntent(type="unbind_policies", params=params)

        # 3B: Binding commands
        if any(word in msg for word in ["bind", "link", "attach", "conform", "connect"]) and ("policy" in msg or "policies" in msg or "p-" in msg):
            codes = re.findall(r"(P-[A-Z]+-\d+)", message.upper())
            target_match = re.search(r"(ADR-[\w-]+)", message.upper())
            
            if codes:
                params = {"codes": ",".join(codes)}
                if target_match:
                    params["target_adr"] = target_match.group(1)
                return ResolvedIntent(type="bind_policies", params=params)


        # PRIORITY 4: Analysis/Decision Proposals (Moved up)
        if any(word in msg for word in ["analyze", "review", "assess", "evaluate", "propose", "suggest"]) and not any(query_word in msg for query_word in ["what", "which", "show", "list", "how many", "count"]):
            return ResolvedIntent(type="run_analysis", params={"mode": "explore"})

        # PRIORITY 5: Memory and history
        if any(word in msg for word in ["similar", "memory", "history", "past", "previous", "recall", "decide", "decision", "context"]):
            return ResolvedIntent(type="fetch_memory", params={"query": message})

        # PRIORITY 5: Experiment mode
        if any(word in msg for word in ["experiment", "try", "test run"]):
            return ResolvedIntent(type="start_experiment", params={"mode": "experiment"})

        # No LLM available or it failed, treat as conversational
        return ResolvedIntent(type="conversational", params={"message": message})

    def resolve(self, message: str) -> Union[ResolvedIntent, DecomposedPlan]:
        """
        Synchronous wrapper for resolve_async.
        
        - Preferred in synchronous callers (tests/GBE harness).
        - In async contexts, use `await resolve_async(...)` to avoid
          creating nested event loops.
        """
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # Execute in running loop and wait for result
                return asyncio.run_coroutine_threadsafe(
                    self.resolve_async(message), loop
                ).result()
        except RuntimeError:
            # No running loop; fall back to fresh loop below
            pass

        return asyncio.run(self.resolve_async(message))


