# Sprint 08 Brainstorming - semantic-model-and-powerbi

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-29 |
| **Author** | GitHub Copilot |
| **Status** | Proposed |
| **Previous Version** | 0.0.0 (new brainstorming artifact) |

## Stage

Superpowers Stage 1 `brainstorming` output for the Sprint 08 Direct Lake
semantic model thin slice (W1.4).

## Traceability

| Field | Value |
| ----- | ----- |
| Slice | `semantic-model-and-powerbi` |
| Parent sprint issue | #66 |
| Planned PR | `s08-semantic-model-thin` |
| Parent sprint document | [sprint-08-data-platform-resources-and-ingestion-pipeline.md](../sprint-08-data-platform-resources-and-ingestion-pipeline.md) |

## Problem

Sprint 08 needs a minimal semantic model so Power BI can validate the
after-ingest result with one thin measure (`Encounter Count`).

## Recommendation

Implement a thin Direct Lake semantic model scoped to `gold.demand_encounter`
with one required measure and deterministic naming, leaving wider measure packs
for W2.

## Acceptance Criteria

1. Semantic model reads from Direct Lake gold table.
2. `Encounter Count` measure returns expected value for W1 data.
3. Model object names and measure names are documented.
4. Scope remains thin; no dashboard/report build in this slice.
