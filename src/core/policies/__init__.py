"""
Consensus AI — Policy Enforcement Package
==========================================

Pre-execution policy checks and violations.

Usage:
    from src.core.policies import PolicyEnforcer, PolicyViolationError

    enforcer = PolicyEnforcer(kb)
    try:
        enforcer.check_adr_creation(adr)
    except PolicyViolationError as e:
        print(f"Policy violated: {e.policy_code}")
"""

from .enforcement import PolicyEnforcer
from .exceptions import (
    AuthorityViolationError,
    ConceptModificationError,
    ImmutabilityViolationError,
    PolicyViolationError,
    StrategicOptionViolationError,
)

__all__ = [
    "PolicyEnforcer",
    "PolicyViolationError",
    "AuthorityViolationError",
    "ImmutabilityViolationError",
    "ConceptModificationError",
    "StrategicOptionViolationError",
]
