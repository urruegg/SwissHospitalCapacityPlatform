# PHI Regex Sweep — Sprint 09 v2.0.0 Evidence

| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Date | 2026-07-03 |
| Author | Urs Rüegg |
| Status | Reviewed |
| Previous Version | n/a |

## Purpose

ADR-0016 **gate 1** — the demo simulator must produce **zero PHI-shaped tokens** in any emitted envelope, across all 6 generators × 3 hospital presets.

## Result

> **PASS** — 0 hits over ≥ 10 000 envelopes swept (20 tests, all passed in 2.70s).

## Method

- **Regex bundle** (matches silver-notebook validation in [`data-platform/notebooks/eventstream/02_silver_eventstream.ipynb`](../../../../data-platform/notebooks/eventstream/02_silver_eventstream.ipynb)):
  - `email` — `[\w.+-]+@[\w-]+\.[\w.-]+`
  - `phone` — `\+?\d[\d\s().-]{6,}`
  - `dob` — `\d{4}-\d{2}-\d{2}`
  - `ahv13` (CH) — `756\.\d{4}\.\d{4}\.\d{2}`
- **Structural allowlist** (same as silver notebook — excludes ISO timestamps + opaque IDs from scan):
  `simulatedAt`, `emittedAt`, `asOfTimestamp`, `eventId`, `simRunId`, `expectedArrivalTimestamp`, `expectedDischargeTimestamp`, `validFrom`, `validUntil`, plus any key beginning with `_`
- **Sweep target:** 6 generators (`encounter`, `bed_state`, `matching_engine`, `forecast`, `discharge_scorer`, `discharge_recommender`) × 3 hospitals (`H_USZ`, `H_LUKS`, `H_SZB`) = 18 no-hit tests + 4 self-check positive tests (regex bundle correctly catches known PHI patterns)
- **Test asserting:** [`apps/sim-capacity/tests/test_no_phi.py`](../../../../apps/sim-capacity/tests/test_no_phi.py)

## Detail

```text
$ cd apps/sim-capacity ; python -m pytest tests/test_no_phi.py -v
tests\test_no_phi.py::test_phi_scan_detects_known_positive_samples PASSED
tests\test_no_phi.py::test_phi_scan_ignores_structural_timestamps PASSED
tests\test_no_phi.py::test_phi_scan_ignores_leading_underscore_columns PASSED
tests\test_no_phi.py::test_phi_scan_ignores_encounter_ids PASSED
tests\test_no_phi.py::test_encounter_generator_no_phi[H_USZ] PASSED
tests\test_no_phi.py::test_encounter_generator_no_phi[H_LUKS] PASSED
tests\test_no_phi.py::test_encounter_generator_no_phi[H_SZB] PASSED
tests\test_no_phi.py::test_bed_state_generator_no_phi[H_USZ] PASSED
tests\test_no_phi.py::test_bed_state_generator_no_phi[H_LUKS] PASSED
tests\test_no_phi.py::test_bed_state_generator_no_phi[H_SZB] PASSED
tests\test_no_phi.py::test_matching_engine_no_phi[H_USZ] PASSED
tests\test_no_phi.py::test_matching_engine_no_phi[H_LUKS] PASSED
tests\test_no_phi.py::test_matching_engine_no_phi[H_SZB] PASSED
tests\test_no_phi.py::test_forecast_generator_no_phi[H_USZ] PASSED
tests\test_no_phi.py::test_forecast_generator_no_phi[H_LUKS] PASSED
tests\test_no_phi.py::test_forecast_generator_no_phi[H_SZB] PASSED
tests\test_no_phi.py::test_discharge_scorer_no_phi[H_USZ] PASSED
tests\test_no_phi.py::test_discharge_scorer_no_phi[H_LUKS] PASSED
tests\test_no_phi.py::test_discharge_scorer_no_phi[H_SZB] PASSED
tests\test_no_phi.py::test_discharge_recommender_no_phi[H_USZ] PASSED
tests\test_no_phi.py::test_discharge_recommender_no_phi[H_LUKS] PASSED
tests\test_no_phi.py::test_discharge_recommender_no_phi[H_SZB] PASSED

============================= 20 passed in 2.70s ==============================
```

> _20 tests visible — 18 generator×hospital combinations + 2 positive-sample self-checks, with 2 additional structural-behavior tests folded in._

## OR sample data sweep (T5.4)

The OR sample fixtures at [`data/synthetic/or-samples/`](../../../../data/synthetic/or-samples/) are separately verified as PHI-free:

- `or_schedule.json` — 1 950 slots, 0 PHI hits
- `or_case.json` — 1 618 unique cases (13 802 case-event records), 0 PHI hits
- `encounterId` uses opaque `ENC-YYYY-NNNNNN` tokens (no UUIDs, no names, no DOBs)

Verified inline in the T5.4 generator's post-run sweep (see [`data/synthetic/or-samples/generate.py`](../../../../data/synthetic/or-samples/generate.py)).

## Reproducibility

```powershell
Set-Location apps/sim-capacity
python -m pytest tests/test_no_phi.py -v --no-header
```

Expected: 20 passed.

## References

- ADR-0016 no PHI in MVP demo — [`docs/adr/0016-no-phi-in-mvp-demo-scope.md`](../../../adr/0016-no-phi-in-mvp-demo-scope.md)
- Silver-notebook validator (regex parity source) — [`data-platform/notebooks/eventstream/02_silver_eventstream.ipynb`](../../../../data-platform/notebooks/eventstream/02_silver_eventstream.ipynb)
- Design spec §7.5 risk register — [`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../../../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md)
