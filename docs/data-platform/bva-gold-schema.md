# BVA Gold star schema (Sprint 15)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | (none — initial) |

Star schema produced by the BVA medallion
([`data-platform/notebooks/bva/`](../../data-platform/notebooks/bva/)) and
consumed by the BVA semantic model (T5) and C-suite reports (T6). Mirrors the
design spec [§5](../superpowers/specs/2026-07-09-sprint-15-bva-design.md).
Naming is snake_case + `gold.` schema prefix (PR #153 reconciliation).

## Facts

### `gold.bva_fact_azure_consumption`

Grain: **resource × meter × day**. Source of all cost/spend KPIs.

| Column | Type | Notes |
| --- | --- | --- |
| `resource_key` | string | FK → `dim_resource` |
| `meter_key` | string | FK → `dim_meter` |
| `date_key` | string `YYYY-MM-DD` | FK → `dim_date` |
| `env_key` | string | FK → `dim_environment` |
| `hospital_key` | string | FK → `dim_hospital` |
| `capability_key` | string | FK → `dim_capability` |
| `effective_cost` | decimal | CHF, effective cost (post-discount) |
| `billed_cost` | decimal | CHF, billed cost |
| `list_cost` | decimal | CHF, list cost |
| `quantity` | decimal | metered quantity |

### `gold.bva_fact_budget`

Grain: **env × capability × month**. Plan baseline for plan-vs-actual variance.

| Column | Type | Notes |
| --- | --- | --- |
| `env_key` | string | FK → `dim_environment` |
| `capability_key` | string | FK → `dim_capability` |
| `month_key` | string `YYYY-MM` | FK → `dim_date` (month grain) |
| `plan_cost` | decimal | mean monthly actual per (env, capability) = stable plan |
| `actual_cost` | decimal | that month's actual |
| `variance_cost` | decimal | `actual_cost − plan_cost` |

### `gold.bva_fact_value_realization`

Grain: **capability × month × hospital**. Value + adoption side of the BVA.

| Column | Type | Notes |
| --- | --- | --- |
| `capability_key` | string | FK → `dim_capability` |
| `month_key` | string `YYYY-MM` | FK → `dim_date` (month grain) |
| `hospital_key` | string | FK → `dim_hospital` |
| `allocated_cost` | decimal | capability-allocated Azure consumption |
| `benefit_realized` | decimal | `allocated_cost × BENEFIT_MULTIPLIER[capability]` (synthetic) |
| `adoption_count` | int | distinct active users (Sprint 12 join, T4) |
| `decision_cycles` | decimal | synthetic decision volume per capability |

> `benefit_realized`, `decision_cycles`, and the `BENEFIT_MULTIPLIER` /
> `DECISION_CYCLES_PER_KCHF` rates are **synthetic** calibration constants
> (documented in `bva_transforms.py`) so every derived KPI stays explainable in a
> board setting. No PHI, no real financials.

## Dimensions

| Dimension | Key | Attributes |
| --- | --- | --- |
| `gold.bva_dim_service` | `service_key` | `service_name`, `service_category` |
| `gold.bva_dim_meter` | `meter_key` | `meter_name`, `meter_category`, `meter_sub_category`, `pricing_unit` |
| `gold.bva_dim_resource` | `resource_key` | `resource_name`, `resource_type`, `region`, `service_key`, `env_key`, `hospital_key`, `capability_key` |
| `gold.bva_dim_environment` | `env_key` | dev / sit / prod |
| `gold.bva_dim_hospital` | `hospital_key` | USZ / LUKS / Zollikerberg / Aggregated |
| `gold.bva_dim_capability` | `capability_key` | BMCA / OOA / DCA / ORSA / SBA / CSA |
| `gold.bva_dim_date` | `date_key` | `month_key`, `year`, `month`, `day` |
| `gold.bva_dim_exec_role` | `exec_role_key` | CEO / CFO / CIO / COO / CTO / BOARD (RLS routing) |

## RLS surface

`hospital_key`, `env_key`, and `exec_role_key` are the row-level-security
predicates (design spec §8). `Aggregated` bypasses the hospital filter;
`HCC.GuestReadOnly` sees `Aggregated` + the Board-summary landing only. RLS is
enforced in the semantic model (T5) — see
[`data-platform/reports/tests/bva-rls-test-plan.md`](../../data-platform/reports/tests/bva-rls-test-plan.md).
