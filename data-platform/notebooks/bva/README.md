# BVA medallion (Sprint 15 · T3–T4)

Fabric notebooks that transform the synthetic FOCUS-shaped consumption seed
(T1/T2) and Sprint 12 adoption telemetry into the BVA Gold star schema consumed
by the semantic model (T5) and C-suite reports (T6).

- Design contract: [`docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md`](../../../docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md) §3–§5.
- Gold star schema: [`docs/data-platform/bva-gold-schema.md`](../../../docs/data-platform/bva-gold-schema.md).

## Layers

| Notebook | Layer | Writes |
| --- | --- | --- |
| `ingest_bronze_consumption.py` | Bronze | `bronze.bva_consumption` (raw FOCUS rows from `Files/Bronze/consumption/`) |
| `ingest_bronze_adoption.py` | Bronze | `bronze.bva_adoption` (Sprint 12 sign-ins / synthetic backfill from `Files/Bronze/adoption/`) |
| `build_silver_bva.py` | Silver | `silver.bva_consumption` (keys + `date_key`/`month_key` + provenance) |
| `build_gold_bva_dims.py` | Gold | `gold.bva_dim_{service,meter,resource,environment,hospital,capability,date,exec_role}` |
| `build_gold_bva_facts.py` | Gold | `gold.bva_fact_{azure_consumption,budget,value_realization}` |

Naming is snake_case + `gold.` schema prefix (per PR #153 reconciliation).

## Single tested implementation

The transform logic lives in the pure, framework-agnostic
[`bva_transforms.py`](bva_transforms.py) (no PySpark, no I/O) so it is
unit-testable with byte-stable fixtures — the same convention as the evidence
medallion's `readiness_rules.py`. The notebooks read the Delta/Files sources,
`collect()` the synthetic rows (~12k) to the driver, apply the pure functions,
and write the Gold tables. For the synthetic-seed scale this keeps **one** tested
implementation with no notebook/reference drift.

## Adoption join (T4)

`build_gold_bva_facts.py` joins Sprint 12 adoption telemetry into
`gold.bva_fact_value_realization`:

- `adoption_index_from_signins` counts **distinct successful** sign-ins per
  `(capability, month, hospital)`, mapping `appRole → capability` via
  `DEFAULT_ROLE_CAPABILITY` (governance/admin roles are excluded) and
  `upn → hospital` via the persona dimension.
- When real Sprint 12 emission has not yet landed, use the documented **30-day
  synthetic backfill** (`data-platform/scripts/adoption_seed_synthetic.py`,
  design spec §14) and record the switchover point in the PR.

## Tests

```bash
python3 -m unittest discover -s data-platform/notebooks/bva/tests -v
```

Covers Silver normalisation + provenance, all eight dimensions, the three facts
(cost conservation, budget variance, value realization), and the adoption join
(success filter, role mapping, distinct-user counting, hospital attribution).

## Publish (gated)

Publishing the notebooks + wiring the daily Fabric pipeline is a `deploy`-ceiling
action gated by `approved-to-apply` (AGENTS.md §4):

```bash
# plan only (safe)
python3 data-platform/scripts/bva/deploy_pipeline.py --dry-run

# gated live publish (after an approved-to-apply comment on the PR/issue)
python3 data-platform/scripts/bva/deploy_pipeline.py --approved-to-apply <handle>
```

After the publish, record the pipeline item id as the `FABRIC_BVA_PIPELINE_ID`
repo variable (consumed by `.github/workflows/bva-sim-refresh.yml`).
