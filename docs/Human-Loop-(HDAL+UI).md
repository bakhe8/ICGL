# docs/05_hdal_human_loop.md
## الهدف
تطبيق HDAL: الإنسان هو الحكم النهائي، وكل قرار سيادي يتطلب توقيع بشري.

## المتطلبات
1) Decision Package
- يجمع:
  - ADR draft
  - PolicyReport
  - SentinelReport
  - AgentResults
  - Historical matches (v1 optional)
  - Recommended synthesis

2) Human Actions
- APPROVE | REJECT | MODIFY | EXPERIMENT
- rationale إلزامي (حتى سطر واحد)

3) Signing
- v1: signature_hash placeholder (HMAC local أو string)
- v2: مفاتيح + تشفير
- كل قرار يُسجل في Sovereign Ledger داخل KB

4) UI
- v1: Console UI (prompt في CLI) + JSON output
- v2: VS Code Webview:
  - عرض Decision Package
  - أزرار القرار + rationale
  - يكتب decision في ledger

5) Tamper Resistance (v1)
- ledger append-only
- لا تعديل قرار سابق، فقط قرار جديد

## معايير القبول
- عند تشغيل icgl run:
  - يعرض Decision Package
  - المستخدم يختار APPROVE + rationale
  - ينشئ HumanDecision ويخزنها
- محاولة تغيير concept بدون HDAL => مرفوضة
