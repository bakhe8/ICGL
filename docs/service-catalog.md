# ICGL Service Catalog (Current Snapshot)

## Services
- API (FastAPI)
  - Path: `api/server.py`
  - Default port: 8000 (`API_PORT` env)
  - Dependencies: Python 3.14, Poetry env, SQLite (`data/kb.db`, `data/observability.db`, `data/extended_mind.db`), LanceDB (`data/lancedb/`)
  - Domains: `modules.{kb,memory,policies,hdal,observability,governance,agents,core,utils,git,llm,sentinel}` (المسارات الكانونية؛ تمت إزالة نظائر backend لهذه الدومينات)
  - Run: `API_PORT=8000 poetry run python -m api.server` (أو `uvicorn api.server:app --reload --port 8000`)
- UI Gateway
  - Path: `ui-gateway/main.py` (static + reverse proxy)
  - Default port: 8080 (`GATEWAY_PORT`)
  - Serves: `ui/web/dist`
  - Proxies to API: `http://127.0.0.1:8000` (اضبط `API_PORT` لو لزم)
  - Run: `poetry run python ui-gateway/main.py`
- Frontend apps
  - Web app: `ui/web` (Vite/React)
    - Dev: `npm run dev --prefix ui/web`
    - Build: `npm run build --prefix ui/web`
  - UI components package: `libs/js/ui-components`
    - Lint (tsc --noEmit): `npm run lint --prefix libs/js/ui-components`
    - Build: `npm run build --prefix libs/js/ui-components`

## Agents
- Declared active agents: 33 (كل الوكلاء مسجّلون في الـRegistry).
- Implemented agent classes: 33 (تتضمن Archivist, Documentation, Monitor, Sentinel, Mock للتجارب، إضافةً إلى ArchitectAgent, BuilderAgent, PolicyAgent, GuardianSentinelAgent, RefactoringAgent, TestingAgent, VerificationAgent، وغيرها).
- Registry: `modules/agents/registry.py` (backend يوجّه إلى modules).

## Data Stores
- `data/kb.db` (SQLite) — Knowledge base / ADRs.
- `data/observability.db` (SQLite) — Logs/metrics/traces ledger.
- `data/extended_mind.db` (SQLite) — Graph data for Extended Mind visualization.
- `data/lancedb/` (LanceDB) — Vector memory (`icgl_memory` table).

## Quality Gates (planned/added)
- Pre-commit: `.pre-commit-config.yaml` (ruff, black, isort, prettier, hygiene).
- CI: `.github/workflows/ci.yml` split إلى:
  - Python lint/test
  - Node lint/build لـ `ui/web`
  - node-ui-components (lint/build لحزمة المكوّنات)
  - Python libs packaging check (تثبيت libs/python/*)
