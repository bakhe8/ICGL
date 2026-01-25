# خطة إعادة الهيكلة (حالة التنفيذ)

## ما أُنجز

- نقل الجذور الخلفية: `api/` أصبحت تحت `backend/api/`، و`backend/` القديمة تحت `backend/services/` مع رفع `scripts/`, `tests/`, `config/` إلى `backend/`.
- نقل الواجهة: `admin/` → `frontend/admin-app/`, `web/` → `frontend/web-app/`, والصفحات الثابتة إلى `frontend/static/`.
- shared-ui: إنشاء `frontend/shared-ui/` (components/hooks/styles/assets/api-types مع .gitkeep و README)، إضافة alias `@shared-ui` في tsconfig & Vite لكلا التطبيقين، وإنشاء تهيئات أساسية في `config/` (`tsconfig.base`, `eslint.config.base`, `tailwind.config.base`) مع توريثها في التطبيقات. نقل الأنماط المتطابقة (`PolicyEditor.css`, `TraceVisualization.css`) و`react.svg` إلى shared-ui وتحديث الاستيرادات.
- shared-ui بأسماء مميزة: نقل مكونات ولوحات الإدارة (Chat, MessageBubble, ThinkingBlock, ChatContainer, ADRFeed, DashboardContainer, MetricsGrid, PolicyEditor, TraceVisualization, NCCIContainer) إلى مسارات مميزة لكل تطبيق: `frontend/shared-ui/admin-app/components/...` و`frontend/shared-ui/web-app/components/admin/...` مع إضافة aliases `@admin-ui` و`@web-ui` وتحديث الاستيرادات. نقل هوكس المحادثة/الويب سوكيت إلى مسارات مميزة (`frontend/shared-ui/admin-app/hooks/*`, `frontend/shared-ui/web-app/hooks/*`) وتحديث الاستيرادات في الصفحات والفهارس.
- shared/python: إنشاء الحزمة `shared/python/` مع `__init__.py` وREADME، ونسخ محتوى `frontend/web-app/src/backend/*` إلى `shared/python/ui-backend` كبداية للمشترك. إضافة نسخ مميزة من الوحدات الخلفية إلى مجلدات مسماة `*_shared` (agents/kb/governance/observability/utils) وتحديث استيرادات `backend/api` و`backend/services` للإشارة إليها؛ إبقاء الأصل مؤقتًا لضمان الاستقرار.
- تسجيل: إضافة `logs/` إلى `.gitignore`.
- تهيئات lint بايثون: إضافة `config/ruff.toml`.

## الهيكل المستهدف (مستمر)

- backend/: `api/`, `services/`, `scripts/`, `tests/`, `config/`
- frontend/: `admin-app/`, `web-app/`, `shared-ui/`, `static/`
- shared/: `python/` (agents, kb, governance, observability, utils, core…)
- config/, docs/, scripts/, logs/

## المهام المتبقية (مرتبة للتنفيذ)

1) **UI مشتركة**: استكمال نقل بقية المكونات/الهوكس/الأنماط/الأصول غير المتطابقة إلى `frontend/shared-ui/` مع تمييز مسارات admin/web، وتحديث الاستيرادات إلى aliases (`@admin-ui`, `@web-ui`) ثم حذف النسخ القديمة.
2) **Python مشتركة**: حذف النسخ الأصلية في `backend/services/*` بعد التحقق من عمل الاستيرادات الجديدة التي تشير إلى `shared/python/*_shared`.
3) **تهيئات إضافية**: تجميع تهيئات Python format/lint الأخرى (black/flake8 إن لزم) في `config/`.
4) **أصول ثابتة**: تقرير دمج أو حذف النسخ بعد نقلها إلى `frontend/web-app/public/landing-static` و`frontend/web-app/public/cockpit-static`.
5) **تحقق نهائي**: إعادة توليد `duplicate-names.md` بعد التنظيف النهائي، وتشغيل lint/build للواجهات وتشغيل API/اختبارات للتأكد من سلامة المسارات.

## ملاحظات تنفيذية

- احتفظت بالنسخ الأصلية أثناء إنشاء shared-ui/shared/python لتجنب فقدان وظائف؛ التنظيف يتطلب خطوة إزالة النسخ بعد تعديل المسارات.
- التهيئات الأساسية موجودة في `config/tsconfig.base.json`, `config/eslint.config.base.js`, `config/tailwind.config.base.js`.
- alias `@shared-ui` مفعّل في tsconfig (app/node) وفي ملفات Vite (`frontend/admin-app/vite.config.ts`, `frontend/web-app/vite.config.ts`).
