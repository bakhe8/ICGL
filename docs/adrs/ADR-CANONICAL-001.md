# ADR-CANONICAL-001: Governed Autonomy & Adapter-Only External Integration

**Status:** ✅ ACCEPTED  
**Effective Date:** 2026-01-17  
**Supersedes:** ADR-PILOT-OPS-05-001 (Pilot)  
**Related Policies:**

- P-OPS-05 — Foundational Autonomy Protocol
- P-GOV-01 — Sovereign Approval Authority
- P-SEC-02 — External Surface Control
- P-OBS-01 — Traceability & Auditability

**Owner:** Office of the CEO  
**Scope:** All Agents, Orchestrators, Integrations, and Execution Pipelines

---

## 1. Context

The system has transitioned toward a model where **Agents are expected to proactively identify and fulfill their operational needs** while maintaining strict sovereign governance and traceability.

A controlled pilot ([ADR-PILOT-OPS-05-001](file:///c:/Users/Bakheet/Documents/Projects/ICGL/docs/adrs/ADR-PILOT-OPS-05-001.md)) was executed to validate:

- Agent self-initiated operational requests
- Formal inter-department coordination
- Governance gating prior to execution
- External integration isolation via adapters
- End-to-end traceability

The pilot demonstrated **successful compliance** across all stages with:

- ✅ No architectural violations
- ✅ No unauthorized system mutations
- ✅ Full audit linkage from request to execution

The organization now requires a **canonical, binding decision** to elevate this operating model from pilot to standard.

---

## 2. Decision

The organization formally adopts the following **canonical principles**:

### 2.1 Governed Autonomy

All Agents are designated as **autonomous operational owners** of their internal needs.

Each Agent **SHALL**:

1. Detect and declare its own operational gaps or requirements.
2. Submit a formal `OperationalRequest` through the `CoordinationOrchestrator`.
3. Provide explicit rationale, scope, urgency, and risk signals.
4. **Await sovereign approval** before any execution affecting persistent state, integrations, or behavior.

**No Agent is permitted to self-authorize execution.**

### 2.2 Adapter-Only External Integration

All external system interactions **SHALL**:

- Be implemented exclusively through **isolated adapters**.
- Operate in **outbound-only mode** by default.
- Avoid any direct coupling with core systems (Sentinel, Governance, Orchestrator, Knowledge Base).
- Include a **deterministic Kill Switch** mechanism.
- Declare explicit scope, permissions, and data boundaries.

Any deviation requires an **explicit ADR override**.

### 2.3 Mandatory Traceability Chain

Every operational execution **SHALL** maintain the following immutable linkage:

```
OperationalRequest
  → Governance Review
    → ADR Approval
      → Controlled Execution
        → Audit Event
```

**No execution artifact is considered valid unless this chain is provably intact.**

### 2.4 Governance Gate Supremacy

The Governance layer remains the **sole authority** empowered to:

- Approve or reject operational requests.
- Authorize permanent state changes.
- Sanction integrations.
- Declare policy exceptions.

All subordinate systems must enforce this constraint **mechanically**.

---

## 3. Implementation Requirements

### 3.1 Automatic Request–ADR Binding

The platform **SHALL** implement:

- Automatic bidirectional linking between `OperationalRequest` IDs and ADR IDs.
- Mechanical prevention of ADR approval if no valid originating request exists.
- Manual tagging is **deprecated**.

### 3.2 Fast-Track ADR Schema

A simplified ADR schema **SHALL** be introduced for low-risk or pilot decisions, while preserving mandatory fields:

**Minimum Required Fields:**

- Purpose
- Scope
- Risk Level
- Kill Switch Definition
- Rollback Strategy

This schema does **not** weaken governance authority.

### 3.3 Adapter Certification

All adapters **SHALL**:

- Be registered and versioned.
- Undergo integrity validation.
- Declare dependency boundaries.
- Support emergency disablement.

---

## 4. Consequences

### Positive

- ✅ Enables proactive system evolution without sacrificing control.
- ✅ Prevents shadow integrations and uncontrolled mutation.
- ✅ Strengthens institutional memory and traceability.
- ✅ Improves auditability and incident recovery posture.
- ✅ Scales safely with agent population growth.

### Tradeoffs

- ⚠️ Slight increase in procedural overhead.
- ⚠️ Requires discipline in schema enforcement and tooling automation.
- ⚠️ Slower execution for high-risk changes **by design**.

**These tradeoffs are accepted as necessary for sovereign stability.**

---

## 5. Compliance & Enforcement

Violations of this ADR **SHALL** be classified as:

- **Architectural Drift**
- **Governance Breach**
- **Security Violation**

Such violations may trigger:

- 🚨 Automated blocking
- 🔒 System lockdown
- 📋 Mandatory remediation review
- 🏛️ Policy escalation

---

## 6. Review Cycle

This ADR **SHALL** be reviewed:

- After **90 days** of operational usage, or
- Upon any **major architectural incident**, or
- Upon policy evolution requiring structural reassessment.

---

## 7. Ratification

**Approved by:** Office of the CEO  
**Authority Level:** Sovereign  
**Binding Level:** Canonical  
**Effective Immediately:** 2026-01-17

---

## 8. Related Documents

- [ADR-PILOT-OPS-05-001](file:///c:/Users/Bakheet/Documents/Projects/ICGL/docs/adrs/ADR-PILOT-OPS-05-001.md) — Pilot Experiment (Superseded)
- [P-OPS-05](file:///c:/Users/Bakheet/Documents/Projects/ICGL/docs/policies/P-OPS-05.md) — Foundational Autonomy Protocol
- [CoordinationOrchestrator](file:///c:/Users/Bakheet/Documents/Projects/ICGL/src/icgl/coordination/orchestrator.py) — Implementation
- [GovernedSlackAdapter](file:///c:/Users/Bakheet/Documents/Projects/ICGL/src/icgl/observability/slack_adapter.py) — Reference Adapter

---

**This document constitutes the constitutional foundation for all agent operations within the ICGL system.**
