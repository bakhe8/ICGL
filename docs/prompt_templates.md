# Prompt Templates for Fast LLM Execution

Use these cut-paste blocks to give the model crisp goals and outputs. Fill the blanks, keep it short, and include only the files that matter.

## Bugfix
```
You are implementing a fix in the ICGL codebase.
Goal: <describe the bug and expected behavior>.
Scope files: <list key files/paths>.
Acceptance:
- Repro: <how to reproduce>.
- Expected: <what should happen>.
- Tests: add/adjust minimal test to cover the fix.
Output:
- Patch ready to apply.
- Test snippet.
- Note any side-effects.
```

## Feature / Enhancement
```
You are adding a small feature in the ICGL codebase.
Goal: <describe desired behavior>.
Scope files: <list key files/paths>.
Constraints: keep changes minimal and backward compatible.
Acceptance:
- Behavior: <explicit success criteria>.
- Tests: add a focused test (unit/integration) to cover the new path.
Output:
- Patch ready to apply.
- Test snippet.
- Any config/doc updates (brief).
```

## Documentation Update
```
You are improving documentation.
Goal: <topic>.
Scope files: <doc paths>.
Acceptance:
- Clear, concise, actionable.
- No duplicate content.
Output:
- Updated doc content ready to apply.
- If code examples needed, include them.
```

## Performance Pass
```
You are making a targeted perf improvement.
Goal: <describe slowdown and target>.
Scope files: <paths>.
Constraints: preserve behavior; add guardrails for regressions.
Acceptance:
- Metric: <what to improve and by how much, e.g., reduce calls or latency>.
- Tests/bench: add a small benchmark or assertion if feasible.
Output:
- Patch ready to apply with notes on why it’s faster and any trade-offs.
```
