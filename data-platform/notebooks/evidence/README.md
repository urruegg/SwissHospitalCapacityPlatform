# Evidence medallion notebooks (Sprint 14 · T3)

Fabric PySpark notebooks that ingest the Showcase Evidence JSON into the
Bronze → Silver → Gold medallion and score readiness. Gold star schema:
[`docs/data-platform/evidence-gold-schema.md`](../../../docs/data-platform/evidence-gold-schema.md).
Scoring rules: [`docs/adr/0021-readiness-scoring-rules.md`](../../../docs/adr/0021-readiness-scoring-rules.md).

## Pipeline order

| # | Notebook | Layer | Writes |
| - | --- | --- | --- |
| 1 | `ingest_bronze.py` | Bronze | `bronze.evidence_*` (raw JSON, schema-on-read) |
| 2 | `build_silver.py` | Silver | `silver.evidence_*` (typed + provenance-gated; `*_quarantine` for failures) |
| 3 | `build_gold_dims.py` | Gold | `gold.dim_*` (snake_case, `gold.` prefix) |
| 4 | `build_gold_facts.py` | Gold | `gold.fact_availability_evidence`, `gold.fact_bom_deployment`, `gold.bridge_*` |
| 5 | `score_readiness.py` | Gold | `gold.fact_readiness_snapshot`, `gold.fact_readiness_summary` |

## Invariants

- **Naming** — snake_case tables with a `gold.` schema prefix (per PR #153
  reconciliation), e.g. `gold.dim_resource`, `gold.fact_readiness_snapshot`.
- **Provenance gate** — Silver drops any row missing `sourcePath` / `sourceCommit`
  (facts also require `verifiedBy` / `asOf`) to a `*_quarantine` table.
- **Pure scoring** — the T-SHOW / T-PROD logic lives in
  [`readiness_rules.py`](readiness_rules.py) (no Spark) so it is unit-tested with
  a byte-stable golden regression fixture in
  [`tests/fixtures/readiness_golden/`](tests/fixtures/readiness_golden/).

## Deploy gate

Publishing these notebooks to `ws-ihzhhpf-sit-data` and running the pipeline is a
`deploy`-ceiling action. It requires an `approved-to-apply` comment from a repo
maintainer per [AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete).

## Test the pure functions locally

```bash
python -m unittest discover \
  -s data-platform/notebooks/evidence/tests \
  -t data-platform/notebooks/evidence/tests
```
