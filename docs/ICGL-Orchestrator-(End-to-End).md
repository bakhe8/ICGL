# docs/06_icgl_orchestrator.md
## الهدف
تنفيذ ICGL كـ pipeline رسمي:
ADR -> Policy Gate -> Sentinel -> Agents -> Synthesis -> HDAL -> KB Update

## المتطلبات
1) Pipeline Stages
- Draft ADR (أو استلامه)
- Policy Gate
- Agent Run (parallel)
- Sentinel Scan (بعد agents و/أو قبلهم حسب التصميم)
- Synthesis (تجميع توصية واحدة)
- HDAL (قرار بشري)
- KB Update + LearningLog

2) Invariants
- لا write في KB قبل قرار HDAL (إلا تسجيل draft مؤقت)
- CRITICAL policy violation => توقف قبل agents
- CRITICAL sentinel alert => توقف قبل HDAL أو يذهب مباشرة لـ HDAL حسب config

3) Synthesis Output
- Recommendation summary
- Minority opinions
- What could go wrong
- What policies are affected
- Suggested experiment plan إن لزم

## معايير القبول
- تنفيذ دورة كاملة على ADR-001:
  - Policy report
  - Agents report
  - Sentinel report
  - HDAL decision
  - KB updated
- ينتج ملف JSON نهائي للدورة داخل `runs/<run_id>.json`
