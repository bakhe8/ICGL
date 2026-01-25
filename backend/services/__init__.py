"""
Consensus AI — AutoBeto Package
================================

A Governance-First Intelligence System for Long-Lived Decisions.

This package provides:
- kb: Knowledge Base (schemas, concepts, policies, ADRs)
- governance: ICGL orchestrator
- sentinel: Risk detection and drift prevention
- hdal: Human Decision Authority Layer
- validator: Schema validation

Usage:
    from autobeto.kb import KnowledgeBase, Concept, Policy, ADR
    from autobeto.governance import ICGL
    from autobeto.sentinel import Sentinel
    from autobeto.hdal import HDAL
"""

from .kb import (
    KnowledgeBase,
    Concept,
    Policy,
    SentinelSignal,
    ADR,
    HumanDecision,
    LearningLog,
    uid,
    now,
)
from .governance import ICGL
from .sentinel import Sentinel
from .hdal import HDAL

__version__ = "0.1.0"

__all__ = [
    "KnowledgeBase",
    "Concept",
    "Policy",
    "SentinelSignal",
    "ADR",
    "HumanDecision",
    "LearningLog",
    "ICGL",
    "Sentinel",
    "HDAL",
    "uid",
    "now",
]


def run_demo():
    """
    Demonstrates the ICGL cycle with a sample ADR.
    
    Usage:
        python -m autobeto
        # or via CLI:
        autobeto consensus --human bakheet
    """
    kb = KnowledgeBase()
    sentinel = Sentinel()
    hdal = HDAL()
    icgl = ICGL(kb, sentinel, hdal)

    # Example ADR
    adr = ADR(
        id=uid(),
        title="Bootstrap Example ADR",
        status="DRAFT",
        context="Initial skeleton validation",
        decision="Validate ICGL skeleton",
        consequences=["System structure validated"],
        related_policies=[],
        sentinel_signals=[],
        human_decision_id=None,
    )

    icgl.run_cycle(adr, human_id="bakheet")

    print("\n📚 Knowledge Base Snapshot:")
    print(f"   Concepts: {len(kb.concepts)}")
    print(f"   Policies: {len(kb.policies)}")
    print(f"   ADRs: {len(kb.adrs)}")
    print(f"   Human Decisions: {len(kb.human_decisions)}")
    print(f"   Learning Logs: {len(kb.learning_log)}")
