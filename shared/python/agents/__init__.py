"""
Consensus AI — Agents Package
==============================

Multi-agent runtime for specialized reasoning.

Components:
- Agent Registry
- Specialized Agents (Architect, Failure, Policy, Guardian, Sentinel)
"""

from shared.python.agents.base import (
    Agent,
    AgentResult,
    AgentRole,
    MockAgent,
    Problem,
)

from .architect import ArchitectAgent
from .builder import BuilderAgent
from .catalyst import CatalystAgent
from .engineer import EngineerAgent
from .execution_orchestrator import ExecutionOrchestratorAgent

# from .executive_agent import ExecutiveAgent  # Circular dependency via governance.signing_queue
from .failure import FailureAgent
from .guardian import ConceptGuardian
from .guardian_sentinel import GuardianSentinelAgent
from .hdal_agent import HDALAgent
from .hr import HRAgent
from .mediator import MediatorAgent
from .monitor import MonitorAgent
from .performance_analyzer import PerformanceAnalyzerAgent
from .policy import PolicyAgent
from .refactoring import RefactoringAgent
from .registry import AgentRegistry, SynthesizedResult
from .researcher import ResearcherAgent
from .secretary import SecretaryAgent
from .security_orchestrator import SecurityOrchestratorAgent
from .sentinel_agent import SentinelAgent
from .specialists import CodeSpecialist
from .testing import TestingAgent
from .validation_orchestrator import ValidationOrchestratorAgent
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
    "GuardianSentinelAgent",
    "BuilderAgent",
    "EngineerAgent",
    "HRAgent",
    "SecretaryAgent",
    "TestingAgent",
    "VerificationAgent",
    "HDALAgent",
    "MonitorAgent",
    "SentinelAgent",
    "ExecutiveAgent",
    "PerformanceAnalyzerAgent",
    "RefactoringAgent",
    "ResearcherAgent",
    "SecurityOrchestratorAgent",
    "CodeSpecialist",
    "ValidationOrchestratorAgent",
    "MediatorAgent",
    "CatalystAgent",
    "ExecutionOrchestratorAgent",
]


def __getattr__(name):
    if name == "ExecutiveAgent":
        from .executive_agent import ExecutiveAgent

        return ExecutiveAgent
    raise AttributeError(f"module {__name__} has no attribute {name}")
