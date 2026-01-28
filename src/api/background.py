import time
from dataclasses import asdict
from typing import Any, List

from src.api.deps import get_icgl
from src.core.kb.schemas import ADR, now, uid
from src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

# Note: active_synthesis and managers are accessed via injection or the root server context
# To keep it simple, we use a global registry for background tasks if needed,
# but here we'll assume the caller provides the necessary stateful objects.


async def run_analysis_task(adr: ADR, human_id: str, icgl: Any, manager: Any, scp_manager: Any) -> None:
    """Background task to run full ICGL analysis on an ADR."""
    from src.api.server import get_status  # Circular import handled by local import

    start_time = time.time()
    logger.info(f"🌀 Starting Background Analysis for {adr.id}")
    try:
        from src.core.agents.core.base import Problem

        # Policy gate check (pre-analysis)
        policy_report = icgl.enforcer.check_adr_compliance(adr)
        if policy_report.status == "FAIL":
            icgl.kb.save_synthesis_state(adr.id, {"status": "blocked", "policy_report": policy_report.__dict__})
            return

        # 1. Semantic Search (Historical Echo / S-11)
        query = f"{adr.title} {adr.context} {adr.decision}"
        matches = await icgl.memory.search(query, limit=4)
        semantic = []
        for m in matches:
            if m.document.id != adr.id:
                semantic.append(
                    {
                        "id": m.document.id,
                        "title": m.document.metadata.get("title", "Unknown"),
                        "score": round(m.score * 100, 1),
                    }
                )

        # 2. Sentinel Detailed Scan
        alerts = await icgl.sentinel.scan_adr_detailed_async(adr, icgl.kb)

        # 3. Agent Synthesis
        problem = Problem(title=adr.title, context=adr.context, metadata={"decision": adr.decision})
        synthesis = await icgl.registry.run_and_synthesize(problem, icgl.kb)

        icgl.kb.save_synthesis_state(
            adr.id,
            {
                "adr": asdict(adr),
                "synthesis": {
                    "overall_confidence": synthesis.overall_confidence,
                    "consensus_recommendations": synthesis.consensus_recommendations,
                    "all_concerns": synthesis.all_concerns,
                    "agent_results": [asdict(r) for r in synthesis.individual_results],
                    "semantic_matches": semantic[:3],
                    "sentinel_alerts": [
                        {
                            "id": a.rule_id,
                            "severity": a.severity.value,
                            "message": a.message,
                            "category": a.category.value,
                        }
                        for a in alerts
                    ],
                    "mindmap": generate_consensus_mindmap(adr.title, synthesis),
                    "mediation": None,
                    "policy_report": policy_report.__dict__,
                },
            },
        )

        # 4. Mediation Mode (Phase G) if consensus low
        if synthesis.overall_confidence < 0.7:
            logger.info(f"⚖️ Consensus Low ({synthesis.overall_confidence:.2f}). Invoking Mediator...")
            from src.core.agents.governance.mediator import MediatorAgent

            llm_provider = icgl.registry.get_llm_provider() if hasattr(icgl.registry, "get_llm_provider") else None
            mediator = MediatorAgent(llm_provider=llm_provider)

            problem_mediation = Problem(
                title=adr.title,
                context=adr.context,
                metadata={"decision": adr.decision, "agent_results": [asdict(r) for r in synthesis.individual_results]},
            )
            mediation_result = await mediator.analyze(problem_mediation, icgl.kb)

            current_state = icgl.kb.get_synthesis_state(adr.id) or {}
            if "synthesis" in current_state:
                current_state["synthesis"]["mediation"] = {
                    "analysis": mediation_result.analysis,
                    "confidence": mediation_result.confidence,
                    "concerns": mediation_result.concerns,
                }
                icgl.kb.save_synthesis_state(adr.id, current_state)

            logger.info("⚖️ Mediation Complete.")

        # 5. Record Observability Data
        duration = round((time.time() - start_time) * 1000)
        current_state = icgl.kb.get_synthesis_state(adr.id) or {}
        current_state["latency_ms"] = duration
        icgl.kb.save_synthesis_state(adr.id, current_state)

        icgl.observer.record_metric(
            agent_id="consensys-orchestrator",
            role="Orchestrator",
            latency=float(duration),
            confidence=synthesis.overall_confidence,
            success=True,
            task_type="governance_cycle",
        )

        # FINAL BROADCAST
        # Fetching status locally to avoid global state issues
        current_status = await get_status()
        await manager.broadcast({"type": "status_update", "status": current_status.data})

        # SCP BROADCAST (Real-time alerts)
        if alerts:
            for alert in alerts:
                await scp_manager.broadcast(
                    {
                        "id": f"alert-{uid()}",
                        "type": "event",
                        "data": {
                            "event_type": "sentinel_signal",
                            "message": alert.message,
                            "source": "Sentinel",
                            "severity": alert.severity.value.lower()
                            if hasattr(alert.severity, "value")
                            else str(alert.severity).lower(),
                            "timestamp": now(),
                        },
                    }
                )

        # Update ADR in KB with signals
        adr.sentinel_signals = [str(a) for a in alerts]
        icgl.kb.add_adr(adr)

        logger.info(f"✨ Analysis Complete for {adr.id} ({duration}ms)")

    except Exception as e:
        logger.error(f"Async Analysis Failure: {e}", exc_info=True)
        icgl = get_icgl()
        icgl.kb.save_synthesis_state(adr.id, {"status": "failed", "error": str(e)})

        try:
            icgl = get_icgl()
            icgl.observer.record_metric(
                agent_id="consensys-orchestrator",
                role="Orchestrator",
                latency=round((time.time() - start_time) * 1000),
                confidence=0.0,
                success=False,
                error_code=str(e),
                task_type="governance_cycle",
            )
        except Exception:
            pass


def generate_consensus_mindmap(title: str, synthesis) -> str:
    """Generates Mermaid mindmap syntax from synthesis results."""
    lines: List[str] = ["mindmap", f"  root(({title}))"]

    # Consensus Node
    lines.append("    Consensus")
    for rec in synthesis.consensus_recommendations[:3]:
        clean_rec = rec.replace("(", "[").replace(")", "]").replace('"', "'")
        lines.append(f"      {clean_rec}")

    # Agents Node
    lines.append("    Agents")
    for res in synthesis.individual_results:
        role = res.role.value
        conf = int(res.confidence * 100)
        lines.append(f"      {role} ({conf}%)")
        if res.concerns:
            first_concern = res.concerns[0].replace("(", "[").replace(")", "]")
            lines.append(f"        {first_concern}")

    # Risks Node
    if synthesis.all_concerns:
        lines.append("    Risks")
        for concern in synthesis.all_concerns[:3]:
            clean_concern = concern.replace("(", "[").replace(")", "]")
            lines.append(f"      {clean_concern}")

    return "\n".join(lines)
