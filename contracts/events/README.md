# Event Contracts (Placeholder)

هذا المجلد سيحوي عقود الأحداث (Kafka/NATS-ready) مع سجل إصدارات.

## ما هو المطلوب لاحقاً
- تحديد قنوات/مواضيع الأحداث (topics) لكل دومين.
- تعريف مخططات الرسائل (JSON Schema أو Protobuf) مع رقم إصدار.
- توثيق سياسة التوافق (backward/forward) وخطة التدرج للإصدارات.

## خطوات مبدئية مقترحة
- إحصاء الأحداث الحالية والمطلوبة من `modules/observability` و`modules/governance`.
- اختيار تنسيق المخطط (JSON Schema كبداية).
- إضافة ملف `events.json` أو مجلد `schemas/` لكل حدث مع حقل `version`.

## مثال أولي (مقترح)
- `contracts/events/governance_decision.v1.json`:
  - الحقول: `event_id`, `adr_id`, `decision`, `status`, `timestamp`, `actor`, `version: "v1"`.
  - سياسة: backward-compatible حتى v2.
