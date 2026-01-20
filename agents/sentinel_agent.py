"""
Consensus AI — Sentinel Agent
==============================

Agent wrapper for the Sentinel Rule Engine.
Allows the Sentinel to participate in the agent pool discussion.
"""

from pathlib import Path
from agents.base import Agent, AgentRole, Problem, AgentResult
from sentinel.sentinel import Sentinel, RuleRegistry


class SentinelAgent(Agent):
    """
    Sentinel wrapper agent.
    Runs the Sentinel rule engine and reports alerts as part of synthesis.
    """
    
    def __init__(self, sentinel: Sentinel = None):
        super().__init__(agent_id="agent-sentinel", role=AgentRole.SENTINEL)
        self.sentinel = sentinel or Sentinel()
        
    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # Minimal real scan: look at latest ADRs for sentinel signals
        concerns = []
        recommendations = []
        analysis_lines = ["Sentinel risk posture:"]
        latest_alerts = []
        log_lines = []
        try:
            if hasattr(kb, "adrs"):
                adrs = list(kb.adrs.values())
                if adrs:
                    latest = sorted(adrs, key=lambda x: x.created_at, reverse=True)[:3]
                    for adr in latest:
                        if adr.sentinel_signals:
                            latest_alerts.extend(adr.sentinel_signals)
                    analysis_lines.append(f"Checked {len(latest)} recent ADR(s).")
                else:
                    analysis_lines.append("No ADRs found in KB.")
        except Exception as e:
            concerns.append(f"ADR scan failed: {e}")

        # Read recent error log if exists
        try:
            log_path = Path(__file__).resolve().parents[2] / "error.log"
            if log_path.exists():
                log_lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-20:]
                if log_lines:
                    analysis_lines.append(f"Read {len(log_lines)} recent error.log lines.")
                else:
                    analysis_lines.append("error.log is empty.")
            # runtime health tail
            health_log = Path(__file__).resolve().parents[2] / "data" / "runtime_health.log"
            if health_log.exists():
                tail = health_log.read_text(encoding="utf-8", errors="ignore").splitlines()[-10:]
                if tail:
                    log_lines.extend(tail)
                    analysis_lines.append("Included runtime_health.log tail.")
        except Exception as e:
            concerns.append(f"Log read failed: {e}")

        if latest_alerts:
            concerns.extend(latest_alerts)
        else:
            analysis_lines.append("No recorded sentinel signals in recent ADRs.")

        if not recommendations:
            recommendations.append("استمر بفحص المخاطر قبل أي قرار")

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis="\n".join(analysis_lines),
            recommendations=recommendations,
            concerns=concerns,
            references=log_lines,
            confidence=0.8 if concerns else 1.0
        )

    def detect_patterns(self, events: list[dict], limit: int = 10) -> dict:
        """
        Analyze a list of events/logs for patterns.
        Real implementation using simple heuristics on the provided events.
        """
        alerts = []
        
        # Heuristic 1: High frequency of errors
        errors = [e for e in events if e.get("level") == "error" or "error" in str(e).lower()]
        if len(errors) > 3:
            alerts.append({
                "alert_id": "pat-err-burst",
                "pattern": "Error Burst",
                "severity": "high",
                "description": f"Detected {len(errors)} errors in recent logs.",
                "event_count": len(errors),
                "timestamp": errors[-1].get("timestamp", "now")
            })

        # Heuristic 2: Frequent proposal creation
        proposals = [e for e in events if e.get("type") == "proposal_created"]
        if len(proposals) > 2:
            alerts.append({
                "alert_id": "pat-prop-spam",
                "pattern": "Proposal Spike",
                "severity": "medium",
                "description": "Unusual frequency of new proposals.",
                "event_count": len(proposals),
                "timestamp": proposals[-1].get("timestamp", "now")
            })
            
        # Heuristic 3: Conflict detection (Mock for now if no real conflict events)
        conflicts = [e for e in events if e.get("type") == "conflict_detected"]
        if conflicts:
             alerts.append({
                "alert_id": "pat-conf-recur",
                "pattern": "Recurring Conflicts",
                "severity": "medium",
                "description": "System is experiencing repeated policy conflicts.",
                "event_count": len(conflicts),
                "timestamp": conflicts[-1].get("timestamp", "now")
            })

        return {
            "analyzed_events": len(events),
            "alerts_found": len(alerts),
            "alerts": alerts[:limit],
            "fallback": False
        }
