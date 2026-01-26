# ICGL Copilot Instructions

## Big picture
 ICGL is a governance-first decision system: CLI/API propose ADRs, `ICGL.run_governance_cycle()` enforces hard policy gates, runs Sentinel scans, coordinates multi-agent analysis, requires HDAL human sign-off, and persists outcomes to the Knowledge Base and memory.
 Core orchestration lives in [src/icgl/governance/icgl.py](src/icgl/governance/icgl.py): Policy Gate → Sentinel Scan → Agent Analysis → HDAL Decision → KB/Merkle/Memory update.
 The API layer exposes a singleton engine and runtime integrity checks; key server code lives in [api/main.py](api/main.py) and [src/icgl/api/server.py](src/icgl/api/server.py).

## Key components & boundaries
 Knowledge Base and schema definitions: [src/icgl/kb](src/icgl/kb). Persistence uses SQLite (KB) and logs/merkle stored under `data/logs`.
 Sentinel engine and rules: [src/icgl/sentinel](src/icgl/sentinel). Sentinel performs intent checks and delegates S-12 style LLM analysis.
 Memory: local LanceDB vector store adapter at [src/icgl/memory/lancedb_adapter.py](src/icgl/memory/lancedb_adapter.py). Default memory path `data/lancedb`, embedding dim = 1536.
 Runtime Integrity Guard (RIG): enforced by [src/icgl/core/runtime_guard.py](src/icgl/core/runtime_guard.py). RIG verifies environment, Merkle chain consistency, and LanceDB backend before running governance cycles.

## Developer workflows
 Install editable package: `pip install -e .` (see [pyproject.toml](pyproject.toml)).
 Bootstrap dev: `scripts/bootstrap.sh` (make executable then run). Also available as VS Code task `Bootstrap dev`.
 Run API (developer): `python -m api.main` (task: "Run API"). Server can also be invoked via `python -m icgl.api.server` depending on context.
 CLI entrypoint: `icgl` (implemented in [src/icgl/main.py](src/icgl/main.py) and [src/icgl/cli.py](src/icgl/cli.py)). Common commands: `icgl kb stats`, `icgl icgl run`, `icgl runtime repair`.
 Tests: `pytest -q`. Tests rely on fixtures that stub LLM calls and manipulate RIG state ([tests/conftest.py](tests/conftest.py)).

## Project-specific conventions
 Environment: `.env` at repo root is loaded early; real runs require `OPENAI_API_KEY` and other secrets. See [src/icgl/cli.py](src/icgl/cli.py) and [src/icgl/llm/client.py](src/icgl/llm/client.py).
 No silent LLM fallback: in governance mode the system expects a valid `OPENAI_API_KEY`; tests monkeypatch the LLM client rather than allowing a noop.
 Merkle-backed decisions: authoritative history is required. If Merkle/logs are inconsistent RIG refuses to proceed until `icgl runtime repair` is run.
 LanceDB is local: data is stored in `data/lancedb`. The adapter is at [src/icgl/memory/lancedb_adapter.py](src/icgl/memory/lancedb_adapter.py).

## Integration points
 LLM: `LLMClient` in [src/icgl/llm/client.py](src/icgl/llm/client.py) wraps OpenAI calls. Tests replace/monkeypatch this client.
 Vector DB: LanceDB used via the lancedb adapter. Default storage path `data/lancedb`.
API & UI: FastAPI server and WebSocket endpoints (`/ws/status`, `/ws/analysis/{adr_id}`) implemented in [src/icgl/api/server.py](src/icgl/api/server.py); web UI assets under `ui/web/` and `chat/`.

## Local services / frontend
- Memory: LanceDB is used embedded, no separate service required.
- Default LanceDB setting: stored under `data/lancedb`.
- Frontend dev: web assets use Vite + Tailwind; `postcss.config.js` is in `ui/web/`. Start the frontend with the VS Code task `npm: dev - web` or by running `npm run dev` في مسار `ui/web/`.

## Quick references (files to inspect)
 Orchestration: [src/icgl/governance/icgl.py](src/icgl/governance/icgl.py)
 Runtime guard: [src/icgl/core/runtime_guard.py](src/icgl/core/runtime_guard.py)
 LLM client: [src/icgl/llm/client.py](src/icgl/llm/client.py)
 KB & schemas: [src/icgl/kb](src/icgl/kb)
 LanceDB adapter: [src/icgl/memory/lancedb_adapter.py](src/icgl/memory/lancedb_adapter.py)
 API entrypoints: [api/main.py](api/main.py) and [src/icgl/api/server.py](src/icgl/api/server.py)
 CLI: [src/icgl/main.py](src/icgl/main.py) and [src/icgl/cli.py](src/icgl/cli.py)

---
If any area above looks incomplete or you'd like more detail (examples of agent patterns, sample test harnesses, or common PR checks), tell me which section to expand.
