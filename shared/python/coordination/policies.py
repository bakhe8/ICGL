"""
ICGL Coordination — Policies
============================

Governs interaction policies between agents.
"""

from enum import Enum


class CoordinationPolicy(Enum):
    CONSENSUS = "consensus"
    EXECUTIVE_DECISION = "executive"
    VETO_POWER = "veto"
    ADVISORY = "advisory"


POLICY_READ_ONLY = CoordinationPolicy.ADVISORY


def get_default_policy() -> CoordinationPolicy:
    return CoordinationPolicy.CONSENSUS
