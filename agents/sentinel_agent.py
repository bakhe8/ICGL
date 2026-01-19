"""
Consensus AI — Sentinel Agent
==============================

Agent wrapper for the Sentinel Rule Engine.
Allows the Sentinel to participate in the agent pool discussion.
"""

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
        except Exception as e:
            concerns.append(f"ADR scan failed: {e}")

        # Read recent error log if exists
        try:
            log_path = Path(__file__).resolve().parents[2] / "error.log"
            if log_path.exists():
                log_lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-20:]
                if log_lines:
                    analysis_lines.append(f"Read {len(log_lines)} recent error.log lines.")
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
