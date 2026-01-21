"""
Consensus AI — Policy Enforcement Package
==========================================

Pre-execution policy checks and violations.

Usage:
    from icgl.policies import PolicyEnforcer, PolicyViolationError
    
    enforcer = PolicyEnforcer(kb)
    try:
        enforcer.check_adr_creation(adr)
    except PolicyViolationError as e:
        print(f"Policy violated: {e.policy_code}")
"""

from .exceptions import (
    PolicyViolationError,
    AuthorityViolationError,
    ImmutabilityViolationError,
    ConceptModificationError,
    StrategicOptionViolationError,
)
from .enforcement import PolicyEnforcer

__all__ = [
    "PolicyEnforcer",
    "PolicyViolationError",
    "AuthorityViolationError",
    "ImmutabilityViolationError",
    "ConceptModificationError",
    "StrategicOptionViolationError",
]
