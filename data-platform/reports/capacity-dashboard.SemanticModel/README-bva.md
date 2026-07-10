# BVA semantic-model additions (Sprint 15 · T5)

Additive Direct Lake tables + KPI measures layered onto the
`capacity-dashboard` semantic model to serve the BVA C-suite reports (T6) and
whiteboard cards (T7). Authored as `bva_`-prefixed files so they never collide
with the operational dimensions edited in parallel (PR #172) and so the BVA Gold
tables never clash with the operational `gold.dim_hospital`.

## Tables (all Direct Lake, schema `gold`, `bva_`-prefixed)

| TMDL table | Gold entity | Role |
| --- | --- | --- |
| `bva_fact_azure_consumption` | `gold.bva_fact_azure_consumption` | resource × meter × day cost |
| `bva_fact_budget` | `gold.bva_fact_budget` | env × capability × month plan/variance |
| `bva_fact_value_realization` | `gold.bva_fact_value_realization` | capability × month × hospital value + adoption |
| `bva_dim_capability` | `gold.bva_dim_capability` | BMCA / OOA / DCA / ORSA / SBA / CSA |
| `bva_dim_environment` | `gold.bva_dim_environment` | dev / sit / prod |
| `bva_dim_hospital` | `gold.bva_dim_hospital` | USZ / LUKS / Zollikerberg / Aggregated |
| `bva_dim_date` | `gold.bva_dim_date` | day grain (+ `month_key`) |
| `bva_dim_exec_role` | `gold.bva_dim_exec_role` | CEO / CFO / CIO / COO / CTO / BOARD (RLS routing) |
| `bva_measures` | *(calculated holder)* | the KPI catalogue |

Star relationships wire the three facts to the shared dimensions on
`capability_key`, `env_key`, `hospital_key`, and `date_key` (facts on a day
grain). Monthly facts (`bva_fact_budget`, `bva_fact_value_realization`) are not
related to the day-grained `bva_dim_date` to avoid a many-to-many join; their
time context is `month_key`.

## KPI catalogue

All 28 measures live on `bva_measures.tmdl` and **mirror**
[`data-platform/notebooks/bva/bva_kpi.py`](../../../notebooks/bva/bva_kpi.py)
one-for-one. The DAX↔Python mapping and the synthetic target constants
(`TARGET_ANNUAL_BENEFIT_CHF = 1 200 000`, `TARGET_ACTIVE_USERS = 120`, …) are
catalogued in [`docs/adr/0025-bva-kpi-catalog.md`](../../../../docs/adr/0025-bva-kpi-catalog.md).

Because the sandbox cannot evaluate DAX, the KPI **semantics** are validated by
golden tests against the reference module:

```bash
python3 -m unittest discover -s data-platform/reports/tests -v
```

## RLS

Row-level security (exec-role, hospital, and guest-aggregated) is authored in
`definition/roles/Bva*.tmdl` (T6) and verified per
[`data-platform/reports/tests/bva-rls-test-plan.md`](../../tests/bva-rls-test-plan.md).

## Publish (gated)

Publishing the model to `ws-ihzhhpf-sit-data` is a `deploy`-ceiling action gated
by `approved-to-apply` (AGENTS.md §4). The publish itself is done by the human
operator via Fabric deployment tooling after the plan is approved on the PR; no
autonomous publish is wired into CI.
