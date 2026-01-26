# Quick Runbook (Dev)

## Environments
- Python: 3.14 مع Poetry (`poetry install --no-root`) — CI ومحلي متطابقان.
- Node: 20.x مع npm (`cd ui/web && npm ci` مؤقتاً؛ سنوحّد لاحقاً تحت `ui/`).
- Data: SQLite files in `data/` auto-created; LanceDB at `data/lancedb/`.

## Common Commands
- Python lint: `poetry run ruff api shared modules`
- Python tests: `poetry run pytest`
- API dev server: `API_PORT=8000 poetry run python -m api.server`
- UI gateway: `poetry run python ui-gateway/main.py` (serves built assets, port 8080; يتوقع الـAPI على 8000)
- Web app (ui/web):
  - Dev: `npm run dev --prefix ui/web`
  - Lint: `npm run lint -- --max-warnings=0 --prefix ui/web`
  - Build: `npm run build --prefix ui/web`
- UI shared components (`libs/js/ui-components`):
  - Lint (tsc no emit): `npm run lint --prefix libs/js/ui-components`
  - Build: `npm run build --prefix libs/js/ui-components`
  - Test alias: `npm test --prefix libs/js/ui-components` (يشغّل lint)
- توليد مخطط API: `poetry run python - <<'PY'\nimport json, pathlib\nfrom api.server import app\nspec = app.openapi()\npathlib.Path(\"contracts/api\").mkdir(parents=True, exist_ok=True)\npathlib.Path(\"contracts/api/openapi.json\").write_text(json.dumps(spec, indent=2), encoding=\"utf-8\")\nprint(\"wrote contracts/api/openapi.json\")\nPY`
- توليد Types للواجهة (يتطلب openapi-typescript): `npx openapi-typescript contracts/api/openapi.json -o ui/web/app/api/types.ts`
- في CI: Job `api-contracts-types` يولّد المخطط والـtypes ويرفعهما كـ artifact باسم `api-contracts`.
- OTel (تجريبي): ملف `config/otel.yaml` يعرّف مستقبل OTLP وتصدير logging. شغّله مع collector خارجي أو عدّل endpoints حسب البيئة.
- حزم مشتركة: Job `package-publish-dryrun` يبني حزمة npm (`libs/js/ui-components`) ووحدات Python (`libs/python/*`) ويرفع المخرجات كـ artifacts (لا نشر فعلي).

## Pre-commit (local)
- Install hooks: `poetry run pre-commit install`
- Run all hooks: `poetry run pre-commit run --all-files`

## Data Stores
- `data/kb.db`, `data/observability.db`, `data/extended_mind.db` (SQLite)
- `data/lancedb/` (vector memory)
