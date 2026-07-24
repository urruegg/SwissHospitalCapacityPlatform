# Foresight medallion notebooks (`foresight`)

> **Version** 1.0.0 · **Date** 2026-07-23 · **Author** Urs Rüegg · **Status** Draft · **Previous Version** — (new — Sprint 26 WS-A, issue #335)

Sprint 26 WS-A — the deterministic **Foresight tier** that turns the descriptive
Gold occupancy surface into the predictive tier (design spec §3.2 / D2): a
72h occupancy **Forecast**, its **Driver** decomposition ("why"), and a Trust-A
**Signal** projection that evidences the seasonality driver.

**Synthetic + deterministic only** (ADR-0013 / ADR-0016). No PHI (ward-level
aggregates and public-authority signals). **No LLM-guessed numbers** — every
number is a pure function of the ward baseline series (design D2/D4), with a
clean seam (`build_gold_forecast.run(wards=...)` / `DEFAULT_WARDS`) to swap in a
real forecasting model later without changing the Gold contract or ontology
binding.

## Design

The heavy Spark I/O lives in each module's `run()` (`# pragma: no cover`); the
transform logic is Spark-free and unit-tested (`tests/`), following the
`external-signals` notebook pattern. Empty inputs still write well-typed Delta
tables via an explicit `_empty_schema`.

| Module | Role |
| ------ | ---- |
| `build_gold_forecast.py` | `build_occupancy_forecast(wards, produced_at)` → `gold.fact_occupancy_forecast` rows; `build_forecast_drivers(...)` → `gold.fact_forecast_driver` rows (deltas reconcile to the net forecast change); `occupancy_forecast_envelope` / `forecast_driver_envelope` wrap rows into the `DC-*` contract for validation. |
| `build_gold_signal.py` | `foresight_signals(ext_rows)` — deny-by-default Trust-A projection over the Sprint 21 `gold.ext_fact_signal` spine with a deterministic `signal_probability(severity)`; → `gold.fact_signal`. |
| `run_foresight_medallion.ipynb` | Fabric orchestration: imports the modules and calls `run()`; verifies counts + the Medicine A 72h breach. |

## Medallion chain + table names

| Layer | Table | Contents |
| ----- | ----- | -------- |
| Gold | `gold.fact_occupancy_forecast` | One row per ward × horizon-hour (0..72h): forecast occupied beds, occupancy %, CI bounds, capacity-breach flag. Contract `DC-OCCUPANCY-FORECAST-v1`; grounds `hcp:Forecast`. |
| Gold | `gold.fact_forecast_driver` | One row per forecast-point × driver factor (`forecast_admissions` / `planned_discharges` / `transfers` / `seasonality`) with a signed bed delta + optional `signalId`. Contract `DC-FORECAST-DRIVER-v1`; grounds `hcp:Driver`. |
| Gold | `gold.fact_signal` | Trust-A projection over `gold.ext_fact_signal` (deny-by-default) with a deterministic probability, evidencing the seasonality driver. Reuses `DC-EXT-SIGNAL-v1`; grounds `hcp:Driver --evidencedBy--> hcp:ExternalSignal`. |

**Dependency:** the `gold.fact_signal` step needs the Sprint 21 external-signal
Gold tables (`gold.ext_fact_signal`, `gold.ext_dim_source`) already materialised
by [`../external-signals/run_ext_medallion.ipynb`](../external-signals/run_ext_medallion.ipynb).

## Ontology binding

`hcp:Forecast` / `hcp:Driver` / `hcp:Ward` + relations `forWard` / `explainedBy`
/ `evidencedBy` are declared in
[`docs/ontology/reference-layer.ttl`](../../../docs/ontology/reference-layer.ttl)
(v0.3.0) and mapped in
[`docs/ontology/crosswalk.md`](../../../docs/ontology/crosswalk.md) (v0.4.0),
enforced by the STRICT two-layer conformance gate.

## Offline test

```bash
cd data-platform/notebooks/foresight
python -m unittest discover -s tests -v

# STRICT ontology two-layer conformance (from repo root)
cd ../../..
python scripts/ontology/check_crosswalk_conformance.py --strict
```
