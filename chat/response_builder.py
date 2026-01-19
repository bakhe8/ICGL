"""
ICGL Response Builder
=====================

Builds rich chat responses from ICGL engine results.
"""

from typing import Any, Dict, List, Optional
from .api_models import ChatMessage, ChatResponse, MessageBlock
from ..kb.schemas import ADR


class ResponseBuilder:
    """Converts ICGL results into chat messages with rich blocks."""
    
    def build_analysis_response(
        self, 
        analysis_result: Dict[str, Any],
        adr: Optional[ADR] = None
    ) -> ChatResponse:
        """
        Build response for analysis results.
        
        Args:
            analysis_result: Result from ICGL analysis
            adr: ADR object if available
            
        Returns:
            Chat response with structured blocks
        """
        blocks = []
        
        # Analysis block
        if "synthesis" in analysis_result:
            blocks.append(MessageBlock(
                type="analysis",
                title="🧠 Multi-Agent Analysis",
                data={
                    "synthesis": analysis_result["synthesis"],
                    "confidence": analysis_result.get("confidence", 0),
                    "agents": analysis_result.get("agent_results", [])
                },
                collapsed=True
            ))
        
        # Alerts block
        if analysis_result.get("sentinel_signals"):
            blocks.append(MessageBlock(
                type="alerts",
                title=f"⚠️ {len(analysis_result['sentinel_signals'])} Sentinel Alerts",
                data={"signals": analysis_result["sentinel_signals"]},
                collapsed=True
            ))
        
        # Actions block
        actions = []
        if analysis_result.get("requires_signature"):
            actions.append({
                "label": "✍️ Sign Decision",
                "action": "sign",
                "adr_id": adr.id if adr else None
            })
        
        if analysis_result.get("can_experiment"):
            actions.append({
                "label": "▶ Run Experiment",
                "action": "experiment"
            })
        
        if actions:
            blocks.append(MessageBlock(
                type="actions",
                title="Available Actions",
                data={"actions": actions},
                collapsed=False  # Show actions by default
            ))
        
        # Build main message
        confidence = analysis_result.get("confidence", 0)
        content = f"✅ Analysis complete with {confidence:.0%} confidence.\n\n"
        
        if analysis_result.get("synthesis"):
            content += analysis_result["synthesis"][:200] + "..."
        
        message = ChatMessage(
            role="system",
            content=content,
            blocks=blocks
        )
        
        return ChatResponse(
            messages=[message],
            state={
                "awaiting_sign": analysis_result.get("requires_signature", False),
                "adr_id": adr.id if adr else None
            },
            suggestions=[
                "Show full analysis",
                "What are the risks?",
                "Sign this decision"
            ]
        )
    
    def build_refactor_response(self, session_id: str, file_count: int) -> ChatResponse:
        """Build response for refactor completion."""
        message = ChatMessage(
            role="system",
            content=f"✅ Documentation refactor complete!\n\n"
                   f"Generated {file_count} files in session `{session_id}`.",
            blocks=[
                MessageBlock(
                    type="actions",
                    data={
                        "actions": [
                            {"label": "📋 Review Files", "action": "review", "session_id": session_id},
                            {"label": "✅ Approve", "action": "approve"},
                            {"label": "❌ Reject", "action": "reject"}
                        ]
                    },
                    collapsed=False
                )
            ]
        )
        
        return ChatResponse(
            messages=[message],
            state={"refactor_session": session_id},
            suggestions=["Show generated files", "Approve changes"]
        )
    
    def build_query_response(self, results: List[Any], query_type: str) -> ChatResponse:
        """Build response for query results."""
        content = f"Found {len(results)} {query_type}.\n\n"
        
        blocks = []
        for item in results[:5]:  # Show first 5
            if query_type == "adrs":
                blocks.append(MessageBlock(
                    type="adr",
                    title=f"📜 {item.title}",
                    data={
                        "id": item.id,
                        "status": item.status,
                        "decision": item.decision
                    },
                    collapsed=True
                ))
        
        message = ChatMessage(
            role="system",
            content=content,
            blocks=blocks
        )
        
        return ChatResponse(
            messages=[message],
            suggestions=["Show more details"]
        )
    
    def build_help_response(self, topic: Optional[str] = None) -> ChatResponse:
        """Build help response."""
        if topic == "analyze":
            content = """**How to Analyze Proposals**

You can ask me to analyze proposals in natural language:

Examples:
- "Analyze this proposal: migrate to TypeScript"
- "Review the decision to refactor code"
- "Evaluate switching to Rust"

I'll run multi-agent analysis and show you the results with governance checks.
"""
        elif topic == "refactor":
            content = """**How to Refactor Documentation**

You can request documentation improvements:

Examples:
- "Refactor the documentation"
- "Improve the docs"
- "Rewrite API documentation"

I'll generate improved docs and stage them for your review.
"""
        else:
            content = """**ICGL Sovereign Chat**

I can help you with:
- 🧠 **Analyze proposals** - Multi-agent governance analysis
- 📚 **Refactor docs** - AI-powered documentation improvement
- ⚠️ **Check risks** - Sentinel monitoring
- ✍️ **Sign decisions** - Human approval workflow
- 📜 **Query knowledge** - Search ADRs, policies

Try asking me anything in natural language!
"""
        
        message = ChatMessage(
            role="assistant",
            content=content
        )
        
        return ChatResponse(
            messages=[message],
            suggestions=[
                "Analyze a proposal",
                "Refactor docs",
                "Show recent decisions"
            ]
        )
    
    def build_error_response(self, error: str) -> ChatResponse:
        """Build error response."""
        message = ChatMessage(
            role="system",
            content=f"❌ Error: {error}\n\nPlease try again or ask for help."
        )
        
        return ChatResponse(
            messages=[message],
            suggestions=["Help", "Try again"]
        )
