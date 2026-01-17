# EXP-001: Vector Store Performance Spike

**Date**: 2026-01-16  
**Subject**: Qdrant Performance Baseline (Local Mode)  
**Status**: COMPLETED  

## Context

As part of the Conditional Approval for ADR-004, we must prove that the chosen Vector Engine (Qdrant) meets minimal performance requirements for local development.

## Methodology

- **Infrastructure**: Qdrant Local Mode (File based).
- **Dataset**: 1,000 synthetic vectors (Dimension: 128).
- **Metrics**:
  - Write Latency (Vectors/sec).
  - Search Latency (ms/query).

## Results

| Metric | Result | Target | Status |
| :--- | :--- | :--- | :--- |
| **Write Throughput** | ~2000 vec/s | > 100/s | ✅ PASS |
| **Search Latency** | 0.04 ms | < 50ms | ✅ PASS |

## Impact

These results confirm that Qdrant in Local Mode is sufficiently performant for Cycle 2 and 3 needs.
Persistence survives process restarts (verified in previous spike).

## Decision

Proceed with full adoption for Cycle 3 (Sentinel).
