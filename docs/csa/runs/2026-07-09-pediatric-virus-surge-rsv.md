---
scenarioId: pediatric-virus-surge-rsv
runId: run-rsv-2026-07-09-demo
tier: 2
requestedBy: crisis.manager
synthetic: true
---

# CSA run — Pediatric virus surge (RSV) — 2026-07-09

| Field | Value |
| ----- | ----- |
| **Scenario** | `pediatric-virus-surge-rsv` (F6) |
| **Requested by** | `crisis.manager` (`HCC.CrisisManager`) |
| **Tier** | **2 — Besondere Lage** |
| **Rules version** | ADR-0021 v1.0.0 |
| **Data** | Synthetic (ADR-0016) — computed via `csa-simulate.simulate()` |

## Tier classification

**Tier 2 (Besondere Lage).** Pediatric-bed utilisation reaches **112%**
(45 occupied vs 40 capacity after a +50% demand shock), breaching the 90%
threshold and requiring internal reallocation. Capacity is **not** exceeded
after internal levers (headroom leaves 46 effective beds ≥ 45 projected
occupancy), so the scenario stays single-site — it does not escalate to
Ausserordentliche Lage.

Rule fired: *pediatric-beds utilization 112% breaches threshold 90% — internal
reallocation required.*

## Key impacts

- Peak utilisation **1.13**; pediatric-bed shortfall **5 beds**.
- One resource dimension over threshold; nursing staff under strain.
- Single-site, seasonal onset (gradual over ~4 weeks).

## Recommended response levers

| Lever | Rationale |
| ----- | --------- |
| `lever-open-pediatric-overflow-cohort` | Convert adjacent capacity to absorb the 5-bed shortfall. |
| `lever-recall-off-duty-clinical-staff` | Relieve nursing strain from the surge. |
| `lever-accelerate-discharge-of-medically-fit-patients` | Free pediatric beds for incoming RSV admissions. |
| `lever-defer-non-urgent-elective-admissions` | Protect surge headroom over the wave. |

## KPI expectations

- `pediatric-bed-shortfall` → target ≤ 0 after overflow cohort + discharge.
- `pediatric-occupancy-pct` → back below 90% within the reallocation window.

## Doctrine citations

- Swiss *Lage* tiers per [ADR-0021](../../adr/0021-csa-tier-classifier-rules.md).
- Advisory only — no lever auto-executed (AGENTS.md §5).
