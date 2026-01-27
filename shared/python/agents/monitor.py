"""
Monitor Agent - System Health and Resource Monitoring
====================================================

The Monitor Agent tracks system health, resource usage, uptime,
and performance metrics for the ICGL system.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil

from shared.python.agents.base import Agent, AgentResult, AgentRole, Problem
from shared.python.kb.schemas import now


class HealthStatus:
    """Represents system health status."""

    def __init__(self):
        self.timestamp = now()
        self.status = "unknown"
        self.cpu_percent: float = 0.0
        self.memory_percent: float = 0.0
        self.disk_percent: float = 0.0
        self.uptime_seconds: float = 0.0
        self.issues: List[str] = []


class MonitorAgent(Agent):
    """
    Monitor Agent: Real-time system health and performance monitoring.

    Responsibilities:
    - Track CPU, memory, and disk usage
    - Monitor system uptime and availability
    - Detect resource bottlenecks and anomalies
    - Generate health check reports
    - Alert on concerning trends
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="monitor",
            role=AgentRole.MONITOR,
            llm_provider=llm_provider,
        )
        self.health_history: List[HealthStatus] = []
        self.start_time = datetime.now()
        self.alert_thresholds = {
            "cpu": 80.0,  # percent
            "memory": 85.0,  # percent
            "disk": 90.0,  # percent
        }

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Analyzes problems from system health and monitoring perspective.

        Focus areas:
        - Performance impact and resource requirements
        - Monitoring and observability needs
        - Health check implications
        - System stability concerns
        """

        # Get current system health
        health = self._get_system_health()

        # Analyze performance impact
        performance_impact = await self._analyze_performance_impact(problem)

        # Check resource requirements
        resource_needs = self._estimate_resource_needs(problem)

        # Generate monitoring recommendations
        monitoring_plan = self._generate_monitoring_plan(problem)

        # Build comprehensive analysis
        analysis = f"""
=== CURRENT SYSTEM HEALTH ===
Status: {health.status.upper()}
CPU Usage: {health.cpu_percent:.1f}%
Memory Usage: {health.memory_percent:.1f}%
Disk Usage: {health.disk_percent:.1f}%
Uptime: {self._format_uptime(health.uptime_seconds)}

=== PERFORMANCE IMPACT ANALYSIS ===
{performance_impact}

=== ESTIMATED RESOURCE NEEDS ===
{resource_needs}

=== MONITORING RECOMMENDATIONS ===
{monitoring_plan}

=== HEALTH CONCERNS ===
{self._format_issues(health.issues)}
"""

        # Record health snapshot
        self.health_history.append(health)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                "Add health checks for new components",
                "Monitor resource usage during implementation",
                "Set up alerts for anomalies",
                "Establish baseline performance metrics",
            ],
            concerns=[
                "May impact system performance" if resource_needs else "Resource impact expected to be minimal",
                f"{len(health.issues)} system issues detected" if health.issues else "No current system issues",
                "Requires ongoing monitoring",
            ],
            confidence=0.82,
        )

    def _get_system_health(self) -> HealthStatus:
        """Get current system health metrics."""
        health = HealthStatus()

        try:
            # CPU usage
            health.cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            health.memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage("/")
            health.disk_percent = disk.percent

            # Uptime
            uptime = datetime.now() - self.start_time
            health.uptime_seconds = uptime.total_seconds()

            # Determine overall status
            health.issues = self._check_thresholds(health.cpu_percent, health.memory_percent, health.disk_percent)

            if not health.issues:
                health.status = "healthy"
            elif len(health.issues) == 1:
                health.status = "degraded"
            else:
                health.status = "critical"

        except Exception as e:
            health.status = "unknown"
            health.issues.append(f"Failed to collect metrics: {str(e)}")

        return health

    def _check_thresholds(self, cpu: float, memory: float, disk: float) -> List[str]:
        """Check if any metrics exceed alert thresholds."""
        issues = []

        if cpu > self.alert_thresholds["cpu"]:
            issues.append(f"⚠️ CPU usage high: {cpu:.1f}% (threshold: {self.alert_thresholds['cpu']}%)")

        if memory > self.alert_thresholds["memory"]:
            issues.append(f"⚠️ Memory usage high: {memory:.1f}% (threshold: {self.alert_thresholds['memory']}%)")

        if disk > self.alert_thresholds["disk"]:
            issues.append(f"🔴 Disk usage critical: {disk:.1f}% (threshold: {self.alert_thresholds['disk']}%)")

        return issues

    async def _analyze_performance_impact(self, problem: Problem) -> str:
        """Analyze potential performance impact of the problem."""
        prompt = f"""
Analyze the potential performance impact of this change.

Change: {problem.title}
Details: {problem.context}

Provide a brief assessment (2-3 sentences) of:
1. Expected performance impact (high/medium/low)
2. Key performance considerations
3. Recommended performance testing
"""

        try:
            impact = await self._ask_llm(prompt)
            return impact.strip()
        except Exception:
            return (
                "Performance impact assessment pending. "
                "Recommend baseline testing before and after implementation "
                "to quantify actual impact."
            )

    def _estimate_resource_needs(self, problem: Problem) -> str:
        """Estimate resource requirements for the change."""
        context_lower = problem.context.lower()
        needs = []

        # Check for resource-intensive operations
        if any(kw in context_lower for kw in ["database", "migration", "index", "large dataset"]):
            needs.append("📊 Database: Moderate to High")

        if any(kw in context_lower for kw in ["api", "endpoint", "request", "traffic"]):
            needs.append("🌐 Network: Low to Moderate")

        if any(kw in context_lower for kw in ["computation", "processing", "analysis", "ml"]):
            needs.append("💻 CPU: Moderate to High")

        if any(kw in context_lower for kw in ["cache", "storage", "memory", "buffer"]):
            needs.append("🧠 Memory: Moderate to High")

        if not needs:
            needs.append("✅ Minimal resource impact expected")

        return "\n".join(needs)

    def _generate_monitoring_plan(self, problem: Problem) -> str:
        """Generate monitoring recommendations."""
        return """
1. Add health check endpoint for new functionality
2. Instrument code with performance metrics
3. Set up logging for key operations
4. Configure alerts for error rates and latency
5. Dashboard for real-time visibility
6. Weekly performance review
"""

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        uptime = timedelta(seconds=int(seconds))
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def _format_issues(self, issues: List[str]) -> str:
        """Format health issues for display."""
        if not issues:
            return "✅ No issues detected"

        return "\n".join(issues)

    def get_health_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate health report for the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_health = [h for h in self.health_history if datetime.fromisoformat(h.timestamp) > cutoff]

        if not recent_health:
            return {
                "period": f"Last {hours} hours",
                "data_points": 0,
                "message": "No data available",
            }

        # Calculate averages
        avg_cpu = sum(h.cpu_percent for h in recent_health) / len(recent_health)
        avg_memory = sum(h.memory_percent for h in recent_health) / len(recent_health)

        # Count issues
        total_issues = sum(len(h.issues) for h in recent_health)

        return {
            "period": f"Last {hours} hours",
            "data_points": len(recent_health),
            "avg_cpu_percent": round(avg_cpu, 2),
            "avg_memory_percent": round(avg_memory, 2),
            "total_issues": total_issues,
            "current_status": recent_health[-1].status if recent_health else "unknown",
        }

    def set_alert_threshold(self, metric: str, threshold: float) -> bool:
        """Update alert threshold for a metric."""
        if metric in self.alert_thresholds:
            self.alert_thresholds[metric] = threshold
            return True
        return False

    def get_current_metrics(self) -> Dict[str, float]:
        """Get current resource metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
        }
