"""
Consensus AI — Agents Package
==============================

Multi-agent runtime for specialized reasoning.

Components:
- Agent Registry
- Specialized Agents (Architect, Failure, Policy, Guardian, Sentinel)
"""

from .architect import ArchitectAgent
from .archivist import ArchivistAgent
from .base import (
    Agent,
    AgentResult,
    AgentRole,
    MockAgent,
    Problem,
)
from .builder import BuilderAgent
from .catalyst import CatalystAgent
from .engineer import EngineerAgent
from .failure import FailureAgent
from .guardian import ConceptGuardian
from .guardian_sentinel import GuardianSentinelAgent
from .hr import HRAgent
from .knowledge_steward import KnowledgeStewardAgent
from .policy import PolicyAgent
from .refactoring import RefactoringAgent
from .registry import AgentRegistry, SynthesizedResult
from .secretary import SecretaryAgent
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
    "ArchivistAgent",
    "FailureAgent",
    "PolicyAgent",
    "ConceptGuardian",
    "GuardianSentinelAgent",
    "BuilderAgent",
    "EngineerAgent",
    "HRAgent",
    "SecretaryAgent",
    "HDALAgent",
    "KnowledgeStewardAgent",
    "RefactoringAgent",
    "MonitorAgent",
    "CodeSpecialist",
    "VerificationAgent",
    "TestingAgent",
    "CatalystAgent",
]
