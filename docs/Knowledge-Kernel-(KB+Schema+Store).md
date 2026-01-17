# docs/02_kb.md
## الهدف
إنشاء Knowledge Base كنواة سيادية (Source of Truth) وفق schema واضح:
- Concepts
- Policies
- Sentinel Signals
- ADRs
- Human Decisions
- Learning Logs

## المتطلبات
1) Schema طبقي:
- dataclasses/pydantic (اختر واحدًا)
- IDs ثابتة (string)
- versioning لكل كيان (semver)

2) Storage
- v1: JSON file store داخل `data/` (أو SQLite خيار بديل)
- write operations محصورة في Orchestrator + HDAL
- read operations متاحة للAgents كـ read-only view

3) Validation
- validate on write (رفض أي إدخال غير مطابق)
- تحقق علاقات:
  - ADR.related_policies موجودة
  - ADR.sentinel_signals موجودة
  - HumanDecision.adr_id موجود

4) Seed Data Loader
- تحميل Seeds (concepts/policies) عند الإقلاع
- منع ازدواج IDs

## API مطلوب
- kb.load()
- kb.save()
- kb.get_concept(id)
- kb.list_policies()
- kb.add_adr(adr) (محمي)
- kb.add_human_decision(decision) (محمي)

## معايير القبول
- تشغيل CLI: init-kb -> يكتب KB JSON صالح
- validate-kb -> يمر بدون أخطاء
- كسر علاقة (policy id غير موجود) -> يفشل validation برسالة واضحة
