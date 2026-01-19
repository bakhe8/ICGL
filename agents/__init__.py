"""
Consensus AI — Agents Package
==============================

Multi-agent runtime for specialized reasoning.

Components:
- Agent Registry
- Specialized Agents (Architect, Failure, Policy, Guardian, Sentinel)
"""

from agents.base import (
    Agent,
    MockAgent,
    AgentResult,
    AgentRole,
    Problem,
)
from agents.registry import AgentRegistry, SynthesizedResult
from agents.architect import ArchitectAgent
from agents.failure import FailureAgent
from agents.policy import PolicyAgent
from agents.guardian import ConceptGuardian
from agents.sentinel_agent import SentinelAgent
from agents.builder import BuilderAgent

from agents.specialists import CodeSpecialist


from agents.monitor_agent import MonitorAgent
from agents.secretary_agent import SecretaryAgent
from agents.archivist_agent import ArchivistAgent
from agents.development_manager import DevelopmentManagerAgent
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
