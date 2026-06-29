# Sprint 08 Brainstorming - realtime-capacity-simulator

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-29 |
| **Author** | GitHub Copilot |
| **Status** | Reviewed |
| **Previous Version** | 0.0.0 (new brainstorming artifact) |

## Stage

Superpowers Stage 1 `brainstorming` output for the Sprint 08 real-time
capacity simulator thin slice (W1.5).

## Traceability

| Field | Value |
| ----- | ----- |
| Slice | `realtime-capacity-simulator` |
| Parent sprint issue | #66 |
| Planned PR | `s08-simulator-thin` |
| Parent sprint document | [sprint-08-data-platform-resources-and-ingestion-pipeline.md](../sprint-08-data-platform-resources-and-ingestion-pipeline.md) |

## Problem

Sprint 08 needs a minimal simulator path that emits one contract-compliant
demand event into the bronze streaming path and merges into
`gold.demand_encounter` as `provenance_source='simulator'`.

## Recommendation

Start with a deterministic one-event producer and one-shot kickstart entrypoint,
validated with unit tests and schema invariants; defer multi-scenario generation
to W2.

## Acceptance Criteria

1. Producer emits one valid `DC-DEMAND-ENCOUNTER-v1` envelope.
2. Kickstart entrypoint emits one valid envelope with profile metadata.
3. Gold transform accepts simulator records and preserves residency/purpose tags.
4. Simulator output includes pseudonymized identifiers only and no PHI fields.
