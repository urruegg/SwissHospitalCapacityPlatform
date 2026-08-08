# Sprint 40 — Curavias Start-Pane Frontier-Showcase Fidelity Polish

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-08-06 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Planned (design + plan authored; awaiting requester review before M1) |
| **Previous Version** | n/a (new document) |
| **Design spec** | [`docs/superpowers/specs/2026-08-06-sprint-40-start-frontier-fidelity-design.md`](../superpowers/specs/2026-08-06-sprint-40-start-frontier-fidelity-design.md) |
| **Implementation plan** | [`docs/superpowers/plans/2026-08-06-sprint-40-start-frontier-fidelity-plan.md`](../superpowers/plans/2026-08-06-sprint-40-start-frontier-fidelity-plan.md) |
| **Predecessors** | Sprint 27 (design system + local verify loop, #365) · Sprint 37 (Start → narrative shell) · Sprint 38 (Backstage → scroll narrative) |
| **Owner agent** | [`ux-design-agent`](../../agents/ux-design-agent/AGENT.md) |
| **Workflow** | Trunk-based parallel sprints — [`docs/DEV_WORKFLOW.md`](../DEV_WORKFLOW.md) + ADR-0038 |
| **Tracker issue** | [#561](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/561) (epic) |

> **Multi-sprint parallel-work note.** Per `docs/DEV_WORKFLOW.md`: `main` is the trunk; this
> sprint runs on its own worktree `sprint-40/start-frontier-fidelity` created off `main`
> (never stacked on another sprint's branch). Spec + this doc + plan land first. One
> milestone → one branch → one squash PR; CI is the merge gate; a **human merges**. Other
> workers see this sprint through the tracker issue and the `sprint-40` label.

---

## 1. Sprint goal

Bring the Curavias app **Start pane** (`/start`) to **content and visual fidelity** with the
Frontier-Showcase mockup — same information architecture, same content beats, same visual
devices — rendered natively in Fluent v9 + the codified design system so it stays
pattern-conformant, dark-mode-safe, accessible (WCAG 2.1 AA), and multilingual
(en / de / fr / it).

**Success shape:**

- Every Start section renders the mockup's content beats (no missing beat, no orphan beat),
  verified against a **content-parity matrix**.
- The mockup's signature devices — gradient headline, KPI tiles, glyph hospital cards, the
  seven-agent roster, the DC-INSIGHT beat strip, the 102% → 94% worked example, the TCO /
  value-lever / sensitivity tables — exist as **reused design-system recipes**, not one-off CSS.
- The hero is a **P14 eyebrow header**; section-to-rail handoff (P17) is consistent; section
  eyebrows are **i18n-keyed** (closing the tracked P12 gap).
- Every section passes the atom + pattern gates and axe AA; before / after evidence is
  attached per section.

---

## 2. Source baseline

1. [Sprint 40 design spec](../superpowers/specs/2026-08-06-sprint-40-start-frontier-fidelity-design.md) — goal, scope, approach, mockup beat catalogue, per-section gaps, recipes, i18n, milestones, DoD.
2. [Sprint 40 implementation plan](../superpowers/plans/2026-08-06-sprint-40-start-frontier-fidelity-plan.md) — milestone-by-milestone TDD tasks (M0–M6).
3. Mockup: [`docs/superpowers/ideas/Curavias-Frontier-Showcase.html`](../superpowers/ideas/Curavias-Frontier-Showcase.html) — content + visual source of truth.
4. [PRD](../PRD.md) — FR/NFR source of truth (`FR-UX-001..006`, `NFR-UX-001..004`).
5. `apps/hcc-app-fluent` — the internal app being polished (Start already on the narrative shell since Sprint 37).
6. [`docs/brandkit/curavias-ux-patterns.md`](../brandkit/curavias-ux-patterns.md) (P1–P17) + [`curavias-app-style-guide.md`](../brandkit/curavias-app-style-guide.md) (atom + pattern gates).
7. [`docs/runbooks/curavias-ux-local-verify-loop.md`](../runbooks/curavias-ux-local-verify-loop.md) — reused verify loop.

---

## 3. Sprint scope

| # | Task | Deliverable | DoD |
|---|------|-------------|-----|
| M0 | Confirm local verify loop | Baseline `/start` capture (reuse Sprint 27 runbook) | `dev`/`test`/`test:a11y` green on baseline; snapshots captured |
| M1 | Phase 1 intake | Parity matrix + `start-content.ts` structures + design-system recipes + i18n keys | Every reconciled beat renders; `tsc` + Vitest (content + i18n parity) green |
| M2 | `hero` + `work-chart` | P14 hero header; Humans/Agents/On-demand triad + principle mini-table | Atom + pattern gates; before/after evidence; axe clean |
| M3 | `cio-why-now` + `hospitals` | Decision mini-table restyle; glyph hospital cards + 7-agent roster strip | Gates + evidence + axe clean |
| M4 | `patient-path` | 5-stop beat strip + DC-INSIGHT strip + 102%→94% worked example | Gates + evidence + axe clean |
| M5 | `ninety-day` + `bva` | Three-phase device + live-in-PROD note; KPI tiles + TCO/lever mini-tables + sensitivity bars + proof chips + PO rail CTA | Gates + evidence + axe clean |
| M6 | Conformance close-out | Brandkit Start conformance table (P13–P17); close P12 eyebrow follow-up | Full `/start` axe + light/dark sweep clean; docs versioned + lint-clean |

Each milestone is one draft PR (or a small section group), human-merged.

---

## 4. Backlog stories

Stories map 1:1 to the plan's tasks. Each becomes a child issue linked to the epic (#561),
labelled `sprint-40` + `lane:experience`.

| Story | Milestone | Summary | FR/NFR |
|-------|-----------|---------|--------|
| S40-0 | M0 | Bring up the shared-context local verify loop; capture `/start` baseline | FR-UX-004 |
| S40-1 | M1-A | Author the Start content-parity matrix from mockup beats | FR-UX-006 |
| S40-2 | M1-B | Extend `start-content.ts`: agent roster, DC-INSIGHT, worked example, BVA tables (TDD) | FR-UX-006 |
| S40-3 | M1-C | Add reusable design-system recipes (KPI tile, glyph card, mini-table, beat strip, worked-example callout, sensitivity bars, proof chip) | FR-UX-001 |
| S40-4 | M1-D | Add i18n keys (en/de/fr/it) + key the section eyebrows (close P12) | FR-UX-001, NFR-UX-004 |
| S40-5 | M2 | Polish `hero` (P14 header) + `work-chart` | FR-UX-002/006, NFR-UX-001/002/003 |
| S40-6 | M3 | Polish `cio-why-now` + `hospitals` (+ agent roster) | FR-UX-002/006, NFR-UX-001/002/003 |
| S40-7 | M4 | Polish `patient-path` (+ DC-INSIGHT + worked example) | FR-UX-002/006, NFR-UX-001/002/003 |
| S40-8 | M5 | Polish `ninety-day` + `bva` (+ sensitivity + proof) | FR-UX-002/006, NFR-UX-001/002/003 |
| S40-9 | M6 | Conformance close-out: brandkit table + P12 follow-up | FR-UX-002/006, NFR-UX-001 |

---

## 5. Acceptance bar (per section)

A Start section is **done** when:

- Its mockup beat(s) are fully rendered (parity matrix reference); no missing/orphan beat.
- It passes the **atom gate** (8 pt grid, type ramp, elevation, motion, hover / pressed /
  focus, explicit empty / loading / error states, dark-mode parity) and the **pattern gate**
  (P13–P17; P14 eyebrow; P17 rail handoff) from the style-guide §3.
- `npm --prefix apps/hcc-app-fluent run test:a11y` is clean for the section (`NFR-UX-001`).
- New / changed copy is keyed and localised in en / de / fr / it with no mojibake.
- Before / after evidence (light / dark, desktop / narrow) is attached to the section PR
  (`NFR-UX-003`).
- `tsc` + Vitest green; the section consumes shared recipes, not bespoke CSS.

---

## 6. Traceability

| Requirement | How this sprint advances it |
|-------------|------------------------------|
| `FR-UX-001` | Extends the codified design system with reusable recipes |
| `FR-UX-002` | Updates the app style-guide + brandkit pattern catalogue (Start conformance + P12) |
| `FR-UX-004` | Reuses the SIT-connected local visual-verify loop |
| `FR-UX-006` | Executes the ordered polish backlog for the Start surface |
| `NFR-UX-001` | axe-core WCAG 2.1 AA per-section merge gate |
| `NFR-UX-002` | Fluent v9 + M365 heuristic checklist per section |
| `NFR-UX-003` | Before / after visual evidence on every section PR |
| `NFR-UX-004` | Experience-lane-only; no backend / data / agent / infra change |

---

## 7. Out of scope

- Any Backstage / Main / role-board change (Backstage reused as precedent only; the mockup
  states Main is not duplicated in the showcase).
- Backend, data-contract, agent-prompt, or infrastructure change; PHI; public-site (Astro)
  patterns — forbidden by `NFR-UX-004`.
- New brand tokens beyond the design system; new narrative sections beyond the mockup's beats.

---

## Appendix A — Session log

| Date | Session | Outcome |
|------|---------|---------|
| 2026-08-06 | Design + plan (autonomous) | Brainstorming → design spec, implementation plan, and this backlog authored on `sprint-40/start-frontier-fidelity`; mockup vendored; epic #561 opened; draft PR raised for review. Requester unavailable — user-review gate deferred; no app code written (brainstorming HARD-GATE respected). |
