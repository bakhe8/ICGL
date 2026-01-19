"""
Response Composer
-----------------

Creates human-friendly chat responses with structured blocks.
"""

from typing import Any, Dict, List, Optional
from chat.api_models import ChatMessage, ChatResponse, MessageBlock
from kb.schemas import ADR


class ResponseComposer:
    def _alert_level(self, alerts: List[Dict[str, Any]]) -> str:
        severities = [a.get("severity", "").upper() for a in alerts]
        if any(s in {"CRITICAL", "HIGH"} for s in severities):
            return "HIGH" if "HIGH" in severities else "CRITICAL"
        if severities:
            return "LOW"
        return "NONE"

    def analysis_response(self, adr: ADR, analysis: Dict[str, Any], state: Dict[str, Any]) -> ChatResponse:
        synthesis = analysis.get("synthesis") or {}
        alerts = synthesis.get("sentinel_alerts") or analysis.get("sentinel_signals") or []
        confidence = synthesis.get("overall_confidence", 0.0)
        actions = [
            {"label": "✍️ Approve", "action": "submit_signature", "value": "APPROVE"},
            {"label": "🛑 Reject", "action": "submit_signature", "value": "REJECT"},
        ] if state.get("waiting_for_human") else []

        blocks = [
            MessageBlock(
                type="analysis",
                title="🧠 Multi-Agent Analysis",
                data={
                    "confidence": confidence,
                    "consensus": synthesis.get("consensus_recommendations", []),
                    "concerns": synthesis.get("all_concerns", []),
                },
                collapsed=False,
            )
        ]

        if alerts:
            blocks.append(
                MessageBlock(
                    type="alerts",
                    title=f"⚠️ Sentinel Alerts ({len(alerts)})",
                    data={"alerts": alerts},
                    collapsed=True,
                )
            )

        if actions:
            blocks.append(
                MessageBlock(
                    type="actions",
                    title="Next steps",
                    data={"actions": actions},
                    collapsed=False,
                )
            )

        message_text = (
            f"Analysis ready for '{adr.title}'. "
            f"Confidence {confidence:.0%}. "
            + ("Awaiting your decision." if state.get("waiting_for_human") else "No signature needed.")
        )

        msg = ChatMessage(role="assistant", content=message_text, text=message_text, blocks=blocks)
        return ChatResponse(
            messages=[msg],
            state={
                "waiting_for_human": state.get("waiting_for_human", False),
                "alert_level": self._alert_level(alerts),
                "mode": state.get("mode", "explore"),
                "adr_id": adr.id,
            },
            suggestions=[
                "Show similar decisions",
                "Approve",
                "Reject",
            ],
        )

    def memory_response(self, payload: Dict[str, Any], state: Dict[str, Any]) -> ChatResponse:
        matches = payload.get("matches", [])
        blocks = [
            MessageBlock(
                type="memory",
                title="📜 Similar Decisions",
                data={"matches": matches},
                collapsed=False,
            )
        ]
        text = f"Found {len(matches)} related memories for your query."
        return ChatResponse(
            messages=[ChatMessage(role="assistant", content=text, text=text, blocks=blocks)],
            state=state,
            suggestions=["Run analysis", "Ask another question"],
        )

    def signature_prompt(self, adr_id: str, state: Dict[str, Any]) -> ChatResponse:
        text = f"Ready to sign ADR {adr_id}. Approve or Reject?"
        blocks = [
            MessageBlock(
                type="actions",
                title="Signature required",
                data={
                    "actions": [
                        {"label": "✍️ Approve", "action": "submit_signature", "value": "APPROVE"},
                        {"label": "🛑 Reject", "action": "submit_signature", "value": "REJECT"},
                    ]
                },
                collapsed=False,
            )
        ]
        return ChatResponse(
            messages=[ChatMessage(role="assistant", content=text, text=text, blocks=blocks)],
            state=state | {"waiting_for_human": True},
            suggestions=["Approve", "Reject", "Show risks"],
        )

    def signature_receipt(self, result: Dict[str, Any], state: Dict[str, Any]) -> ChatResponse:
        text = f"Decision recorded for ADR {result['adr_id']}: {result['decision']}."
        return ChatResponse(
            messages=[ChatMessage(role="assistant", content=text, text=text)],
            state=state | {"waiting_for_human": False},
            suggestions=["Start new analysis", "Show similar decisions"],
        )

    def binding_receipt(self, result: Dict[str, Any], state: Dict[str, Any]) -> ChatResponse:
        bound = result.get("bound_policies", [])
        unknown = result.get("unknown_codes", [])
        total = result.get("total_bindings", 0)

        msg_parts = []
        if bound:
            msg_parts.append(f"✅ Bound policies: {', '.join(bound)}.")
        if unknown:
            msg_parts.append(f"⚠️ Unknown policies: {', '.join(unknown)}.")

        msg_parts.append(f"ADR now has {total} related policies.")

        text = " ".join(msg_parts)

        return ChatResponse(
            messages=[ChatMessage(role="assistant", content=text, text=text)],
            state=state,
            suggestions=["Approve", "Show risks"],
        )

    def status_response(self, status: Dict[str, Any], state: Dict[str, Any]) -> ChatResponse:
        active_alert = status.get("active_alert_level", "NONE")
        emoji = "🟢" if active_alert == "NONE" else "🔴" if active_alert == "CRITICAL" else "🟡"
        
        text = f"{emoji} System Status: {active_alert}"
        
        telemetry = status.get("telemetry", {})
        blocks = [
            MessageBlock(
                type="metrics",
                title="System Telemetry",
                data={
                    "drift_count": telemetry.get("drift_detection_count", 0),
                    "active_failures": telemetry.get("agent_failure_count", 0),
                    "last_latency": telemetry.get("last_latency_ms", 0),
                    "alert_level": active_alert
                },
                collapsed=False
            )
        ]
        
        return ChatResponse(
            messages=[ChatMessage(role="assistant", content=text, text=text, blocks=blocks)],
            state=state,
            suggestions=["Run analysis", "Show help"]
        )

    def self_diagnose_response(self, diagnostics: Dict[str, Any], state: Dict[str, Any]) -> ChatResponse:
        stats = diagnostics.get("stats", {}) or {}
        suggestions = diagnostics.get("suggestions", []) or []
        issues = diagnostics.get("issues", []) or []

        status_text = "🟢 Self-diagnosis complete." if diagnostics.get("engine_ready", True) else "🔴 Self-diagnosis degraded."

        blocks = [
            MessageBlock(
                type="metrics",
                title="System Snapshot",
                data={
                    "adrs": stats.get("adrs", 0),
                    "policies": stats.get("policies", 0),
                    "human_decisions": stats.get("human_decisions", 0),
                    "learning_logs": stats.get("learning_logs", 0),
                    "env_loaded": diagnostics.get("env_loaded", False),
                },
                collapsed=False,
            ),
            MessageBlock(
                type="text",
                title="Recommendations",
                data={"content": "\n".join([f"- {item}" for item in suggestions])},
                collapsed=False,
            ),
            MessageBlock(
                type="actions",
                title="Decision",
                data={
                    "actions": [
                        {"label": "✅ Approve recommendations", "action": "ack_recommendations", "value": "APPROVE_RECOMMENDATIONS"},
                        {"label": "🛑 Reject recommendations", "action": "ack_recommendations", "value": "REJECT_RECOMMENDATIONS"},
                    ]
                },
                collapsed=False,
            ),
        ]

        if issues:
            blocks.insert(
                1,
                MessageBlock(
                    type="alerts",
                    title="Detected Issues",
                    data={"alerts": issues},
                    collapsed=False,
                ),
            )

        return ChatResponse(
            messages=[ChatMessage(role="assistant", content=status_text, text=status_text, blocks=blocks)],
            state=state,
            suggestions=["System Status", "Run analysis", "Help"],
        )

    def recommendations_receipt(self, action: str, state: Dict[str, Any]) -> ChatResponse:
        if action == "APPROVE":
            text = "✅ Recommendations approved."
        else:
            text = "🛑 Recommendations rejected."
        return ChatResponse(
            messages=[ChatMessage(role="assistant", content=text, text=text)],
            state=state,
            suggestions=["System Status", "Run analysis", "Help"],
        )

    def help_response(self, state: Dict[str, Any]) -> ChatResponse:
        text = "I am the ICGL Governance Agent. Here is what I can do:"
        blocks = [
            MessageBlock(
                type="text",
                title="Available Commands",
                data={
                    "content": """
- **Analyze**: "Analyze decision to migrate to Cloud"
- **Status**: "System Status"
- **Self Diagnose**: "Diagnose system" / "تشخيص النظام"
- **Bind Policy**: "Bind policy P-CORE-01 to ADR-123"
- **Sign**: "Approve ADR-123"
                    """
                },
                collapsed=False
            )
        ]
        return ChatResponse(
            messages=[ChatMessage(role="assistant", content=text, text=text, blocks=blocks)],
            state=state,
            suggestions=["System Status", "Run analysis"]
        )

    def query_response(self, result: Dict[str, Any], state: Dict[str, Any]) -> ChatResponse:
        """
        Compose response for query intents (read-only state retrieval).
        """
        if "error" in result:
            return self.error(result["error"], state)

        # Handle different query types
        if "policies" in result:
            # Policy binding query
            policies = result.get("policies", [])
            adr_id = result.get("adr_id", "Unknown")
            adr_title = result.get("adr_title", "")
            count = result.get("count", 0)

            if policies:
                policy_list = "\n".join([f"  • {p['code']}: {p['title']}" for p in policies])
                text = f"📋 **{adr_id}** has {count} bound policies:\n{policy_list}"
            else:
                text = f"📋 **{adr_id}** has no bound policies yet."

            blocks = [
                MessageBlock(
                    type="data",
                    title=f"Policy Bindings for {adr_id}",
                    data={"adr_title": adr_title, "policies": policies, "count": count},
                    collapsed=False
                )
            ]

        elif "adr_id" in result and "title" in result:
            # Full ADR query
            text = f"📄 **{result['adr_id']}**: {result['title']}\n\nStatus: {result['status']}\nBound Policies: {result['policy_count']}"
            blocks = [
                MessageBlock(
                    type="adr_details",
                    title="ADR Details",
                    data=result,
                    collapsed=False
                )
            ]

        elif "type" in result and result["type"] == "policies":
            # Count query
            text = f"📊 **{result['adr_id']}** has **{result['count']}** bound policies."
            blocks = []

        elif "type" in result and result["type"] == "general":
            # General system count
            text = f"📊 System totals:\n  • ADRs: {result.get('total_adrs', 0)}\n  • Policies: {result.get('total_policies', 0)}"
            blocks = []

        else:
            text = "Query completed."
            blocks = []

        return ChatResponse(
            messages=[ChatMessage(role="assistant", content=text, text=text, blocks=blocks)],
            state=state,
            suggestions=["Run analysis", "Bind policy", "Show help"]
        )

    def conversational_response(self, message: str, state: Dict[str, Any]) -> ChatResponse:
        """
        Handle conversational queries that don't fit other categories.
        """
        text = (
            "I'm here to help with governance decisions. "
            "I can analyze proposals, bind policies, or retrieve information. "
            "Try:\n"
            "  • 'Analyze <your decision>'\n"
            "  • 'What policies are bound to ADR-001?'\n"
            "  • 'Bind policy P-CORE-01 to ADR-001'\n"
            "  • 'Help'"
        )

        return ChatResponse(
            messages=[ChatMessage(role="assistant", content=text, text=text)],
            state=state,
            suggestions=["Help", "System Status", "Show recent decisions"]
        )

    def error(self, error: str, state: Optional[Dict[str, Any]] = None) -> ChatResponse:
        text = f"❌ {error}"
        return ChatResponse(
            messages=[ChatMessage(role="system", content=text, text=text)],
            state=state or {},
            suggestions=["Help", "Try again"],
        )
