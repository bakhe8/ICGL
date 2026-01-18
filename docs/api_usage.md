# ICGL API Quick Guide

## Auth
- If `ICGL_API_KEY` is set, include header `X-ICGL-API-KEY: <value>` on all requests.

## Key Endpoints
- `POST /propose` — body: `{"title": "...", "context": "...", "decision": "...", "human_id": "..."}` → returns `{ "adr_id": "...", "status": "Analysis Triggered" }`
- `GET /analysis/{adr_id}` — returns synthesis, policy report، ونتائج السنتينل إن وُجدت.
- `POST /sign/{adr_id}` — body: `{"action": "APPROVE|REJECT|EXPERIMENT|MODIFY", "rationale": "...", "human_id": "..."}`; blocks إذا كان Policy/Sentinel فيه CRITICAL.
- `GET /dashboard/overview` — ملخص اللجان والطلبات وأحدث ADR موقّع.

## Notes
- حارس الوقت RuntimeGuard مفعّل دائمًا؛ يجب توفر `OPENAI_API_KEY`.
- لتمكين التنفيذ التلقائي بعد التوقيع: `ICGL_ENABLE_AUTO_WRITE=true` (افتراضيًا معطل).
