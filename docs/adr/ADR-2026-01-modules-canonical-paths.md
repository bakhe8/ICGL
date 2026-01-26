# ADR: Modules as Canonical Domain Paths

- Status: Accepted
- Date: 2026-01-26
- Context: المسارات القديمة كانت تعتمد على `backend.*` مع تشابك وتكرار. تم نقل الدومينات إلى `modules/*` لتسطيح واستقلالية الدومينات، مع حزم `libs` للحصص المشتركة.
- Decision:
  - `modules/{agents,governance,observability,kb,memory,policies,hdal,core,utils,git,llm,sentinel}` هي المسارات الكانونية.
  - تم حذف نظائر `backend/*` لهذه الدومينات أو إبقاؤها كشيم مؤقتة ثم إزالتها.
  - واجهة العقود: `contracts/api/openapi.json` + `contracts/events/*.json` (رفع artifacts في CI).
  - CI يبني/يلنت ويولّد الـtypes والمخطط ويعبّئ الحزم (dry-run).
- Consequences:
  - استيرادات `backend.*` لهذه الدومينات تعتبر legacy ويجب عدم استخدامها.
  - أي تطوير جديد يجب أن يعتمد على `modules.*`، والحزم المشتركة من `libs/python/*` و`libs/js/ui-components`.
  - الوثائق (runbook/service-catalog) محدّثة لتعكس المسارات الجديدة.
- Rollout:
  - تم تعديل الاستيرادات وتشغيل الاختبارات.
  - CI محدّث للتحقق من الحزم والعقود.
