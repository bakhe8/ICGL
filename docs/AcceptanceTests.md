# docs/07_acceptance_tests.md
## الهدف
تعريف اختبارات قبول تجعلنا نثق أن النظام يجيب على السؤال الأصلي (تعاون Agents) بدون فوضى.

## Test 1: Multi-Agent Collaboration
- input: ProblemPackage + ADR draft
- expected:
  - 3+ AgentResults structured
  - Synthesis produced
  - No agent writes to KB

## Test 2: Policy Hard Stop
- input: ADR يحاول تغيير Concept
- expected:
  - Policy FAIL CRITICAL
  - Orchestrator stops
  - Requires HDAL path

## Test 3: Sentinel Drift Detection
- input: ADR يستخدم context كسلطة
- expected:
  - Sentinel alert S-05
  - recommended_action = CONTAIN/ESCALATE

## Test 4: Human Sovereign Decision Logging
- input: APPROVE decision
- expected:
  - HumanDecision saved
  - Ledger append-only
  - ADR links human_decision_id

## Test 5: KB Validation
- input: ADR references missing policy id
- expected:
  - validate fails with clear error
