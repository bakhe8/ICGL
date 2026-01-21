# ADR-003: Roadmap as a Governed Entity

**Date:** 2026-01-16
**Status:** ACCEPTED
**Decision:** Treat the Product Roadmap as a governed artifact subject to ICGL cycles.

## Context

Usually, a roadmap is a static text file or a backlog in Jira/Trello that changes whimsically based on "business needs" or developer preference. This leads to scope creep and loss of strategic coherence (P-CORE-01).

## Decision

We will treat `docs/roadmap.md` not as a wish list, but as a **Sovereign Execution Plan**.

1. **Concept Definition**: Introduce `RoadmapItem` as a formal concept.
2. **Policy Enforced**: No change to the roadmap without an ADR (P-GOV-10).
3. **Cyclical Execution**: Development will proceed in `ICGL Cycles`, not arbitrary "Sprints".

## Consequences

- **Positive**: Every feature added is traceable to a governance decision.
- **Positive**: "Shadow work" (undocumented features) becomes a policy violation.
- **Negative**: Updating the roadmap requires more friction (ADR required).

## Compliance

- **P-GOV-10**: This ADR formally establishes the policy P-GOV-10.
