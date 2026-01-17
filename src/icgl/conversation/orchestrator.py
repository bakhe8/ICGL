"""
Conversation Orchestrator
-------------------------

Routes chat requests through intent resolution, governed actions, and response composition.
"""

from typing import Dict
from .intent_resolver import IntentResolver, ResolvedIntent
from .dispatcher import ActionDispatcher, ConversationSession
from .composer import ResponseComposer
from ..chat.schemas import ChatRequest, ChatResponse

try:
    from .intent_decomposer import DecomposedPlan, IntentStep
    DECOMPOSER_AVAILABLE = True
except ImportError:
    DECOMPOSER_AVAILABLE = False
    DecomposedPlan = None
    IntentStep = None


class ConversationOrchestrator:
    def __init__(self, icgl_provider, analysis_runner):
        self.sessions: Dict[str, ConversationSession] = {}
        self.intent_resolver = IntentResolver()
        self.dispatcher = ActionDispatcher(icgl_provider, analysis_runner)
        self.composer = ResponseComposer()

    def _get_session(self, session_id: str) -> ConversationSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationSession(session_id=session_id)
        return self.sessions[session_id]

    async def handle(self, request: ChatRequest) -> ChatResponse:
        session = self._get_session(request.session_id)
        try:
            normalized = request.message.strip().lower()
            if normalized in {"approve_recommendations", "reject_recommendations"}:
                action = "APPROVE" if "approve" in normalized else "REJECT"
                resp = self.composer.recommendations_receipt(action, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if "recommendation" in normalized and any(word in normalized for word in ["approve", "reject", "accept", "decline", "وافق", "ارفض", "قبول", "رفض"]):
                action = "APPROVE" if any(word in normalized for word in ["approve", "accept", "وافق", "قبول"]) else "REJECT"
                resp = self.composer.recommendations_receipt(action, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            intent_or_plan = await self.intent_resolver.resolve_async(request.message)
            
            # Check if it's a DecomposedPlan (multi-step)
            if DECOMPOSER_AVAILABLE and isinstance(intent_or_plan, DecomposedPlan):
                return await self._handle_decomposed_plan(intent_or_plan, request, session)
            
            # Single intent (fast path)
            intent = intent_or_plan

            if intent.type == "fetch_memory":
                payload = await self.dispatcher.fetch_memory(intent.params["query"], session, request.context.human_id)
                resp = self.composer.memory_response(payload, {"mode": session.mode, "waiting_for_human": session.awaiting_signature})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "start_experiment":
                adr, result = await self.dispatcher.start_experiment(request.message, session, request.context.human_id)
                resp = self.composer.analysis_response(adr, result, {"waiting_for_human": True, "mode": "experiment"})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "run_analysis":
                adr, result = await self.dispatcher.run_analysis(request.message, session, request.context.human_id, mode=intent.params.get("mode", "explore"))
                resp = self.composer.analysis_response(adr, result, {"waiting_for_human": True, "mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "submit_signature":
                outcome = await self.dispatcher.submit_signature(session, intent.params["action"], intent.params.get("rationale", request.message), request.context.human_id)
                resp = self.composer.signature_receipt(outcome, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "bind_policies":
                outcome = await self.dispatcher.bind_policies(
                    session,
                    intent.params["codes"].split(","),
                    request.context.human_id,
                    target_adr_id=intent.params.get("target_adr")
                )
                resp = self.composer.binding_receipt(outcome, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "view_status":
                status_data = await self.dispatcher.get_system_status()
                resp = self.composer.status_response(status_data, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "self_diagnose":
                diagnostics = await self.dispatcher.self_diagnose()
                resp = self.composer.self_diagnose_response(diagnostics, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "ack_recommendations":
                action = intent.params.get("action", "REJECT")
                # If APPROVE and last message was self-diagnose with actionable recommendations, auto-execute
                if action == "APPROVE" and hasattr(session, "_last_self_diagnose") and session._last_self_diagnose:
                    # Run first analysis and governance cycle
                    adr, result = await self.dispatcher.run_analysis(
                        "Initial system bootstrap analysis", session, request.context.human_id, mode="explore"
                    )
                    # Run governance cycle
                    icgl = self.dispatcher.icgl_provider()
                    await icgl.run_governance_cycle(adr, request.context.human_id)
                    # Compose response with results
                    resp = self.composer.analysis_response(adr, result, {"mode": session.mode, "auto_executed": True})
                    resp.state["session_id"] = request.session_id
                    # Clear flag
                    session._last_self_diagnose = False
                    return resp
                resp = self.composer.recommendations_receipt(action, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "show_help":
                resp = self.composer.help_response({"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "unbind_policies":
                outcome = await self.dispatcher.unbind_policies(
                    session,
                    intent.params["codes"].split(","),
                    request.context.human_id,
                    target_adr_id=intent.params.get("target_adr")
                )
                resp = self.composer.binding_receipt(outcome, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "query_binding_state":
                query_result = await self.dispatcher.query_bindings(
                    session,
                    intent.params.get("target"),
                    intent.params.get("query_type")
                )
                resp = self.composer.query_response(query_result, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "query_count":
                count_result = await self.dispatcher.query_count(
                    session,
                    intent.params.get("target"),
                    intent.params.get("query_type")
                )
                resp = self.composer.query_response(count_result, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "query_adr":
                adr_result = await self.dispatcher.query_adr(
                    session,
                    intent.params.get("target")
                )
                resp = self.composer.query_response(adr_result, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            if intent.type == "conversational":
                # Conversational query - provide helpful response without creating ADR
                resp = self.composer.conversational_response(intent.params.get("message", ""), {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            # Fallback: prompt for signature if available
            if session.awaiting_signature and session.last_adr_id:
                resp = self.composer.signature_prompt(session.last_adr_id, {"mode": session.mode})
                resp.state["session_id"] = request.session_id
                return resp

            resp = self.composer.error("Unrecognized intent.", {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        except Exception as e:
            resp = self.composer.error(str(e), {"mode": session.mode, "waiting_for_human": session.awaiting_signature})
            resp.state["session_id"] = request.session_id
            return resp

    async def _handle_decomposed_plan(self, plan: DecomposedPlan, request: ChatRequest, session: ConversationSession) -> ChatResponse:
        """
        Execute a multi-step decomposed plan from the LLM.
        """
        # Check for clarification needed
        if plan.requires_clarification:
            text = plan.clarification_question or "I need more information. Can you clarify your request?"
            resp = self.composer.conversational_response(text, {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp
        
        # Execute intents in suggested sequence
        results = []
        sequence = plan.suggested_sequence or list(range(len(plan.intents)))
        
        for idx in sequence:
            if idx >= len(plan.intents):
                continue
                
            intent_step = plan.intents[idx]
            
            # Convert IntentStep to ResolvedIntent for existing handlers
            resolved = ResolvedIntent(type=intent_step.type, params=intent_step.params)
            
            # Execute the intent using existing handlers
            result = await self._execute_single_intent(resolved, request, session)
            results.append({"intent": intent_step.type, "result": result})
        
        # Return composite response
        # For now, return the last result (can be enhanced to show all steps)
        if results:
            return results[-1]["result"]
        else:
            return self.composer.error("No intents to execute", {"mode": session.mode})
    
    async def _execute_single_intent(self, intent: ResolvedIntent, request: ChatRequest, session: ConversationSession) -> ChatResponse:
        """
        Execute a single intent (extracted from handle method for reuse).
        """
        if intent.type == "fetch_memory":
            payload = await self.dispatcher.fetch_memory(intent.params["query"], session, request.context.human_id)
            resp = self.composer.memory_response(payload, {"mode": session.mode, "waiting_for_human": session.awaiting_signature})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "start_experiment":
            adr, result = await self.dispatcher.start_experiment(request.message, session, request.context.human_id)
            resp = self.composer.analysis_response(adr, result, {"waiting_for_human": True, "mode": "experiment"})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "run_analysis":
            adr, result = await self.dispatcher.run_analysis(request.message, session, request.context.human_id, mode=intent.params.get("mode", "explore"))
            resp = self.composer.analysis_response(adr, result, {"waiting_for_human": True, "mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "submit_signature":
            outcome = await self.dispatcher.submit_signature(session, intent.params["action"], intent.params.get("rationale", ""), request.context.human_id)
            resp = self.composer.signature_receipt(outcome, {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "bind_policies":
            outcome = await self.dispatcher.bind_policies(
                session,
                intent.params["codes"].split(","),
                request.context.human_id,
                target_adr_id=intent.params.get("target_adr")
            )
            resp = self.composer.binding_receipt(outcome, {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "view_status":
            status_data = await self.dispatcher.get_system_status()
            resp = self.composer.status_response(status_data, {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

            if intent.type == "self_diagnose":
                import logging
                logger = logging.getLogger("icgl.orchestrator")
                logger.info(f"[self_diagnose] Triggered by: {request.message}")
                try:
                    diagnostics = await self.dispatcher.self_diagnose()
                    logger.info(f"[self_diagnose] Diagnostics: {diagnostics}")
                    # If recommendations include analysis/governance, set flag for auto-execute
                    recs = diagnostics.get("suggestions", [])
                    if any("analysis" in r or "governance" in r for r in recs):
                        session._last_self_diagnose = True
                    else:
                        session._last_self_diagnose = False
                    resp = self.composer.self_diagnose_response(diagnostics, {"mode": session.mode})
                    resp.state["session_id"] = request.session_id
                    return resp
                except Exception as e:
                    logger.error(f"[self_diagnose] Exception: {e}", exc_info=True)
                    resp = self.composer.error(f"Self-diagnose failed: {e}", {"mode": session.mode})
                    resp.state["session_id"] = request.session_id
                    return resp

        if intent.type == "ack_recommendations":
            action = intent.params.get("action", "REJECT")
            resp = self.composer.recommendations_receipt(action, {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "show_help":
            resp = self.composer.help_response({"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "unbind_policies":
            outcome = await self.dispatcher.unbind_policies(
                session,
                intent.params["codes"].split(","),
                request.context.human_id,
                target_adr_id=intent.params.get("target_adr")
            )
            resp = self.composer.binding_receipt(outcome, {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "query_binding_state":
            query_result = await self.dispatcher.query_bindings(
                session,
                intent.params.get("target"),
                intent.params.get("query_type")
            )
            resp = self.composer.query_response(query_result, {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "query_count":
            count_result = await self.dispatcher.query_count(
                session,
                intent.params.get("target"),
                intent.params.get("query_type")
            )
            resp = self.composer.query_response(count_result, {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "query_adr":
            adr_result = await self.dispatcher.query_adr(
                session,
                intent.params.get("target")
            )
            resp = self.composer.query_response(adr_result, {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        if intent.type == "conversational":
            resp = self.composer.conversational_response(intent.params.get("message", ""), {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        # Fallback: prompt for signature if available
        if session.awaiting_signature and session.last_adr_id:
            resp = self.composer.signature_prompt(session.last_adr_id, {"mode": session.mode})
            resp.state["session_id"] = request.session_id
            return resp

        resp = self.composer.error("Unrecognized intent.", {"mode": session.mode})
        resp.state["session_id"] = request.session_id
        return resp
