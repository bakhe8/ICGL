"""
Consensus AI — Agents Package
==============================

Multi-agent runtime for specialized reasoning.

Components:
- Agent Registry
- Specialized Agents (Architect, Failure, Policy, Guardian, Sentinel)
"""

from .base import (
    Agent,
    MockAgent,
    AgentResult,
    AgentRole,
    Problem,
)
from .registry import AgentRegistry, SynthesizedResult
from .architect import ArchitectAgent
from .failure import FailureAgent
from .policy import PolicyAgent
from .guardian import ConceptGuardian
from .sentinel_agent import SentinelAgent
from .builder import BuilderAgent

from .specialists import CodeSpecialist


from .monitor_agent import MonitorAgent
from .secretary_agent import SecretaryAgent
from .archivist_agent import ArchivistAgent
from .development_manager import DevelopmentManagerAgent
__all__ = [
    "Agent",
    "MockAgent",
    "AgentResult",
    "AgentRole",
    "Problem",
    "AgentRegistry",
    "SynthesizedResult",
    "ArchitectAgent",
    "FailureAgent",
    "PolicyAgent",
    "ConceptGuardian",
    "SentinelAgent",
    "BuilderAgent",
    "CodeSpecialist",
    "MonitorAgent",
    "SecretaryAgent",
    "ArchivistAgent",
    "DevelopmentManagerAgent",
]
