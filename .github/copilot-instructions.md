# ICGL Copilot Instructions

## Big picture
- ICGL is a governance-first decision system: CLI/API propose ADRs, then `ICGL.run_governance_cycle()` enforces policies, runs Sentinel + multi-agent synthesis, requires HDAL human sign-off, and persists outcomes to the Knowledge Base and memory.
- Core flow is in [src/icgl/governance/icgl.py](src/icgl/governance/icgl.py): Policy Gate → Sentinel Scan → Agent Analysis → HDAL Decision → KB/Merkle/Memory update.
- The API server creates a singleton engine with runtime integrity checks and serves UI/websockets; see [src/icgl/api/server.py](src/icgl/api/server.py).

## Key components & boundaries
- Knowledge Base and schemas live in [src/icgl/kb](src/icgl/kb) with persistence via SQLite and runtime logs under data/.
- Sentinel rules + intent checks are in [src/icgl/sentinel](src/icgl/sentinel); it calls the LLM for S-12 intent analysis.
- Memory is a local Qdrant vector store via [src/icgl/memory/qdrant_adapter.py](src/icgl/memory/qdrant_adapter.py); default path is data/qdrant_memory and embeddings are 1536 dims.
- Runtime Integrity Guard (RIG) is mandatory in CLI/API; it enforces OPENAI_API_KEY, Qdrant locks, and Merkle integrity. See [src/icgl/core/runtime_guard.py](src/icgl/core/runtime_guard.py).

## Developer workflows
- Install (editable): `pip install -e .` (see [pyproject.toml](pyproject.toml)).
- CLI entrypoint: `icgl` from [src/icgl/main.py](src/icgl/main.py) + [src/icgl/cli.py](src/icgl/cli.py). Useful commands: `icgl kb stats`, `icgl icgl run`, `icgl runtime repair`.
- API server: `python -m icgl.api.server` (uses FastAPI + websockets; UI served from src/icgl/ui).
- Tests: `pytest` (fixtures in [tests/conftest.py](tests/conftest.py) stub LLM and force RIG repair/check). API flow tests use FastAPI `TestClient` in [tests/test_api_flow.py](tests/test_api_flow.py).

## Project-specific conventions
- Environment loading is explicit and early in CLI and LLM client; `.env` at repo root is required for real runs ([src/icgl/cli.py](src/icgl/cli.py), [src/icgl/llm/client.py](src/icgl/llm/client.py)).
- No mock fallback is allowed for governance mode; LLM calls raise if `OPENAI_API_KEY` is missing (tests monkeypatch stubs instead).
- Decisions are recorded to a Merkle chain in data/logs; RIG will refuse to run if the chain is inconsistent until `icgl runtime repair` is executed.

## Integration points
- External services: OpenAI API via `LLMClient`, Qdrant local storage via `qdrant-client`.
- Web UI communicates through `/ws/status` and `/ws/analysis/{adr_id}` websockets (see [src/icgl/api/server.py](src/icgl/api/server.py)).
