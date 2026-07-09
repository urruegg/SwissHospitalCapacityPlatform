# BVA synthetic FOCUS-shaped generator (Sprint 15 · T1)

`bva_synth_focus.py` generates the **synthetic seed** for the Sprint 15 BVA
(Business Value Assessment) Evidence data product. It emits a deterministic,
daily-partitioned dataset that mirrors the FinOps **FOCUS** export shape for
Azure consumption, calibrated to the BVA ROM baseline (~CHF 760k/yr Azure spend
per [`docs/BVA.md`](../../docs/BVA.md) v1.0.1).

- Design contract: [`docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md`](../../docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md) §4.
- Implementation plan: [`docs/superpowers/plans/2026-07-09-sprint-15-bva-plan.md`](../../docs/superpowers/plans/2026-07-09-sprint-15-bva-plan.md) Task 1.

## Why synthetic

Per the design spec, the BVA data product runs on **synthetic** consumption data
(Option A). The dataset is FOCUS-shaped so a future PR can swap the Bronze loader
source (real Azure Cost Management / FOCUS export) with one config change without
touching downstream medallion, semantic-model, or report layers.

## Invocation

Run directly (no packaging required, matching the other scripts in this folder):

```bash
cd data-platform/scripts
python3 bva_synth_focus.py --seed 42 --days 90 --out-dir /tmp/bva
```

| Argument | Default | Purpose |
| --- | --- | --- |
| `--seed` | `42` | RNG seed. Same seed → byte-identical output (reproducible demo). |
| `--days` | `90` | Number of daily partitions to generate. |
| `--out-dir` | *(none)* | Output directory. Omit for a dry run (generate + validate in memory only). |
| `--format` | `auto` | `auto` uses Parquet when `pyarrow` is installed, otherwise `jsonl`. Force with `parquet`, `jsonl`, or `csv`. |
| `--end-date` | yesterday (UTC) | Last (most recent) partition date `YYYY-MM-DD`. The 90-day window rolls forward on nightly refresh. |

Output layout (Hive-style partitions consumed by the Fabric Bronze loader in T3):

```text
<out-dir>/BillingPeriod=YYYY-MM/ChargePeriodStart=YYYY-MM-DD/part-00000.<ext>
```

Exit codes: `0` success, `1` FOCUS-shape validation failed, `2` cost calibration
outside ±15% of the ROM baseline.

## Dependencies

The generator core (row generation, FOCUS-shape validation, calibration) is
**dependency-free** (Python 3 standard library only), so the unit tests run
identically in CI and locally. Parquet output additionally requires
[`pyarrow`](https://arrow.apache.org/docs/python/); when it is not installed the
generator transparently falls back to `jsonl`.

## Data model

- **FOCUS columns** (design spec §4): `ChargeType`, `ServiceCategory`,
  `ServiceName`, `ResourceId`, `ResourceName`, `ResourceType`, `Region`,
  `MeterName`, `MeterCategory`, `MeterSubCategory`, `BillingPeriod`,
  `ChargePeriodStart`, `ChargePeriodEnd`, `BilledCost`, `EffectiveCost`,
  `ListCost`, `Quantity`, `UnitPrice`, `PricingUnit`, `Currency` (fixed `CHF`).
- **Custom tag columns**: `x_env` (dev/sit/prod), `x_hospital`
  (USZ/LUKS/Zollikerberg/Aggregated), `x_capability` (BMCA/OOA/DCA/ORSA/SBA/CSA).
- The authoritative column contract lives in
  [`tests/fixtures/focus_schema.json`](tests/fixtures/focus_schema.json).

### Cost calibration

Per-service annual weights sum to `1.0` and are scaled to the ROM baseline. The
top-3 services by share are **Microsoft Fabric**, **Azure Container Apps** and
**Azure Cosmos DB**, matching the Sprint 14 BOM. Per-row Gaussian noise
(mean 1.0, clamped ±30%) makes plan-vs-actual variance realistic while keeping
the annualised total within ±15% of CHF 760k.

Tuning knobs live at the top of `bva_synth_focus.py`:
`ROM_ANNUAL_AZURE_CHF`, the `SERVICES` catalog (per-service `weight`), and the
`HOSPITALS` / `ENVIRONMENTS` / `CAPABILITIES` tag domains.

## Tests

```bash
python3 -m unittest discover -s data-platform/scripts/tests -v
```

Covers determinism, FOCUS-shape conformance, ±15% cost calibration (across
multiple seeds), top-3 cost distribution, tag completeness, partitioning, and
the CLI. Enforced in CI by
[`.github/workflows/bva-generator.yml`](../../.github/workflows/bva-generator.yml).
