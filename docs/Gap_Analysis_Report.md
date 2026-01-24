
# Engineering Review: Target Topology vs. State of Reality (Phase 11)

## 🏗️ Architect Agent Review

**Status**: "Structurally Validated with Minor Deviations"

* **Observation**: The `Target_Topology.md` defines `EVAL` (Sovereign Evaluator Gate) as a central node between `VERIFY` and `SIGN`.
* **Gap 1 (Evaluator Hook)**: In `server.py`, the `metrics` (Purpose Score) are currently calculated *after* synthesis in `active_synthesis`, but the strict "Gate" mechanism that *blocks* `SIGN` based on the score is implicit, not explicit. We rely on `PolicyAgent` rejection, but a dedicated `EvaluatorNode` in code doesn't strictly exist as a standalone class.
* **Gap 2 (Nexus Bridge)**: `NEXUS` (Catalyst) exists in `registry.py` but the `Nexus Gateway` logic in `server.py` is minimal. It's an endpoint `/api/nexus/propose` but not a full "Gateway" class.

## 🛡️ Guardian Sentinel Review

**Status**: "Security & Integrity High, Observability Medium"

* **Observation**: The diagram links `OBS` (Observability) directly to `EVAL`.
* **Gap 3 (KPI Store Persistence)**: We have `active_synthesis` (in-memory) feeding the Cockpit. We do NOT have a persistent time-series database for `KPIs`. If the server restarts, the "Purpose Score History" is lost. The `OBS` node in code is transient.
* **Gap 4 (Budget Manager)**: `Budgeting` exists in `registry.py` as a fail-safe check (`ICGL_TOKEN_BUDGET`). This ALIGNS with the topology's "Governance" layer, but isn't explicitly drawn as a "Budget Node" in the diagram. It's technically covered by `ORCH` attributes.

## 🏛️ Knowledge Steward Review

**Status**: "Memory Kernel Active, Schema Partial"

* **Observation**: `MEM` is defined as "Institutional Memory Kernel (ADRs, Invariants)".
* **Gap 5 (Schema Completeness)**: We successfully migrated ADRs to `backend/kb/kernel/*.json`. However, the *Invariants* and *Lessons* mentioned in the topology are still largely partially structured or residing in `knowledge_base.py` bootstrap code, not fully graph-linked in the Kernel JSONs yet (though `policies` field was added).
* **Reality**: The `Memory Logic Kernel` is operational for ADRs, but "Lessons" (Learning Log) are still a separate list in `knowledge_base.py`.

---

# Action Plan: Closing the Gaps (Phase 10/11 Cleanup)

| Missing Element | Topology Node | Gap Description | Action Item |
| :--- | :--- | :--- | :--- |
| **Sovereign Evaluator Hook** | `EVAL` | Logic exists scattered in `server.py` & `PolicyAgent`. Needs a unifying `evaluate_sovereign_intent()` function. | **Refactor**: Abstract `Purpose Gate` logic into a method in `Orchestrator`. |
| **KPI Store** | `OBS` -> `EVAL` | Metrics are in-memory (`active_synthesis`). No long-term trend analysis possible. | **Persistence**: Save `metrics` payload to `data/observability.db` or `stats.json`. |
| **Memory Kernel Schema** | `MEM` | ADRs are JSON, but 'Lessons' & 'Invariants' are not fully distinct Kernel objects yet. | **Schema Upgrade**: Define `Lesson` and `Invariant` JSON schemas in `backend/kb/schemas.py`. |
| **Budget Manager** | `ORCH` | Budget check is an `if` statement in Registry. | **Formalize**: Create `BudgetManager` class to track tokens across sessions. |
