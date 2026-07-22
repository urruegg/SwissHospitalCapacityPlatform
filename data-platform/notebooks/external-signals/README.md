# External Signals medallion notebooks (`external-signals`)

> **Version** 1.0.0 · **Date** 2026-07-22 · **Author** Urs Rüegg · **Status** Draft · **Previous Version** — (new — Sprint 21 M3)

Sprint 21 M3 — the Fabric Spark notebooks that carry Trust-A Swiss authority
hazard warnings through the **DC-EXT-SIGNAL-v1** medallion (Bronze → Silver →
Gold) so the forecast overlay can pre-seed on external triggers.

**Synthetic-only** (ADR-0013 / ADR-0016). No PHI — the external feeds carry only
public authority hazard warnings (MeteoSwiss, SED, AlertSwiss, BAG).

## Design

The heavy Spark I/O lives in each notebook's `run()`; the transform logic is
Spark-free and unit-tested (`tests/test_signals_pure.py`), following the CSA
notebook pattern.

| Module | Role |
| ------ | ---- |
| `ingest_bronze_signals.py` | `bronze_path(source, date)` — partition convention for raw connector envelopes. `run()` lands them in Bronze. |
| `build_silver_signals.py` | `split_quarantine(records)` — keep `status == "Actual"`, quarantine the rest. `hazard_events(kept)` collapses overlaps via M2 `dedup.collapse`. |
| `build_gold_signals.py` | `to_gold_signal(rec)` → `gold.ext_fact_signal` row; `to_gold_dims(records)` → the three `ext_dim_*` dimensions. |

The Silver stage reuses the M2 `dedup`/`normalize` package under
[`data-platform/scripts/external-signals/`](../../scripts/external-signals/)
(loaded by path so the notebook stays importable in offline tests).

## Medallion chain + table names

| Layer | Path / table | Contents |
| ----- | ------------ | -------- |
| Bronze | `Files/Bronze/external-signals/<source>/<date>` | Raw DC-EXT-SIGNAL-v1 connector envelopes, partitioned by source + ingest date. |
| Silver | `silver.ext_signal` | Actual-status warnings, normalized + deduplicated. |
| Silver | `silver.ext_signal_quarantine` | Non-actual (Exercise / Test / Draft / expired) warnings, retained for audit. |
| Gold | `gold.ext_fact_signal` | One row per actual signal, `ext_*` columns for the forecast overlay + semantic model. |
| Gold | `gold.ext_dim_source` | Trusted-source dimension (`ext_source_id`, authority, trust tier). |
| Gold | `gold.ext_dim_hazard_type` | Hazard-type dimension (scenario template + default Lage tier). |
| Gold | `gold.ext_dim_region` | Affected-canton dimension. |
| Gold | `gold.ext_fact_trigger_event` | Collapsed HazardEvents (M2 `dedup.collapse`) that fire a forecast pre-seed. |

## Eventhouse route

For near-real-time signals the same Bronze envelopes are also routed to the
Real-Time Intelligence **Eventhouse** (`kql.ext_signal_stream`) via an
Eventstream custom endpoint, so an operator sees a hazard warning within minutes
while the batch Silver/Gold refresh keeps the semantic model consistent. The KQL
stream mirrors the `silver.ext_signal` schema and is the low-latency read path;
`gold.ext_fact_signal` remains the governed forecast-overlay source of truth.

## Offline test + seed

```bash
cd data-platform/notebooks/external-signals
python3 -m unittest discover -s tests -v

# End-to-end synthetic seed (runs the M2 connectors over their fixtures):
cd ../../scripts/external-signals
PYTHONPATH=. python3 signals_synth.py --dry-run
```
