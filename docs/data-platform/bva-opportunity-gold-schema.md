# BVA Opportunity Gold projection schema (Sprint 33 WS-D)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | (none — initial) |

One-way analytics projection of the BVA **Opportunity** system-of-record. Cosmos
DB stays the SoR ([`data-platform/bva/opportunity_store.py`](../../data-platform/bva/opportunity_store.py));
the Sprint 33 WS-D notebook
([`data-platform/notebooks/bva/build_gold_bva_opportunity.py`](../../data-platform/notebooks/bva/build_gold_bva_opportunity.py))
reads the container, calls the pure projection
([`data-platform/bva/opportunity_projection.py`](../../data-platform/bva/opportunity_projection.py)),
and writes the two `gold.bva_opportunity*` Delta tables, loaded identically in
SIT and PROD. It implements the WS-D plan
([`docs/superpowers/plans/2026-07-28-sprint-33-bva-agent-ws-d-opportunity-capture.md`](../superpowers/plans/2026-07-28-sprint-33-bva-agent-ws-d-opportunity-capture.md))
and the frozen WS-G0 Opportunity contract
([`docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md`](../superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md) §3).
Traceability: `FR-BVA-004`, `FR-BVA-005`. Naming is snake_case + `gold.` prefix.

## System of record

- **Cosmos DB** account `cosmos-csa-ihzhhpf-sit` (per AGENTS.md §4), database `bva`
  (env `BVA_COSMOS_DATABASE`), container **`opportunities`**, partition key
  **`/hospitalName`**.
- Documents conform to the frozen
  [`bva-opportunity-v1.schema.json`](../../data/synthetic/schema/bva-opportunity-v1.schema.json).
- Deterministic id `opp-<slug(hospitalName)>-0001`: a re-ask about the same
  hospital **updates the same record** and appends to `history[]` — it never
  forks. The store validates every document against the frozen schema before
  upsert.
- **Lifecycle guard:** agents may set `status` up to and including `qualified`;
  advancing to `onboarding`, `won`, or `lost` is **human-only** and refused for
  agent/bot identities (`FR-BVA-004`, ADR-0056 advisory-only posture).

## Projection direction

Cosmos → Gold is **one-way**. The Gold tables are read-only downstream analytics
(Direct Lake); no process writes Opportunity state back from Gold to Cosmos. The
projection is a pure, deterministic, byte-stable flatten — re-running it over the
same documents yields identical rows.

## Gold tables

### `gold.bva_opportunity`

Grain: **one row per Opportunity** (per hospital lineage). Sorted by `id`.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | string | Deterministic Opportunity id (`opp-<slug>-0001`). |
| `hospitalName` | string | Hospital / prospect display name (partition key). |
| `archetype` | string | `acute` \| `rehab` \| `spitex`. |
| `status` | string | Lifecycle stage `new` → `won` / `lost`. |
| `language` | string | `de` \| `en`. |
| `createdAt` | string (ISO-8601) | Record creation timestamp. |
| `createdBy` | string | Identity that first captured the ask. |
| `latestEventAt` | string (ISO-8601) \| null | `at` of the most recent `history` entry. |
| `latestEvent` | string \| null | `event` of the most recent `history` entry. |
| `historyCount` | int | Number of append-only `history` entries. |
| `poVerdict` | string \| null | Product-owner verdict `go` \| `no-go` \| `conditional`. |
| `roiPct` | number \| null | From `bvaResult.metrics.roiPct` (null until first simulate). |
| `paybackMonths` | number \| null | From `bvaResult.metrics.paybackMonths`. |
| `tco3yChf` | number \| null | From `bvaResult.metrics.tco3yChf`. |
| `npvChf` | number \| null | From `bvaResult.metrics.npvChf`. |
| `hasBvaResult` | bool | True when a `bvaResult` snapshot is attached. |

### `gold.bva_opportunity_pipeline`

Grain: **one row per pipeline metric**. Sorted by `metric_id`. Powers the
Backstage opportunity-pipeline view (`FR-BVA-005`).

| `metric_id` | `metric` | Meaning |
| --- | --- | --- |
| `status:<status>` | `status_count` | Count of opportunities in each lifecycle stage (`opportunity_count`). |
| `open` | `open_count` | Count in open stages (`new`, `evaluating`, `qualified`, `onboarding`). |
| `total` | `total_count` | Total opportunities projected. |
| `weighted_roi_pct` | `weighted_roi_pct` | Stage-probability-weighted mean `roiPct` (`value`). |

#### Weighted ROI

Weighted ROI is a stage-probability-weighted mean over opportunities that have
both a numeric `roiPct` and a positive stage weight:

`sum(STAGE_WEIGHTS[status] * roiPct) / sum(STAGE_WEIGHTS[status])`

| Stage | Weight |
| --- | --- |
| `new` | 0.10 |
| `evaluating` | 0.25 |
| `qualified` | 0.50 |
| `onboarding` | 0.80 |
| `won` | 1.00 |
| `disqualified` | 0.00 |
| `lost` | 0.00 |

Records without an ROI, with an unknown status, or in a zero-weight terminal
stage (`disqualified`, `lost`) are excluded from the denominator. The
`weighted_roi_pct` row carries the contributing `opportunity_count`, the
`weight_sum`, and the `stage_weights` map for auditability.

## Relationship to WS-A cost basis

`gold.bva_opportunity` is the **pipeline / capture** projection and is distinct
from the WS-A **cost-basis** star schema
([`bva-cost-gold-schema.md`](bva-cost-gold-schema.md)). An Opportunity's
`bvaResult` snapshot is produced by the WS-B simulation engine (which consumes
the WS-A `bva_baseline_kpi`); WS-D only records and projects that snapshot — it
does not recompute ROI.

## Live load

Publishing these tables to Cosmos + Direct Lake is a `deploy`-ceiling action
gated by `approved-to-apply`; see the gated live-load plan
([`bva-cost-gated-load-plan.md`](bva-cost-gated-load-plan.md)).
