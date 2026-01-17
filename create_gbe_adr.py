
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

from icgl.kb.persistent import PersistentKnowledgeBase
from icgl.kb.schemas import ADR, ID

def update_adr():
    kb = PersistentKnowledgeBase()
    
    adr_id = "a169f8c2-eda8-4afa-ad7c-89a47db2c209"
    
    title = "Introduce Governance Binding Engine (GBE)"
    
    context = """
During live conversational ICGL operation, the system repeatedly failed to bind human intent into structured governance artifacts.

Specifically:
* Human explicitly requested policy binding inside ADR.
* Semantic understanding succeeded.
* Structural mutation of ADR failed.
* Sentinel continuously emitted: `ADR has no related policies`.

This confirmed a systemic capability gap documented in:
> Capability Gap — Intent → Governance Binding Failure

The system currently lacks a deterministic layer that translates conversational intent into schema-safe governance mutations.
"""

    decision = """
Introduce a dedicated internal subsystem:

> 🧠 Governance Binding Engine (GBE)

GBE will act as the authoritative translator between:
`Human Intent  →  Validated Directives  →  Structured Governance Mutation`
"""

    consequences = [
        "Positive: Deterministic governance consistency.",
        "Positive: Removal of Sentinel false warnings.",
        "Positive: Reduced human friction.",
        "Positive: Enables future autonomous governance maturity.",
        "Negative: Added architectural complexity.",
        "Negative: Requires strict testing and validation."
    ]

    # Create ADR object
    # We set status to ACCEPTED because implementation is complete.
    adr = ADR(
        id=adr_id,
        title=title,
        status="ACCEPTED",
        context=context.strip(),
        decision=decision.strip(),
        consequences=consequences,
        related_policies=["P-GOV-09", "P-CORE-01", "P-ARCH-05"], # Proposed policies from user text
        sentinel_signals=[],
        human_decision_id=None,
        created_at=datetime.utcnow()
    )

    kb.add_adr(adr)
    print(f"Updated ADR: {title} ({adr_id})")
    print("✅ Status: ACCEPTED")

if __name__ == "__main__":
    update_adr()
