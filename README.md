# 🏛️ ICGL — Iterative Co-Governance Loop

### A Governance‑First Intelligence System for Long‑Lived Decisions

**ICGL** is not a chatbot, not a copilot, and not an automation tool. It is a governed reasoning system that transforms complex decisions into auditable, traceable, and human‑sovereign outcomes.

---

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Run CLI
icgl --help

# Register governed procedures / requests
icgl ops add-procedure
icgl ops add-request

# Render LLM prompt (bugfix/feature/docs/perf)
python scripts/prompt_helper.py bugfix --goal "Fix X" --files "src/..." --repro "steps" --expected "result"

# Uptime check with optional alert
python scripts/uptime_check.py --url http://127.0.0.1:8000/dashboard/overview

# Run smoke tests
scripts/run_smoke_tests.ps1

# View Knowledge Base stats
icgl kb stats

# Run ICGL governance cycle
icgl icgl run

# Runtime guard
# - RIG enforces real Qdrant/local persistence. Use `icgl runtime repair` if startup aborts.
```

---

## 🧭 What Is ICGL?

ICGL is a **Decision Governance Engine** that:

1. Accepts proposals and architectural decisions
2. Processes through policies, Sentinel, and multi-agent analysis
3. Requires explicit human approval
4. Records outcomes as institutional knowledge

---

## 🧩 Core Architecture

| Component | Description |
|-----------|-------------|
| **Knowledge Base** | Canonical source of truth (Concepts, Policies, ADRs) |
| **ICGL Orchestrator** | Governance cycle engine |
| **Sentinel** | Risk detection and drift prevention |
| **HDAL** | Human Decision Authority Layer |
| **Validator** | Schema validation |

---

## 📁 Package Structure

```
src/icgl/
├── kb/           # Knowledge Base (schemas, storage)
├── governance/   # ICGL orchestrator
├── sentinel/     # Risk detection
├── hdal/         # Human authority layer
├── cli.py        # Command-line interface
└── validator.py  # Schema validation
```

---

## 📖 Documentation

- [Manifesto](docs/manifesto.md) — Identity, philosophy, and goals
- [Knowledge Base](docs/icgl_knowledge_base_v1.md) — Canonical schemas
- [API Quick Guide](docs/api_usage.md) — propose/analysis/sign, auth headers
- [Prompt Templates](docs/prompt_templates.md) — ready-to-paste LLM prompts

---

> **"ICGL exists to make systems honest with themselves — before reality forces them to be."**
