"""
ICGL — HR Department (Workforce Management)
============================================

This package manages agent lifecycle, task scheduling, and operational cycles.

Modules:
- workforce_manager: Central manager for all agents
- scheduler: Task scheduling and coordination
- heartbeat: Continuous operational pulse
- health_monitor: Agent health checks and monitoring
"""

from .workforce_manager import WorkforceManager
from .scheduler import AgentScheduler
from .heartbeat import HeartbeatService

__all__ = [
    "WorkforceManager",
    "AgentScheduler",
    "HeartbeatService",
]
