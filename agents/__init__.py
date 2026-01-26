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
from .catalyst import CatalystAgent
from .engineer import EngineerAgent
from .execution_orchestrator import ExecutionOrchestratorAgent
from .executive_agent import ExecutiveAgent
from .failure import FailureAgent
from .guardian import ConceptGuardian
from .guardian_sentinel import GuardianSentinelAgent
from .hr import HRAgent
from .knowledge_steward import KnowledgeStewardAgent
from .performance_analyzer import PerformanceAnalyzerAgent
from .policy import PolicyAgent
from .refactoring import RefactoringAgent
from .registry import AgentRegistry, SynthesizedResult
from .researcher import ResearcherAgent
from .secretary import SecretaryAgent
from .security_orchestrator import SecurityOrchestratorAgent
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
    "HDALAgent",
    "KnowledgeStewardAgent",
    "RefactoringAgent",
    "MonitorAgent",
    "CodeSpecialist",
    "VerificationAgent",
    "TestingAgent",
    "CatalystAgent",
    "SecurityOrchestratorAgent",
    "ExecutionOrchestratorAgent",
    "ValidationOrchestratorAgent",
    "PerformanceAnalyzerAgent",
    "ResearcherAgent",
    "ExecutiveAgent",
]
