# docs/04_sentinel.md
## الهدف
بناء Sentinel يراقب الانحراف والمجهول والتسرب السلطوي ويُنتج Alerts قابلة للتنفيذ.

## المتطلبات
1) Sentinel Signals Registry
- signal id, name, category, detection_hint, default_action

2) Rule Engine
- Input: ADR/Proposal + AgentResults + PolicyReport + kb snapshot
- Output: SentinelReport:
  - alerts[] (id, severity, reason, evidence)
  - recommended_action: ALLOW | CONTAIN | ESCALATE

3) Minimum Signals (v1)
- S-01 Semantic Drift Risk
- S-05 Authority Leakage Risk
- S-07 Dual Write Hazard
- S-08 Conceptual Drift due to Memory Compression
- S-09 Over-Containment Risk
- S-10 Silent Policy Erosion

4) Containment
- إذا ALERT severity=CRITICAL => يوقف Orchestrator ويطلب HDAL
- يسجل Incident في KB (اختياري v1) أو في log

5) Self-Monitor
- sentinel يجب أن يسجل معدل المنع/التصعيد لتجنب Overblocking (S-09)

## معايير القبول
- سيناريو: ADR بلا policies => Sentinel يرفع alert + ESCALATE
- سيناريو: محاولة اشتقاق status من context => alert Authority Leakage
- تقرير Sentinel يظهر evidence واضح (السبب + أين)
