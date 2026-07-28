# BVA cost-basis Gold star schema (Sprint 33 WS-A)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | (none — initial) |

Cost-basis star schema produced by the Sprint 33 WS-A BVA medallion notebook
([`data-platform/notebooks/bva/build_gold_bva_costbasis.py`](../../data-platform/notebooks/bva/build_gold_bva_costbasis.py))
from the git-owned master data in
[`data/master-data/bva/`](../../data/master-data/bva/), loaded identically in
SIT and PROD. It implements the WS-A plan
([`docs/superpowers/plans/2026-07-28-sprint-33-bva-agent-ws-a-cost-data-product.md`](../superpowers/plans/2026-07-28-sprint-33-bva-agent-ws-a-cost-data-product.md))
and the frozen WS-G0 cost-basis contract
([`docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md`](../superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md)).
Traceability: `FR-BVA-001`, `NFR-BVA-002`, `NFR-BVA-003`, and `NFR-BVA-004`.
Naming is snake_case + `gold.` schema prefix.

## Source master data

| File | Grain |
| ---- | ----- |
| [`bva_cost_element.csv`](../../data/master-data/bva/bva_cost_element.csv) | Authoritative ROM ledger: one row per cost element; 5 `one_time` + 4 `annual_run` rows sum to 1,300,000 / 1,250,000 CHF. |
| [`bva_bom.csv`](../../data/master-data/bva/bva_bom.csv) | One row per BOM resource with resource type, group, environment, and resource id. |
| [`bva_azure_cost_weekly.csv`](../../data/master-data/bva/bva_azure_cost_weekly.csv) | Azure drill-down cost by service, resource, and ISO week in USD. |
| [`bva_copilot_usage_weekly.csv`](../../data/master-data/bva/bva_copilot_usage_weekly.csv) | Copilot usage and USD cost by ISO week. |
| [`bva_team_effort.csv`](../../data/master-data/bva/bva_team_effort.csv) | Human elective build effort by role and ISO week in CHF-rate terms. |
| [`bva_fx_rate.csv`](../../data/master-data/bva/bva_fx_rate.csv) | Explicit USD to CHF FX rate by period. |
| [`bva_hospital_profile.csv`](../../data/master-data/bva/bva_hospital_profile.csv) | One row per synthetic hospital tenant with bed count, target occupancy, and archetype. |

## Gold tables

The five `gold.bva_*` tables are split into facts and dimensions below.

## Facts

### `gold.bva_cost_fact`

Grain: **source × ISO week**. CHF-normalized Azure and Copilot cost fact.

| Column | Type | Notes |
| --- | --- | --- |
| `source` | string | `azure` or `copilot`. |
| `iso_week` | string `YYYY-Www` | ISO week of the supporting source cost. |
| `cost_usd` | decimal | Source-week cost before FX conversion. |
| `usd_to_chf` | decimal | Explicit FX rate selected from `bva_fx_rate.csv`. |
| `cost_chf` | decimal | `cost_usd × usd_to_chf`, rounded to 2 decimals. |

CHF normalization for this table goes only via `bva_fx_rate.csv`, as required by
the frozen cost-basis contract §4. No alternate currency or rate fields are
introduced.

### `gold.bva_effort_fact`

Grain: **role × ISO week**. Human elective team effort cost fact.

| Column | Type | Notes |
| --- | --- | --- |
| `role` | string | Team role from `bva_team_effort.csv`. |
| `iso_week` | string `YYYY-Www` | ISO week of the elective effort line. |
| `elective_hours` | decimal | Human elective hours. |
| `role_rate_chf` | decimal | Configured CHF role rate. |
| `team_cost_chf` | decimal | `elective_hours × role_rate_chf`, rounded to 2 decimals. |

### `gold.bva_baseline_kpi`

Grain: **baseline metric**. Reconciled ROM baseline emitted from the
authoritative ledger.

| Column | Type | Notes |
| --- | --- | --- |
| `metric_id` | string | Stable metric id: `annualRunChf`, `costPerBedChf`, `costPerForecastRunChf`, `costPerHospitalChf`, `hospitals`, `oneTimeChf`, or `totalCostChf`. |
| `value` | decimal | Metric value in the unit declared by `unit`. |
| `unit` | string | `CHF` or `count`. |
| `as_of` | string ISO-8601 | Snapshot timestamp, currently `2026-07-28T00:00:00Z`. |
| `source_ref` | string | Provenance string: `docs/BVA.md ROM; data/master-data/bva/bva_cost_element.csv`. |

`oneTimeChf` and `annualRunChf` derive solely from the
[`bva_cost_element.csv`](../../data/master-data/bva/bva_cost_element.csv) ROM
ledger. Weekly cost, effort, and FX files provide drill-down evidence; they are
not the source of the reconciled ROM baseline.

## Dimensions

### `gold.bva_bom_dim`

Grain: **BOM resource**. Dimension for the committed SIT/PROD bill of materials.

| Column | Type | Notes |
| --- | --- | --- |
| `resource_type` | string | Resource type from `bva_bom.csv`. |
| `resource_group` | string | Azure resource group name. |
| `env` | string | Environment marker, for example `sit` or `prod`. |
| `resource_id` | string | Stable resource identifier and sort key. |

### `gold.bva_hospital_profile_dim`

Grain: **hospital tenant**. Dimension for the three synthetic hospitals used by
WS-A and WS-B baseline calculations.

| Column | Type | Notes |
| --- | --- | --- |
| `tenant_id` | string | Synthetic tenant key. |
| `hospital_name` | string | Synthetic hospital name. |
| `beds` | int | Hospital bed count used by cost-per-bed measures. |
| `occupancy_target` | decimal | Target occupancy ratio. |
| `archetype` | string | WS-B archetype driver, for example `acute` or `rehab`. |

## `sm_bva` measure catalog

| Measure | DAX-style definition sketch | Baseline value |
| ------- | --------------------------- | -------------- |
| `Total Cost CHF` | `CALCULATE(SUM(gold.bva_baseline_kpi[value]), metric_id = "totalCostChf")` | `2,550,000` CHF; equals `bva_baseline_kpi.totalCostChf`. |
| `One-Time CHF` | `CALCULATE(SUM(gold.bva_baseline_kpi[value]), metric_id = "oneTimeChf")` | `1,300,000` CHF; equals `bva_baseline_kpi.oneTimeChf`. |
| `Annual Run CHF` | `CALCULATE(SUM(gold.bva_baseline_kpi[value]), metric_id = "annualRunChf")` | `1,250,000` CHF; equals `bva_baseline_kpi.annualRunChf`. |
| `Cost per Hospital CHF` | `CALCULATE(SUM(gold.bva_baseline_kpi[value]), metric_id = "costPerHospitalChf")` | `850,000` CHF; equals `bva_baseline_kpi.costPerHospitalChf`. |
| `Cost per Bed CHF` | `DIVIDE([Total Cost CHF], SUM(gold.bva_hospital_profile_dim[beds]))` | `1,349.21` CHF; equals `bva_baseline_kpi.costPerBedChf`. |
| `Cost per Forecast Run CHF` | `DIVIDE([Annual Run CHF], 24 * 365)` | `142.69` CHF; equals `bva_baseline_kpi.costPerForecastRunChf`. |

Each semantic-model measure value equals the corresponding
`gold.bva_baseline_kpi` row so `sm_bva` and the Gold table agree.

## ROM reconciliation

| Baseline KPI row | `gold.bva_baseline_kpi` value | `docs/BVA.md` ROM value | Result |
| ---------------- | ----------------------------- | ----------------------- | ------ |
| `oneTimeChf` | `1,300,000` CHF | `1,300,000` CHF one-time implementation cost | Exact match |
| `annualRunChf` | `1,250,000` CHF | `1,250,000` CHF recurring annual run cost | Exact match |
| `hospitals` | `3` | `3` hospitals in the WS-A master data and Sprint 33 baseline | Exact match |

This reconciliation lets the WS-B engine
([`data-platform/bva/archetypes.py`](../../data-platform/bva/archetypes.py))
later source its provisional constants from `sm_bva` without changing the frozen
`bva.simulate` contract.

## Relationship to the Sprint 15 BVA product

This cost-basis product (`gold.bva_bom_dim`, `gold.bva_cost_fact`,
`gold.bva_effort_fact`, `gold.bva_hospital_profile_dim`,
`gold.bva_baseline_kpi`, and `sm_bva`) is new and additive. It does not modify
the Sprint 15 BVA consumption/value-realization tables documented in
[`docs/data-platform/bva-gold-schema.md`](bva-gold-schema.md), their
`gold.bva_fact_*` tables, or that semantic model. There is no table or semantic
model name collision.

## Provenance & PHI

All rows are synthetic or anonymized proof-of-technology data. The product
contains no PHI and follows the demo-scope constraints in
[ADR-0013](../adr/0013-temporary-us-region-demo-scope.md) and
[ADR-0016](../adr/0016-no-phi-in-mvp-demo-scope.md). SIT and PROD use the same
git-owned master-data inputs for parity.
