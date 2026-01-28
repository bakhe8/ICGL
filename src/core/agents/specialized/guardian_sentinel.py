"""
Consensus AI — Guardian Sentinel Agent
=======================================

Consolidates System Monitoring and Risk Detection.
Responsible for architectural safety, real-time metrics, and drift monitoring.
"""

from typing import Any, Optional

import psutil

from src.core.agents.core.base import Agent, AgentResult, AgentRole, Problem


class GuardianSentinelAgent(Agent):
    """
    The Guardian Sentinel: Merges Sentinel and Monitor logic.
    Provides combined reports on system health (CPU/Memory) and governance risk.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="agent-guardian-sentinel",
            role=AgentRole.SENTINEL,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        System-level audit: CPU, Memory, Disk + Drift detection.
        Phase 6: Self-Expansion Trigger.
        """
        # 0. Self-Awareness Trigger (Phase 6)
        if (
            "network" in problem.context.lower()
            or "connectivity" in problem.context.lower()
        ):
            print(
                f"   👁️ [{self.agent_id}] Detecting capability gap for network monitoring..."
            )
            await self.propose_expansion(
                new_capability="Network Latency & Connectivity Monitoring",
                justification="Current scope is limited to local system resources (CPU/Mem/Disk). Network issues remain 'blind spots' for the Sentinel.",
            )

        # 1. Operational Check (Performance Guard)
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        # IO Stats
        io = psutil.disk_io_counters()
        io_report = f"Read: {io.read_bytes / 1024 / 1024:.1f}MB, Write: {io.write_bytes / 1024 / 1024:.1f}MB"

        # 2. Risk Detection Thresholds
        concerns = []
        if cpu > 80:
            concerns.append(
                f"High CPU Load detected ({cpu}%). Proposal execution may be delayed."
            )
        if mem > 85:
            concerns.append(
                f"Critical Memory Pressure ({mem}%). Risk of OOM during complex synthesis."
            )
        if disk > 90:
            concerns.append(
                f"Disk Space Warning ({disk}%). Logging artifacts may fail."
            )

        # 4. Phase 13.4: Red Team Surveillance (Chaos Watch)
        chaos_status = "SAFE"
        if "chaos" in problem.context.lower() or "red team" in problem.context.lower():
            chaos_status = "ACTIVE_MONITORING"
            concerns.append("⚠️ Red Team Activity Detected: Verifying Safety Harness...")

        prompt = f"""
        Analyze the following problem as the Guardian Sentinel:
        
        Title: {problem.title}
        Context: {problem.context}
        
        📡 OPERATIONAL METRICS:
        - CPU Usage: {cpu}%
        - Memory Usage: {mem}%
        - Disk Usage: {disk}%
        - IO Activity: {io_report}
        
        👹 CHAOS WATCH STATUS: {chaos_status}
        
        Tasks:
        1. Detect architectural drift or safety violations.
        2. Evaluate if the current system load ({cpu}%) poses a risk to this proposal.
        3. Identify any 'Silent Failures' in the proposed logic.
        4. If Chaos/Red Team is active, CONFIRM that 'Simulation Mode' is respected.
        """

        analysis = await self._ask_llm(prompt, problem)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                f"Health Check: CPU {cpu}% / MEM {mem}% / DISK {disk}%",
                "Approve execution path if thresholds remain stable.",
                "Verify no breaking changes to core security protocols.",
            ],
            concerns=concerns,
            confidence=1.0,  # High confidence for sensory data
        )
