# Sprint 10 Gold Medallion — Pending-Table Backlog

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | n/a (new — companion backlog tracker for the Sprint 11 grounding gap) |

> **Purpose**: Canonical in-repo record of the **7 grounding tables referenced by
> Sprint 11 agent manifests that do not yet exist** in the Fabric lakehouse. This
> is the *companion backlog issue* cited by every `status: pending` grounding
> entry across the Sprint 11 agent packs. It exists so the missing tables can be
> **produced**, **replaced**, or **retired** deliberately rather than silently
> assumed.
>
> **Origin**: During Fabric verification for PR #153, the actual `gold` schema in
> lakehouse `lh_ihzhhpf_sit` (workspace `ws-ihzhhpf-sit-data`) was enumerated via
> the OneLake DFS API — **17 tables present**. PR #153 reconciled the 8 agent
> references that resolve to real snake-case names and flagged the remaining 7 as
> `status: pending`. This tracker documents those 7.
>
> **Lane**: Data lane (Sprint 10 medallion) with a Platform-control-lane
> dependency (Sprint 13 agent-host enforcement). See
> [copilot-instructions §1 Architecture Lanes](../../../.github/copilot-instructions.md).

## 1. Pending tables

Each row is referenced by at least one Sprint 11 agent manifest under
[`agents/`](../../../AGENTS.md#1-registry) with a `status: pending` grounding
entry. "Manifest prediction" is the aspirational snake-case name the manifest
currently declares.

| # | Referenced by | Manifest prediction | Likely source | Resolution options |
| - | ------------- | ------------------- | ------------- | ------------------ |
| 1 | [`ooa-agent`](../../../agents/ooa-agent/manifest.yaml) (72-h forecast) | `gold.seasonality` | Derived from historical `gold.encounter` + calendar features; Fabric SQL view or scheduled notebook output | **produce** (calendar-feature view) |
| 2 | [`orsa-agent`](../../../agents/orsa-agent/manifest.yaml) (OR steering) | `gold.anaesthesia_status` | Could derive from `gold.or_case.eventType` sequence (event-stream ordering per case) | **produce** or **replace** (agent-host derived view) |
| 3 | [`orsa-agent`](../../../agents/orsa-agent/manifest.yaml) (OR steering) | `gold.staff_availability` | New — needs a staff-plan source of truth (Sprint 12 Entra? HR system?) | **produce** (blocked on staffing source-of-truth) |
| 4 | [`sba-agent`](../../../agents/sba-agent/manifest.yaml) (staffing balance) | `gold.shift_roster` | New — same staffing source-of-truth question | **produce** (blocked on staffing source-of-truth) |
| 5 | [`sba-agent`](../../../agents/sba-agent/manifest.yaml) (staffing balance) | `gold.shift_plan` | New — same staffing source-of-truth question | **produce** (blocked on staffing source-of-truth) |
| 6 | [`data-quality-agent`](../../../agents/data-quality-agent/manifest.yaml) | `ops.data_quality_runs` | New. The **`ops` schema itself does not yet exist**; needs a workflow-scheduled data-quality-run harness that writes results to a curated table. Ties in with the Power BI redesign perf-benchmark scenario. | **produce** (`ops` schema + DQ-run harness) |
| 7 | *(future — not yet in Sprint 11 manifests)* | `gold.discharge_transitions` (Spitex/rehab handoff status) | Would strengthen `dca-agent`'s HITL-03 story | **retire** for now (open when demo storytelling needs it) |

## 2. What Sprint 11 agents do in the meantime

Each pending table is flagged in the owning agent manifest so consumers can tell
grounded from aspirational sources:

```yaml
- table: gold.<name>
  scope: hospital
  status: pending   # NOT YET IN SPRINT 10 MEDALLION; see companion backlog issue
```

The agents that carry `status: pending` grounding entries today:

- [`ooa-agent`](../../../agents/ooa-agent/manifest.yaml) — `gold.seasonality`
- [`orsa-agent`](../../../agents/orsa-agent/manifest.yaml) — `gold.anaesthesia_status`, `gold.staff_availability`
- [`sba-agent`](../../../agents/sba-agent/manifest.yaml) — `gold.shift_roster`, `gold.shift_plan`
- [`data-quality-agent`](../../../agents/data-quality-agent/manifest.yaml) — `ops.data_quality_runs`

## 3. Refusal contract (enforced by the Sprint 13 agent-host)

Per the [Sprint 13 app design](../../superpowers/specs/2026-07-09-sprint-13-app-design.md),
the Container Apps agent-host that loads these packs at runtime must, until a
pending table exists:

1. **Refuse** any grounded query whose target table carries `status: pending`.
2. Emit the exact refusal code `REFUSE: grounding-source-pending: <table>`.
3. Cite this backlog tracker (and the governing issue) in the refusal so the
   caller can find the resolution status.

This is a contract *definition*; runtime *enforcement* is Sprint 13 scope and is
not implemented by the Sprint 11 packs themselves.

## 4. Out-of-scope follow-ups captured for context

These were surfaced alongside the pending-table gap but are tracked/handled
elsewhere — they are **not** resolved by this tracker:

- **Workspace name discrepancy** — design docs use `ws-ihzhhpf-sit`; actual is
  `ws-ihzhhpf-sit-data`. One occurrence at
  [`docs/superpowers/plans/2026-07-09-powerbi-demoable-redesign-plan.md`](../../superpowers/plans/2026-07-09-powerbi-demoable-redesign-plan.md).
  The Power BI redesign agent discovers this at M1 kickoff; no immediate fix.
- **`agents-archive/` → `agents/` restructure** — completed by PR #155
  (`agents/` is now the single source of truth).
- **Legacy `agents/csa-agent/`** — Sprint 09 pack superseded by the Sprint 11
  scaffold under the same folder as part of the #155 restructure.

## 5. Recommended sequencing

1. **PR #153** — Fabric-schema reconciliation (this tracker's origin). *(done)*
2. **Folder restructure PR #155** — `agents-archive/*` → `agents/*`. *(done)*
3. **File Sprint 10 medallion tickets** for the 7 pending tables (this tracker
   can be split into per-table tickets if cleaner for the data-platform team).
4. **Sprint 13 agent-host build** enforces the `status: pending` refusal
   contract in [§3](#3-refusal-contract-enforced-by-the-sprint-13-agent-host).

## 6. Related

- **Sprint 11 agents design** — [`docs/superpowers/specs/2026-07-09-sprint-11-agents-design.md`](../../superpowers/specs/2026-07-09-sprint-11-agents-design.md)
- **Sprint 13 app design** — [`docs/superpowers/specs/2026-07-09-sprint-13-app-design.md`](../../superpowers/specs/2026-07-09-sprint-13-app-design.md)
- **Sprint 10 medallion notebooks** — [`data-platform/notebooks/reference/`](../../../data-platform/notebooks/reference/)
- **Agent registry** — [`AGENTS.md`](../../../AGENTS.md#1-registry)
