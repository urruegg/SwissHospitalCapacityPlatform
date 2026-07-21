# capacity-dashboard.Report

Power BI PBIP report — persona-anchored, Curavias-branded capacity dashboard **v2**
(design spec `docs/superpowers/specs/2026-07-09-powerbi-demoable-redesign-design.md`,
plan `docs/superpowers/plans/2026-07-09-powerbi-demoable-redesign-plan.md`).

## Status

**v2 authored (M1–M6).** All pages carry populated `visualContainers[]`. The report
validates clean with `powerbi-report-author validate` (only network-blocked remote
JSON-schema warnings remain in the sandbox). Publishing to
`ws-ihzhhpf-sit-data` is a `deploy`-ceiling action gated by an `approved-to-apply`
comment per [AGENTS.md §4](../../../AGENTS.md) and is performed only after approval.

## Page structure (5 visible + 6 hidden)

Visible pages (in `pages/pages.json` navigation order):

| Page | Persona | Highlights |
| --- | --- | --- |
| `page-landing` | Entry | Curavias wordmark hero, persona navigation tiles, RLS-proof pill |
| `page-bed-manager` | Bed Manager | Occupancy/beds KPIs, capacity chart, field-parameter slicer, smart narrative, grounding strip |
| `page-or-coordinator` | OR Coordinator | OR KPI wall, Gantt-style timeline, donut, bar, funnel, field-parameter slicer, smart narrative, grounding strip |
| `page-ops-lead` | Ops Lead | Cross-site headline KPIs, flow cards, escalation-tier card (static stub), small-multiples strip, smart narrative, grounding strip |
| `page-grounding` | Governance | Traceability matrix (requirement → ADR → ontology entity → measure → visual) sourced from `grounding.yaml` |

Hidden helper pages (`visibility: HiddenInViewMode`):

| Page | Type | Purpose |
| --- | --- | --- |
| `tooltip-kpi-delta` | Tooltip | Custom tooltip for headline KPI cards |
| `tooltip-contributor` | Tooltip | Custom tooltip for contributor charts |
| `drill-ward` | Drill-through | Ward-level bed state (filter: `dim_ward_capacityunit[hospital_id]`) |
| `drill-theatre` | Drill-through | Per-theatre slot detail (filter: `or_case[orSlotId]`) |
| `drill-discharge` | Drill-through | Discharge readiness (filter: `dim_ward_capacityunit[hospital_id]`) |
| `page-perf-benchmark` | Hidden | Cold/warm hero-scenario benchmark cards + thresholds |

## Governance & data caveats

- **RLS-proof pill** is on every page, bound to `dim_persona[Effective Viewing Label]`.
  Verified across 6 identities by `data-platform/scripts/rls_test.py` (6/6 PASS).
- **No date dimension** in the Direct Lake model, so delta / time-intelligence
  measures are deferred; KPIs and smart narratives compose from base measures only
  (see `data-platform/scripts/check_gold_columns.py` advisory).
- **Field-parameter tables** (`param_capacity_measure`, `param_or_measure`) and the
  `grounding` / `benchmark` tables are Import-mode calculated tables — the same
  intentional Import exception already used by `dim_persona`.
- **Synthetic SIT data only — no PHI.**

## Validation

```bash
# Report structure (0 errors expected; remote-schema warnings are network-blocked)
powerbi-report-author validate data-platform/reports/capacity-dashboard.Report

# Semantic-model contract (16 relationships + 27 measures + 6 roles)
pwsh ./data-platform/scripts/export_semantic_model_tmdl.ps1 -VerifyOnly

# Theme / persona / gold-column / RLS / perf checks
python3 data-platform/scripts/theme_check.py
python3 data-platform/scripts/dim_persona_check.py
python3 data-platform/scripts/check_gold_columns.py
python3 data-platform/scripts/rls_test.py
python3 data-platform/scripts/perf_hero.py
```

## Related

- Semantic model: [`../capacity-dashboard.SemanticModel/`](../capacity-dashboard.SemanticModel/)
- Grounding source: [`grounding.yaml`](grounding.yaml)
- Curavias theme: [`themes/curavias.json`](themes/curavias.json)
- OR sample data: [`../../../data/synthetic/or-samples/`](../../../data/synthetic/or-samples/)
