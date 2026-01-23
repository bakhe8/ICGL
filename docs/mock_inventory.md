# Mock/Placeholder Inventory (ICGL)

قائمة مختصرة بالمواضع التي تحتوي على بيانات أو منطق موك/Placeholder، مع الإجراء المقترح.

## الواجهة الأمامية (web)
- `web/src/data/fallbacks.ts`: مجموعات fallback (agents/docs/pattern alerts/system health) تُستخدم في Cockpit/AgentPage/Mind/Security/Operations. → إبقاءها فقط كـ fallback عند غياب البيانات الحية، مع خطة إزالتها بعد ربط الـAPI.
- `web/src/api/queries.ts`:
  - تم تصحيح المسارات إلى نقاط حقيقية (`/health`, `/status`, `/observability/stats`, `/chat`, `/patterns/alerts`).
  - دوال غير مدعومة من الخادم حالياً تُعيد أخطاء صريحة: `runAITerminal`, `writeAIFile`, `runAgent`, `updateProposal`, `createDecision`.
  - `listConflicts` و `createConflict` ما زالت موك (ترجع مجموعة فارغة/كائن موك) حتى يتوفر مسار حقيقي.
- `web/src/routes/AgentsFlowPage/AgentsFlowPage.tsx`: يستخدم `adrId = 'latest'` ثابت مما ينتج 404 إذا لا يوجد ADR فعلي. → يحتاج لاسترداد `/api/analysis/latest` أو مطالبة المستخدم بإنشاء ADR قبل العرض.
- `web/src/routes/*`: بعض الحقول UI placeholders (حقول بحث/إدخال) لا تؤثر على البيانات.

## الواجهة الخلفية (api/backend)
- `api/server.py`:
  - `/api/events` و `/api/idea-summary/{adr_id}` موك صريح.
  - `list_agents` لديه fallback `dummy-agent` عند فشل الإقلاع.
  - لا توجد مسارات لـ: `/api/system/health`, `/api/system/status`, `/api/system/dashboard/quick`, `/api/chat/free_chat`, `/api/chat/terminal`, `/api/chat/file/write`, `/api/governance/proposals/create`, `/api/governance/decisions/register`, `/api/system/agents/{id}/run`, `/api/governance/conflicts`.
- Stubs في البنية:
  - `backend/coordination/__init__.py`, `backend/kb/llm.py`, `backend/observability/broadcaster.py`, `backend/observability/ml_detector.py`, `backend/sentinel/rules.py` (دوال stub مثل `semantic_drift_stub`, `intent_stub`), `backend/observability.py` (no-op stubs).
  - `backend/agents/base.py` يحتوي `mock_response` للسيناريوهات المغلقة.

## الأثر والخطوات التالية
- إضافة أو تمكين المسارات الناقصة في الخادم لتغطية ما تستدعيه الواجهة (terminal/file/runAgent/proposal update/decision register/conflicts)، أو تعديل الواجهة لإخفاء الميزات إلى أن تتوفر.
- استبدال `/api/events` و `/api/idea-summary/{id}` ببيانات حقيقية من سجل المراقبة/KB.
- ضبط `AgentsFlowPage` للعمل على ADR حقيقي (`/api/analysis/latest`) أو إظهار رسالة فارغة أنشئ ADR أولاً.
- إزالة الاعتماد على fallbackAgents/Docs/PatternAlerts/Health تدريجياً بعد التأكد من أن نقاط الـAPI تعيد بيانات حية.
