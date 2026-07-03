# HCC Utilization Pattern Conformance — Sprint 09 v2.0.0 Evidence

| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Date | 2026-07-03 |
| Author | Urs Rüegg |
| Status | Reviewed |
| Previous Version | n/a |

## Purpose

ADR-0002 / design spec §4.7 gate — the simulator's LUKS preset must reproduce the HCC utilization pattern reference within **MAPE < 15%** to be considered a faithful synthetic stand-in for the reference pattern.

## Result

> **PASS** — MAPE = 2.44% (threshold 15%).

## Method

- **Preset:** `LUKS` from [`apps/sim-capacity/src/calibration/hospital_presets.py`](../../../../apps/sim-capacity/src/calibration/hospital_presets.py)
- **Reference fixture:** [`apps/sim-capacity/tests/fixtures/hcc-utilization-pattern-luks-reference.json`](../../../../apps/sim-capacity/tests/fixtures/hcc-utilization-pattern-luks-reference.json) — hand-authored 12-month relative-demand curve from HCC utilization pattern PNG
- **Simulator:** [`SeasonalProfile.from_preset(preset, seed=42)`](../../../../apps/sim-capacity/src/calibration/seasonal_profile.py); 365 days from 2027-01-01
- **Aggregation:** daily expected admissions → monthly totals → normalized so `sum == 12`
- **Metric:** `MAPE = mean(|sim[m] - ref[m]| / ref[m]) for m in 1..12`
- **Test asserting:** [`test_seasonal_profile_produces_hcc_shape`](../../../../apps/sim-capacity/tests/test_seasonal_profile.py) — runs in CI on every PR that touches `apps/sim-capacity/**`

## Detail

| Month | Simulated | Reference | AE |
| ----- | --------- | --------- | ---- |
| Jan | 1.181 | 1.20 | 0.019 |
| Feb | 1.061 | 1.18 | 0.119 |
| Mar | 1.056 | 1.05 | 0.006 |
| Apr | 0.962 | 1.00 | 0.038 |
| May | 0.943 | 0.95 | 0.007 |
| Jun | 0.871 | 0.90 | 0.029 |
| Jul | 0.844 | 0.85 | 0.006 |
| Aug | 0.848 | 0.85 | 0.002 |
| Sep | 0.917 | 0.95 | 0.033 |
| Oct | 0.984 | 1.00 | 0.016 |
| Nov | 1.118 | 1.15 | 0.032 |
| Dec | 1.215 | 1.22 | 0.005 |

Peak (Dec) and trough (Jul) shape reproduced. Winter surge (Nov-Feb) and summer dip (Jul-Aug) preserved. Feb over-shoot vs reference (largest absolute error 0.119) is within threshold and reflects the reference PNG's very steep Jan→Feb→Mar decline that the deterministic monthly-multiplier model doesn't fully match.

## Reproducibility

```powershell
Set-Location apps/sim-capacity
python -m pytest tests/test_seasonal_profile.py -v
```

Expected: 3 passed. Deterministic via `seed=42`.

## References

- Design spec §4.5, §4.7 — [`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../../../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md)
- `docs/TEST.md` §Sprint 09 evidence — [`docs/TEST.md`](../../../TEST.md)
- ADR-0002 (execution runtime) — [`docs/adr/0002-runtime-is-github-copilot-coding-agent.md`](../../../adr/0002-runtime-is-github-copilot-coding-agent.md)
