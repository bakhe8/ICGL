
# ICGL Copilot Instructions

## System Overview
ICGL is a governance-first, agentic decision system. The core workflow is:
1. CLI/API proposes ADRs
2. `ICGL.run_governance_cycle()` enforces policy gates, runs Sentinel scans, coordinates multi-agent analysis, requires HDAL human sign-off, and persists outcomes to the Knowledge Base (KB) and memory.
3. All decisions are Merkle-backed for auditability.

**Key Orchestration:** [src/icgl/governance/icgl.py](src/icgl/governance/icgl.py)

## System Evolution Plan
**Phase 1: Runtime Validation**
- Start Uvicorn server
- Verify `/health`, `/api/system/stats`, `/observability/traces`

**Phase 2: Core Functionality**
- Implement `resolve_targets_from_text` in `server.py`
- Implement `load_path_map` for project-wide file resolution
- Enrich `get_icgl` with dynamic capability discovery

**Phase 3: Agentic Integration**
- Enhance `shared.python.agents_shared.engineer` logic
- Connect `run_terminal` and `write_file` to governance gates
- Implement multi-agent feedback loops for analysis

**Phase 4: Frontend Synchronization**
- Verify dashboard compatibility with new type schemas
- Update UI for rich message block rendering
- Test real-time WebSocket updates for analysis

**Phase 5: Finalization & Documentation**
- Run full regression suite
- Update all architectural ADRs
- Final handover walkthrough and system state report

## Agent Registry & Patterns
All agents and their capabilities are tracked in the [Agent Registry](modules/agents/AGENTS.md). Avoid duplicate agents and feature overlap. Key agent types:
- **ArchitectAgent**: Structural/design analysis
- **PolicyAgent**: Policy compliance
- **FailureAgent**: Failure mode detection
- **GuardianSentinelAgent**: Risk/health monitoring
- **BuilderAgent**: Code generation (AST-based, retry logic)
- **EngineerAgent**: Code deployment, GitOps
- **MediatorAgent**: Multi-agent coordination
- **KnowledgeStewardAgent**: Docs, ADR lifecycle

See [modules/agents/AGENTS.md](modules/agents/AGENTS.md) for full list and responsibilities.

## Developer Workflows
- **Bootstrap:** `scripts/bootstrap.sh` (or VS Code task `Bootstrap dev`)
- **Install:** `pip install -e .` (see [pyproject.toml](pyproject.toml))
- **Run API:** `python -m api.main` (task: "Run API")
- **CLI:** `icgl` (see [src/icgl/cli.py](src/icgl/cli.py)), e.g. `icgl kb stats`, `icgl icgl run`, `icgl runtime repair`
- **Test:** `pytest -q` (tests use LLM stubs, see [tests/conftest.py](tests/conftest.py))

## Project Conventions
- `.env` at repo root is loaded early; real runs require `OPENAI_API_KEY` and secrets
- No silent LLM fallback: governance mode requires valid OpenAI key
- Merkle/logs must be consistent; repair with `icgl runtime repair` if needed
- LanceDB is local: `data/lancedb` (see [src/icgl/memory/lancedb_adapter.py](src/icgl/memory/lancedb_adapter.py))

## Integration Points
- **LLM:** [src/icgl/llm/client.py](src/icgl/llm/client.py) wraps OpenAI
- **Vector DB:** LanceDB via [src/icgl/memory/lancedb_adapter.py](src/icgl/memory/lancedb_adapter.py)
- **API/UI:** FastAPI server ([api/main.py](api/main.py), [src/icgl/api/server.py](src/icgl/api/server.py)), WebSocket endpoints `/ws/status`, `/ws/analysis/{adr_id}`
- **Frontend:** Vite + Tailwind in `ui/web/`, start with `npm: dev - web` task or `npm run dev` in `ui/web/`

## Key Files & Directories
- Orchestration: [src/icgl/governance/icgl.py](src/icgl/governance/icgl.py)
- Runtime guard: [src/icgl/core/runtime_guard.py](src/icgl/core/runtime_guard.py)
- LLM client: [src/icgl/llm/client.py](src/icgl/llm/client.py)
- KB & schemas: [src/icgl/kb](src/icgl/kb)
- LanceDB adapter: [src/icgl/memory/lancedb_adapter.py](src/icgl/memory/lancedb_adapter.py)
- API entrypoints: [api/main.py](api/main.py), [src/icgl/api/server.py](src/icgl/api/server.py)
- CLI: [src/icgl/main.py](src/icgl/main.py), [src/icgl/cli.py](src/icgl/cli.py)
- Agent registry: [modules/agents/AGENTS.md](modules/agents/AGENTS.md)

---
If any area above is unclear or needs more detail (e.g. agent patterns, test harnesses, PR checks), specify which section to expand.
