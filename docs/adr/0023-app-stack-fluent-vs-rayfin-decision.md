# ADR-0023 — App stack decision: Fluent UI baseline vs Rayfin PoC

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Deciders** | @urruegg |
| **Superseded by** | — |

> Sprint 13 T8 exit ADR. Records the app-stack decision for Sprints 14+ using the
> comparison rubric in design spec
> [`2026-07-09-sprint-13-app-design.md`](../superpowers/specs/2026-07-09-sprint-13-app-design.md) §4.
> Filed at the path the design spec §4 and plan T7/T8 reserve
> (`docs/adr/00XX-app-stack-fluent-vs-rayfin-decision.md`).

## Context

Sprint 13 built two app tracks side by side (design spec §1–§2):

- `apps/hcc-app-fluent/` — the deployable Fluent UI v9 baseline (shell, MSAL
  auth, BedManager whiteboard with 6 card types, Backstage Roles tab, Copilot
  Drawer wired to BMCA via the Container Apps agent-host).
- `apps/hcc-app-rayfin/` — a time-boxed (3 engineering-day) Rayfin-generated
  skeleton for comparison.

The Rayfin generator is a **proprietary CLI/toolchain that was not runnable in
the delivery environment** (no network-reachable Rayfin service or license). Per
the T7 time-box rule (design spec §2.2), the PoC therefore records
**"not evaluable in scope"** for every rubric criterion that depends on running
the actual Rayfin toolchain. `apps/hcc-app-rayfin/` contains a minimal buildable
placeholder shell only (see its README) — it is **not** Rayfin-generated and is
not scored as PoC evidence.

## Decision

**Adopt the Fluent UI v9 baseline (`apps/hcc-app-fluent/`) as the app stack for
Sprint 14+.** The Rayfin track is closed as *not evaluable in scope*; it may be
revisited if a runnable Rayfin toolchain becomes available.

## Evidence per rubric criterion (design spec §4)

| # | Criterion | Fluent | Rayfin |
| --- | --- | --- | --- |
| 1 | Build velocity | Empty repo → shell + one board + agent-host in Sprint 13; app builds green in `app-build.yml`. | Not evaluable (toolchain unavailable). |
| 2 | Fluent UI parity | Native — built on `@fluentui/react-components` v9. | Not evaluable. |
| 3 | Brandkit fidelity | Helvion tokens applied via `src/theme/helvion-theme.ts`, derived from the Power BI M1 token mapping. | Not evaluable (placeholder reuses the same tokens but is not generated output). |
| 4 | Customisation depth | All 6 card types + custom whiteboard canvas + Copilot Drawer implemented. | Not evaluable. |
| 5 | Agent-drawer feasibility | BMCA wired end-to-end through the agent-host; grounded-reply contract test green. | Not evaluable. |
| 6 | License and GA posture | Fluent UI v9 + React 18 + Vite — all OSS/GA, MIT-compatible. | Proprietary; commercial terms not assessable here. |
| 7 | Test tooling | vitest (unit) + Playwright (E2E) + axe-core (a11y) + pytest (agent-host) all green in CI. | Not evaluable (placeholder reuses Playwright smoke only). |
| 8 | Long-term maintenance | Large OSS community, Microsoft-backed, predictable upgrade cadence. | Not evaluable. |

## Dissent notes

- The comparison is **asymmetric by necessity**: only one track was runnable, so
  this is a decision-by-default rather than a head-to-head win. If a Rayfin
  toolchain becomes available, a follow-up spike should re-run the rubric before
  Sprint 14 hardening locks the stack in.

## Consequences

- Sprint 14+ builds on `apps/hcc-app-fluent/`.
- `apps/hcc-app-rayfin/` is retained as a documented placeholder so the layout
  matches the design spec; it is not on the delivery path.
- The Container Apps agent-host (`apps/hcc-agent-host/`, ADR-0022) is the shared
  backend for both the current app and any future re-evaluation.

## Rollback path

Should Fluent prove unsuitable, the app tier can be re-evaluated: the frontend
talks to the agent-host only over `POST /agents/<name>/chat` and `GET /agents`
(a stable HTTP/JSON contract), so a replacement UI can bind to the same backend
without agent-host changes.
