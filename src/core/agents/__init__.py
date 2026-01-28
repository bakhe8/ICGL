"""
Consensus AI — Agents Package (Reorganized)
===========================================

Structured multi-agent runtime. Agents are now grouped by function.
"""

# Core Imports
# Standardized Aliases (Backwards Compatibility)
from src.core.agents.core.architect import ArchitectAgent
from src.core.agents.core.base import (
    Agent,
    AgentResult,
    AgentRole,
    MockAgent,
    Problem,
)
from src.core.agents.core.builder import BuilderAgent
from src.core.agents.core.engineer import EngineerAgent
from src.core.agents.governance.executive_agent import ExecutiveAgent
from src.core.agents.governance.hdal_agent import HDALAgent
from src.core.agents.governance.mediator import MediatorAgent
from src.core.agents.governance.policy import PolicyAgent
from src.core.agents.infrastructure.registry import AgentRegistry, SynthesizedResult
from src.core.agents.operations.failure import FailureAgent
from src.core.agents.operations.monitor import MonitorAgent
from src.core.agents.operations.testing import TestingAgent
from src.core.agents.operations.verification import VerificationAgent
from src.core.agents.specialists.researcher import ResearcherAgent
from src.core.agents.specialists.specialists import CodeSpecialist
from src.core.agents.specialists.ui_ux import UIUXAgent
from src.core.agents.specialized.guardian import ConceptGuardian
from src.core.agents.specialized.guardian_sentinel import GuardianSentinelAgent
from src.core.agents.specialized.security_orchestrator import SecurityOrchestratorAgent
from src.core.agents.specialized.sentinel_agent import SentinelAgent
from src.core.agents.support.archivist import ArchivistAgent
from src.core.agents.support.knowledge_steward import KnowledgeStewardAgent
from src.core.agents.support.secretary import SecretaryAgent

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
    "GuardianSentinelAgent",
    "BuilderAgent",
    "EngineerAgent",
    "TestingAgent",
    "VerificationAgent",
    "HDALAgent",
    "MonitorAgent",
    "SentinelAgent",
    "ExecutiveAgent",
    "CodeSpecialist",
    "UIUXAgent",
    "ResearcherAgent",
    "SecurityOrchestratorAgent",
    "MediatorAgent",
    "ArchivistAgent",
    "SecretaryAgent",
    "KnowledgeStewardAgent",
]


def __getattr__(name):
    if name == "ExecutiveAgent":
        from .governance.executive_agent import ExecutiveAgent

        return ExecutiveAgent
    raise AttributeError(f"module {__name__} has no attribute {name}")
