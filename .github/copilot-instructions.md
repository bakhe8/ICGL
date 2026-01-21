# ICGL Copilot Instructions

## Big picture
 ICGL is a governance-first decision system: CLI/API propose ADRs, `ICGL.run_governance_cycle()` enforces hard policy gates, runs Sentinel scans, coordinates multi-agent analysis, requires HDAL human sign-off, and persists outcomes to the Knowledge Base and memory.
 Core orchestration lives in [src/icgl/governance/icgl.py](src/icgl/governance/icgl.py): Policy Gate → Sentinel Scan → Agent Analysis → HDAL Decision → KB/Merkle/Memory update.
 The API layer exposes a singleton engine and runtime integrity checks; key server code lives in [api/main.py](api/main.py) and [src/icgl/api/server.py](src/icgl/api/server.py).

## Key components & boundaries
 Knowledge Base and schema definitions: [src/icgl/kb](src/icgl/kb). Persistence uses SQLite (KB) and logs/merkle stored under `data/logs`.
 Sentinel engine and rules: [src/icgl/sentinel](src/icgl/sentinel). Sentinel performs intent checks and delegates S-12 style LLM analysis.
 Memory: local Qdrant vector store adapter at [src/icgl/memory/qdrant_adapter.py](src/icgl/memory/qdrant_adapter.py). Default memory path `data/qdrant_memory`, embedding dim = 1536.
 Runtime Integrity Guard (RIG): enforced by [src/icgl/core/runtime_guard.py](src/icgl/core/runtime_guard.py). RIG verifies environment, Merkle chain consistency, and Qdrant locks before running governance cycles.

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
 Qdrant is local: avoid concurrent access; RIG implements lock checks and the adapter is at [src/icgl/memory/qdrant_adapter.py](src/icgl/memory/qdrant_adapter.py).

## Integration points
 LLM: `LLMClient` in [src/icgl/llm/client.py](src/icgl/llm/client.py) wraps OpenAI calls. Tests replace/monkeypatch this client.
 Vector DB: `qdrant-client` used via the qdrant adapter. Default storage path `data/qdrant_memory`.
 API & UI: FastAPI server and WebSocket endpoints (`/ws/status`, `/ws/analysis/{adr_id}`) implemented in [src/icgl/api/server.py](src/icgl/api/server.py); web UI assets under `web/` and `chat/`.

## Local services / frontend
- Qdrant (vector DB): `docker-compose.yml` includes a `qdrant` service (image `qdrant/qdrant:latest`) exposing port `6333` and storing data in `./data/qdrant`. Start it with `docker-compose up -d` or `docker-compose -f docker-compose.yml up -d --build`.
- Default Qdrant settings used by the project: HTTP on `6333`, gRPC configured on `6334` inside container; adapter path: `data/qdrant_memory` (see [src/icgl/memory/qdrant_adapter.py](src/icgl/memory/qdrant_adapter.py)).
- Frontend dev: web assets use Vite + Tailwind; `postcss.config.js` is in `web/`. Start the frontend with the VS Code task `npm: dev - web` or by running `npm run dev` in the `web/` directory.

## Quick references (files to inspect)
 Orchestration: [src/icgl/governance/icgl.py](src/icgl/governance/icgl.py)
 Runtime guard: [src/icgl/core/runtime_guard.py](src/icgl/core/runtime_guard.py)
 LLM client: [src/icgl/llm/client.py](src/icgl/llm/client.py)
 KB & schemas: [src/icgl/kb](src/icgl/kb)
 Qdrant adapter: [src/icgl/memory/qdrant_adapter.py](src/icgl/memory/qdrant_adapter.py)
 API entrypoints: [api/main.py](api/main.py) and [src/icgl/api/server.py](src/icgl/api/server.py)
 CLI: [src/icgl/main.py](src/icgl/main.py) and [src/icgl/cli.py](src/icgl/cli.py)

---
If any area above looks incomplete or you'd like more detail (examples of agent patterns, sample test harnesses, or common PR checks), tell me which section to expand.
