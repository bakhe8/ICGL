"""
Consensus AI — Agents Package
==============================

Multi-agent runtime for specialized reasoning.

Components:
- Agent Registry
- Specialized Agents (Architect, Failure, Policy, Guardian, Sentinel)
"""

from .architect import ArchitectAgent
from .base import (
    Agent,
    AgentResult,
    AgentRole,
    MockAgent,
    Problem,
)
from .builder import BuilderAgent
from .failure import FailureAgent
from .guardian import ConceptGuardian
from .policy import PolicyAgent
from .registry import AgentRegistry, SynthesizedResult
from .sentinel_agent import SentinelAgent
from .specialists import CodeSpecialist
from .testing import TestingAgent
from .verification import VerificationAgent

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
    "VerificationAgent",
    "TestingAgent",
]
