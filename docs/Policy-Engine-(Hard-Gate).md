# docs/03_policy_engine.md
## الهدف
بناء Policy Engine يطبق "Hard Constraints" قبل أي تصويت/تركيب.
لا سياسة = لا مرور.

## المتطلبات
1) Policy Model
- id, code, title, rule, severity, enforced_by

2) Policy Evaluation
- Input: Proposal/ADR draft + context + kb
- Output: PolicyReport:
  - passed_policies[]
  - violated_policies[] (مع تفسير)
  - severity_max
  - decision: PASS | FAIL | ESCALATE

3) Enforcement
- CRITICAL violation => FAIL فوري
- HIGH => ESCALATE للإنسان (حتى لو التصويت إيجابي)
- MED/LOW => يرفق كتوصية

4) Rule Implementation
- rules مكتوبة كدوال واضحة وقابلة للاختبار
- مثال قواعد أساسية:
  - P-ARCH-04 Context Is Not Authority
  - P-ARCH-05 Occurrence Must Be Immutable
  - P-GOV-09 Human Exclusive Concept Authority
  - P-CORE-01 Strategic Optionality Preservation

## معايير القبول
- تمرير ADR-001 (Conditional) مع PASS/ESCALATE حسب محتواه
- كسر P-GOV-09 بمحاولة تغيير concept من غير HDAL => FAIL CRITICAL
- تقرير policy قابل للعرض داخل CLI/UI
