# docs/01_runtime.md
## الهدف
بناء Runtime يشغل عدة Agents بطريقة منضبطة (Governed) داخل ICGL، مع:
- توحيد الإدخال/الإخراج لكل Agent
- تشغيل متوازي أو تسلسلي
- جمع النتائج + metadata
- منع تجاوزات (لا تعديل KB مباشرة من Agents)

## المتطلبات
1) Agent Interface موحد:
- input: ProblemPackage + KnowledgeBase (read-only view) + PolicySnapshot
- output: AgentResult (structured)

2) Registry:
- تسجيل agents بأسماء ثابتة + إصدار
- إمكانية تفعيل/تعطيل agent

3) Execution:
- دعم asyncio للتشغيل المتوازي
- timeouts لكل agent
- ميزانية tokens/وقت (على الأقل placeholders)

4) Contracts
- Agents لا يكتبون في KB.
- Agents لا يغيّرون Concepts/Policies.
- أي اقتراح تغيير = "Recommendation" فقط.

## النماذج (Models)
- ProblemPackage:
  - id, title, description
  - inputs (paths, diffs, snippets)
  - requested_decision_type (ARCH | POLICY | CONCEPT | OTHER)
  - constraints

- AgentResult:
  - agent_id, agent_version
  - claims[] (structured)
  - risks[] (structured)
  - confidence (0..1)
  - recommended_actions[]
  - references[] (paths/ids داخل المشروع)

## مخرجات التنفيذ
- AgentRunReport:
  - run_id
  - start/end
  - results[]
  - failures[] (timeout/errors)

## معايير القبول
- تشغيل 3 Agents على مشكلة dummy ويُنتج JSON report متسق.
- أي Agent crash لا يسقط الدورة كاملة (يسجل failure فقط).
- نتائج كل Agent تكون structured وليست نص حر فقط.
