# ADR-0025 — BVA KPI catalogue (DAX ↔ reference formulas + synthetic constants)

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Deciders** | @urruegg |
| **Superseded by** | — |

> Sprint 15 T5 mini-ADR. Records the BVA KPI catalogue: the canonical list of
> C-suite measures (design spec
> [`2026-07-09-sprint-15-bva-design.md`](../superpowers/specs/2026-07-09-sprint-15-bva-design.md) §6),
> their DAX↔Python mirroring contract, and the synthetic calibration constants
> every value/benefit KPI depends on.

## Context

The BVA semantic model (T5) exposes 28 measures on `bva_measures.tmdl`. The
sandbox cannot evaluate DAX, and we want the KPI **semantics** unit-tested and
board-explainable. We therefore keep a single pure reference implementation and
require the DAX to mirror it exactly.

## Decision

1. **Single source of formula truth** — the reference module
   [`data-platform/notebooks/bva/bva_kpi.py`](../../data-platform/notebooks/bva/bva_kpi.py)
   defines every KPI as a pure function. The DAX measures in
   [`bva_measures.tmdl`](../../data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/bva_measures.tmdl)
   mirror those formulas one-for-one (same name, same arithmetic, `DIVIDE`
   guards match `_safe_div`). Golden tests
   ([`test_bva_kpi_golden.py`](../../data-platform/reports/tests/test_bva_kpi_golden.py))
   assert catalogue completeness, the internal identities, and ROM calibration.

2. **Synthetic calibration constants** (documented so no board KPI is a black
   box; no PHI, no real financials):

   | Constant | Value | Used by |
   | --- | --- | --- |
   | `TARGET_ANNUAL_BENEFIT_CHF` | 1 200 000 | Benefit Realization % |
   | `TARGET_ACTIVE_USERS` | 120 | Strategic Adoption % |
   | `BED_DAYS_PER_DECISION_CYCLE` | 0.02 | Avoidable Bed-Day Index (COO) |
   | `MANUAL_TOUCHES_PER_DECISION_CYCLE` | 0.5 | Manual Touches Saved (COO) |
   | `COPILOT_TURNS_PER_USER_YEAR` | 144 | Cost per Copilot Turn (CTO) |
   | `BENEFIT_MULTIPLIER` (per capability) | 3.5–7.0 | Benefit Realized (in `bva_transforms.py`) |
   | `DECISION_CYCLES_PER_KCHF` (per capability) | 40–120 | Decision Cycles (in `bva_transforms.py`) |

3. **Headline mapping** (design spec §6):

   | Persona | Headline measure(s) |
   | --- | --- |
   | CEO | Net Value Realized (3yr), Benefit Realization % |
   | CFO | Actual TCO (Annualized), Budget Variance % |
   | CIO | Azure Run-Rate (Monthly), Cost Optimization Realized |
   | COO | Avoidable Bed-Day Index |
   | CTO | Cost per Copilot Turn |

## Consequences

- Any new/changed KPI updates **both** `bva_kpi.py` and `bva_measures.tmdl`, and
  is covered by a golden test — no drift between the tested logic and the model.
- Calibration constants are versioned here; changing them is a deliberate,
  reviewable act, not a hidden edit inside a report.
- COO operational proxies are explicitly synthetic until the operational Gold
  facts (bed-day / discharge) are joined in a later sprint.
