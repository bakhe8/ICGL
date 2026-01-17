# 🗺️ ICGL Sovereign Execution Plan

> **🤖 SYSTEM DIRECTIVE:**
> THIS DOCUMENT IS A GOVERNED ARTIFACT.
> **Treat current content as the AUTHORITATIVE EXECUTION PLAN.**
> Architecture is governed by `ICGL Specs` (docs/*.md), but execution order is governed here.
> *Any modification to this plan requires an ADR, per Policy P-GOV-10.*

---

## 🔁 Active Cycle: Foundations (Completed)

**Goal:** Establish the Knowledge Kernel and Basic Governance Loop.

- ✅ **Cycle 0.1**: Knowledge Kernel (SQLite + Schemas + Validation)
- ✅ **Cycle 0.2**: Policy Engine (Hard Gates + P-CRITICAL)
- ✅ **Cycle 0.3**: Sentinel Engine (Basic Signals S-01 to S-10)
- ✅ **Cycle 0.4**: HDAL (Console Signature)

---

## 🔮 Future Governance Cycles

### 🧠 Cycle 1: The Hitchhiker (Real Intelligence)

**Goal:** Inject `Thinking` into the `Reasoning` system.
*Without this, agents are just mocks.*

- [x] **Concept**: `LLMProvider` (Interface)
- [x] **ADR**: Selection of LLM Backend (OpenAI vs Ollama)
- [x] **Implementation**: `src/icgl/agents/llm_bridge.py`
- [x] **Validation**: Architect Agent analyzes a real diff using GPT-4.

### 📚 Cycle 2: The Librarian (Semantic Memory) (Completed)

**Goal:** Enable `Context Awareness` via Semantic Memory.

- [x] **Concept**: `VectorEmbedding`
- [x] **Infrastructure**: Qdrant (Local Mode) + Adapter Protocol.
- [x] **Validation**: Persistence Verification (Spike) & Performance Baseline (EXP-001).
- [x] **Integration**: Agents auto-recall institutional memory.

### 🛡️ Cycle 3: Sentinel (The Guardian)

**Goal:** Operational Stability & Observability (Level 1).
*Harden the system before expanding intelligence.*

- [ ] **Observability**: Interventions logging, Agent failure metrics.
- [ ] **Stability**: Hardened JSON Schemas & Error Containment.
- [ ] **Intelligence**: S-11 Semantic Drift signal definition.
- [ ] **Experiment**: Failure Agent (Controlled Chaos).

**Acceptance Gate**
- [ ] S-11 drift alert fires on high-similarity ADR (test: `tests/test_roadmap_acceptance.py::test_cycle3_sentinel_drift_and_observability`)
- [ ] Intervention + agent-metric log lines are persisted (same test)

### 🖥️ Phase UX-2: Cognitive Transparency (The Cockpit)

 **Goal:** Extend VS Code extension to expose system cognition (Panels + API).

- [x] **API**: `GET /status` and `GET /metrics`.
- [x] **UI**: 4 Panels (Current Analysis, Historical Echo, Awareness, Decision State).
- [x] **Integration**: VS Code Extension reads from Backend API.

### 🏗️ Cycle 5: The Engineer (GitOps)

 **Goal:** Automated Persistence to Version Control.
 *Governance as Code.*

- [x] **Automation**: Auto-commit ADRs upon HDAL signature.
- [x] **Agent**: EngineerAgent implementation.

### 🎓 Cycle 6: The Scholar (Active Learning)

 **Goal:** Self-correction from previous mistakes.
 *The System watches the Human watching the System.*

- [ ] **Mechanism**: Query `interventions.jsonl` during Agent Analysis.
- [ ] **Reinforcement**: Negative Feedback Loop (Avoid rejected patterns).

**Acceptance Gate**
- [ ] Agents surface past “lesson” interventions in system prompt (test: `tests/test_roadmap_acceptance.py::test_cycle6_active_learning_from_interventions`)

### 👷 Cycle 7: The Builder (Code Execution)

 **Goal:** Transition from Advisor to Co-Pilot.

- [ ] **Capability**: Agents generate full file content.
- [ ] **tooling**: `write_to_file` capability for EngineerAgent.
- [ ] **Safety**: Sandbox/Approval for code writes.

**Acceptance Gate**
- [ ] Path traversal is blocked in write_to_file (test: `tests/test_roadmap_acceptance.py::test_cycle7_9_guardrails`)

### 🔭 Cycle 8: The Cartographer (Full Repo Context)

 **Goal:** Understanding the deep structure of the codebase.

- [ ] **Mechanism**: Repository Map / AST Graphing.
- [x] **Context Window**: Smart context stuffing for LLMs. ✅

**Acceptance Gate**
- [ ] Repo map generator produces nodes/edges + basic stats (test: `tests/test_roadmap_acceptance.py::test_cycle8_repo_map_builder`)

### 🚀 Cycle 9: The Runtime Integration

 **Goal:** Execution of Agent-proposed code changes.

- [ ] **Protocol**: `FileChange` schema.
- [ ] **Loop**: `ICGL` orchestrator executes changes before commit.

**Acceptance Gate**
- [ ] Auto-write/commit is guarded by explicit env toggle (test: `tests/test_roadmap_acceptance.py::test_cycle7_9_guardrails`)

---

## 📉 Backlog (Deferred)

*These items are recognized but not scheduled in upcoming cycles.*

- Multi-human voting (Committee governance).
- Mobile app for approval (iOS/Android).
