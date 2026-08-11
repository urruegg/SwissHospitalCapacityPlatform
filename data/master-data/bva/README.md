# Curavias BVA — Master Data for the Product Owner Agent

Grounding tables for BVA, TCO and ROI questions. All figures CHF unless a
`_usd` column says otherwise. USD converted at 0.88 CHF/USD (`AS-001`).

## Tables

| File | Grain | Rows | Purpose |
| ---- | ----- | ---: | ------- |
| `dim_cost_element.csv` | cost element x model version | 15 | One-time and recurring cost lines, both v1.0.1 and v2.0.0 |
| `fact_build_cost_actual.csv` | build cost component | 5 | **Measured** 90-day showcase build cost |
| `fact_azure_cost_weekly.csv` | service x week | 65 | Authoritative Azure ActualCost billing |
| `fact_copilot_usage_weekly.csv` | week x store | 6 | Copilot token and AI Unit telemetry |
| `fact_effort.csv` | effort type | 3 | Human effort and derived cost |
| `fact_value_lever.csv` | value lever | 5 | ROM annual benefit assumptions |
| `fact_roi_scenario.csv` | scenario x model version | 6 | ROI, TCO and payback for all scenarios |
| `fact_unit_economics.csv` | unit metric | 5 | Cost per sprint / agent / resource / hour |
| `dim_assumption.csv` | assumption | 12 | Every modelling assumption, with confidence |
| `dim_evidence_source.csv` | source | 9 | Provenance and caveats per source |

## Evidence status vocabulary

The `evidence_status` column is the most important field in this dataset.
The agent must never present a `modelled` or `ROM` figure as measured.

| Value | Meaning |
| ----- | ------- |
| `measured` | From authoritative billing or a tracked record |
| `measured_extrapolated` | Measured over a shorter window, extended at observed run rate |
| `estimated` | Derived from a rate that is not authoritative |
| `telemetry` | Consumption signal, not a bill |
| `modelled` | ROM assumption |
| `modelled_on_measured` | ROM assumption anchored on a measured figure |
| `ROM` | Rough order of magnitude, ±30% |
| `mixed` | Composite of several statuses |

## Answering rules for the PO agent

1. **Always state evidence status.** "CHF 21,286 (measured)" and
   "CHF 780,000 (modelled, ±30%)" are different claims.
2. **Never quote the build cost as an implementation price.** The 90-day build
   is an art-of-the-possible showcase on synthetic data. It carries no real
   integration, no change management, no cantonal compliance mapping and no
   production HA.
3. **Copilot cost is an estimate.** No billed AI Unit rate exists
   (`AS-009`, confidence low). Say so when quoting it.
4. **Azure figures are proof-of-technology scope** — `westus2`, synthetic data,
   per ADR-0013. Not a production Swiss-region run rate.
5. **Run cost is unvalidated.** Section 5 of the BVA is the least evidenced
   part of the model; flag it on any TCO question.
6. **Copilot telemetry is incomplete.** The AIU series starts 2026-07-17.
   True full-build token cost is higher than stated.
7. **Two models coexist.** v1.0.1 (ROM, 127% ROI) and v2.0.0
   (Frontier-informed, 153% ROI). Name which one you are quoting.

## Headline figures

| Question | Answer | Status |
| -------- | ------ | ------ |
| What did the showcase cost to build? | CHF 21,286 over 90 days | measured |
| How much of that was human? | CHF 18,831 (88.5%), 174 h, 9.4% of an FTE-year | measured |
| How much was cloud and tokens? | CHF 2,454 (11.5%) | measured / estimated |
| What is the 3-year TCO? | CHF 4,530,000 (v2.0.0) or 5,050,000 (v1.0.1) | modelled |
| What is the ROI? | 153% (v2.0.0) or 127% (v1.0.1) | modelled |
| What is the payback? | ~3.6 months (v2.0.0) or ~6.1 months (v1.0.1) | modelled |
| What does the build evidence prove? | Platform-build cost collapses ~30x with 1 human + agents | measured vs ROM |
| What does it not prove? | That integration, adoption or compliance costs collapse | — |
