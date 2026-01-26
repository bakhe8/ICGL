# API Contracts (WIP)

هدف هذا المجلد الاحتفاظ بعقود الـAPI كـمصدر واحد للحقيقة.

## ما يتم توثيقه هنا
- `openapi.json` يتم توليده من تطبيق FastAPI (`api/server.py` + `api/routers/*`).
- أي نماذج إضافية مشتركة لا توجد في المخطط تلقائياً (إن وجدت).

## كيفية التوليد محليًا
1) تأكد أن بيئة Poetry مفعّلة وأن المتطلبات مثبّتة.
2) من جذر المشروع شغّل:
   ```bash
   poetry run python - <<'PY'
   import json, pathlib
   from api.server import app
   spec = app.openapi()
   pathlib.Path("contracts/api/openapi.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
   print("wrote contracts/api/openapi.json")
   PY
   ```
3) صدّر عملاء حسب الحاجة (مثال: `npx openapi-typescript contracts/api/openapi.json -o ui/web/app/api/types.ts`).

## ملاحظات
- أي تغيير في المسارات أو النماذج يجب أن ينعكس هنا قبل الدمج.
- أبقِ إصدار المخطط متزامناً مع الفرع الرئيسي (ينبغي تحديثه عند كل تغيير API).
