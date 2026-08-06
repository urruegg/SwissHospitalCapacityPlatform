# Sprint 40 — Curavias Start-Pane Frontier-Showcase Fidelity Polish — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-08-06 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (new document) |
| **Target app** | `apps/hcc-app-fluent` (internal app — app.curavias.ch) |
| **Owner agent** | [`ux-design-agent`](../../../agents/ux-design-agent/AGENT.md) |
| **Predecessors** | Sprint 27 (design system + local verify loop, #365), Sprint 37 (Start → narrative shell), Sprint 38 (Backstage → scroll narrative) |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution; no per-agent runtime change (ADR-0008 unchanged) |

> **For agentic workers:** This is a design spec. The implementation plan is produced
> separately via `superpowers:writing-plans` and executed via
> `superpowers:subagent-driven-development`. The brainstorming HARD-GATE is satisfied:
> this design is authored and committed for review before any production code.

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and problem statement](#2-context-and-problem-statement)
3. [Scope](#3-scope)
4. [Approach decision](#4-approach-decision)
5. [Mockup content catalogue → app mapping](#5-mockup-content-catalogue--app-mapping)
6. [Phase 1 — content and visual intake](#6-phase-1--content-and-visual-intake)
7. [Phase 2 — per-section visual verify loop](#7-phase-2--per-section-visual-verify-loop)
8. [Per-section gap register](#8-per-section-gap-register)
9. [Design-system recipes touched](#9-design-system-recipes-touched)
10. [i18n plan](#10-i18n-plan)
11. [Milestones](#11-milestones)
12. [Component boundaries and file map](#12-component-boundaries-and-file-map)
13. [Testing and accessibility](#13-testing-and-accessibility)
14. [Side-effect posture and approval gates](#14-side-effect-posture-and-approval-gates)
15. [Risk register](#15-risk-register)
16. [Traceability](#16-traceability)
17. [Definition of done](#17-definition-of-done)
18. [References](#18-references)

---

## 1. Goal and desired end state

Bring the internal Curavias app **Start pane** (`/start`) to **content and visual
fidelity** with the executive showcase mockup
[`docs/superpowers/ideas/Curavias-Frontier-Showcase.html`](../ideas/Curavias-Frontier-Showcase.html),
reusing the codified design system and the P13–P17 narrative patterns that the
**Backstage** surface already exercises end-to-end. The result is a Start pane that
tells the same C-level Frontier-Firm story as the mockup — same information
architecture, same content beats, same visual devices — but expressed natively in
Fluent v9 + the app design system, so it stays pattern-conformant, dark-mode-safe,
accessible, and multilingual.

**Desired end state:**

- Every Start section renders the mockup's content beats (no missing beat, no
  orphan beat), verified against an authoritative **content-parity matrix**.
- Every Start section passes the **pattern gate** (P13–P17 for the narrative
  surface; P14 eyebrow header; P17 context-click rail handoff) and the **atom gate**
  (8 pt grid, type ramp, elevation, motion, interaction + async states, dark-mode
  parity, WCAG 2.1 AA) from the
  [style-guide §3 consistency review](../../brandkit/curavias-app-style-guide.md).
- The mockup's signature visual devices — gradient headline, KPI tiles, glyph
  hospital cards, the seven-agent roster, the DC-INSIGHT beat strip, the 102% → 94%
  worked example, the TCO / value-lever / sensitivity tables — exist as **reused
  design-system recipes**, not one-off CSS.
- Start section **eyebrow kickers are i18n-keyed** (closing the tracked P12 gap) and
  all new / changed copy is localised in **en / de / fr / it**.
- Each polished section carries **before / after visual evidence** (light / dark,
  desktop / narrow) on its pull request.

## 2. Context and problem statement

The Start pane already adopted the shared **narrative shell** in Sprint 37: it renders
`START_SECTIONS` through
[`NarrativeShell`](../../../apps/hcc-app-fluent/src/workspaces/shared/narrative/NarrativeShell.tsx)
with a sticky full-width section nav (P15), storytelling scroll (P16,
`leadingGroupCount={2}`), and an intro-as-section-0 (P13). `StartHero` already uses
several mockup devices (the `#365B7D → #17B890` gradient hook, KPI metric tiles, trust
pills, the live `siteCapacity` squeeze card). **The structure is done — the gap is
fidelity and completeness**, and it is uneven across sections:

- **Content drift.** The mockup carries beats the app under-represents or omits — the
  seven-agent glyph roster ("The agent team behind every hospital"), the **DC-INSIGHT
  five-step** pattern ("How an agent answers"), the **102% → 94%** worked example, and
  the BVA **TCO / value-lever / sensitivity / proof** tables. Some app sections carry
  beats the mockup does not emphasise (e.g. the seven-decision "Today vs Curavias"
  table under `cio-why-now`). Neither side is authoritative yet.
- **Visual unevenness.** `StartHero` is close to the mockup; downstream sections
  (`work-chart`, `cio-why-now`, `hospitals`, `patient-path`, `ninety-day`, `bva`) vary
  in how faithfully they render the mockup's cards, mini-tables, glyphs, and green-tick
  eyebrow treatment.
- **Pattern conformance gaps.** The
  [brandkit conformance table](../../brandkit/curavias-ux-patterns.md#start-narrative-surface)
  shows the hero is not yet a P14 eyebrow header, and section-to-rail handoff (P17) is
  wired inconsistently across the frontier components.
- **P12 gap.** Section eyebrow kickers are **inline English literals** in
  `SECTION_META` (`StartView.tsx`), not i18n keys.

The user's requested method is explicitly two-phase: **(1)** intake all mockup content
and visuals into the app, then **(2)** walk each Start section visually in a
Copilot-chat-driven loop in VS Code against the shared local dev server
(`http://localhost:5173/start`), changing where needed. This spec structures the sprint
to that method and reuses the Backstage approach as the precedent.

## 3. Scope

### In scope

- All eight Start sections: `hero`, `work-chart`, `cio-why-now`, `hospitals`,
  `patient-path`, `ninety-day`, `bva` (plus the intro / overview section 0).
- **Content intake**: reconcile the app content model
  ([`start-content.ts`](../../../apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts))
  against the mockup; add missing beats; retire orphan beats only when they weaken the
  exec story; keep every figure grounded (BVA evidence, `siteCapacity`).
- **Visual intake**: express the mockup's devices as reused design-system recipes;
  make the hero a P14 eyebrow header; make section-to-rail handoff (P17) consistent.
- **i18n**: key the section eyebrows; localise all new / changed copy across
  en / de / fr / it.
- **Per-section verify loop**: reuse the Sprint 27
  [local visual-verify runbook](../../runbooks/curavias-ux-local-verify-loop.md) with
  before / after evidence and an axe scan per section.

### Out of scope (YAGNI)

- Any Backstage change (that surface is already narrative-complete; only reused as a
  precedent).
- Any Main / role-board change; the mockup itself states Main is not duplicated in the
  showcase.
- The standalone showcase HTML itself (it is the source of truth, not a deliverable).
- Backend / data-contract / agent-prompt / infrastructure change, PHI, or public-site
  (Astro) patterns — forbidden by `NFR-UX-004` (experience-lane only).
- New narrative sections beyond the mockup's beats; new brand tokens beyond the design
  system.

## 4. Approach decision

Three approaches were considered; **Approach A is chosen.**

### Approach A — Adapt the mockup to the Fluent design system (chosen)

Match the mockup's content, information architecture, and visual **devices**, but render
them through the app's design-system tokens and P13–P17 recipes.

- **Pros** — stays within `NFR-UX-002` pattern conformance and `NFR-UX-004`
  experience-lane guardrails; dark-mode and WCAG AA come "for free" from the token
  layer; maximises reuse of what Sprint 37 already built; every device becomes a
  reusable recipe usable by later surfaces.
- **Cons** — not a pixel-identical clone of the standalone HTML; a few mockup flourishes
  are re-expressed rather than copied verbatim.

### Approach B — High-fidelity pixel match

Reproduce the mockup's exact "Brand Kit v2" palette, gradients, and spacing as the pixel
target, even where it diverges from current recipes.

- **Pros** — closest literal match to the mockup.
- **Cons** — forks the design system (two sources of visual truth), risks dark-mode and
  contrast regressions, and violates `NFR-UX-002` / `NFR-UX-004`. Rejected.

### Approach C — Content-only intake

Pull the mockup copy and section order into existing components with minimal visual
change.

- **Pros** — smallest change; fastest.
- **Cons** — leaves the visual unevenness the user explicitly asked to fix; ignores
  Phase 2. Rejected as insufficient.

**Rationale.** This repo mandates a single codified design system as the source of visual
truth (`FR-UX-001`) and a consistency review gate keyed to pattern + atom conformance.
Approach A is the only option that satisfies the mockup-alignment goal **and** those
constraints, and it yields reusable recipes for the remaining polish backlog
(`FR-UX-006`).

## 5. Mockup content catalogue → app mapping

The mockup is a single governed scroll of C-level beats. This is the authoritative beat
list the content-parity matrix (M1) is built from. `✓` = beat already present in the app;
`~` = present but under-rendered; `+` = to be intaken.

| # | Mockup beat | Maps to Start section | Status |
|---|-------------|------------------------|--------|
| 1 | Page kicker "Start · for hospital & healthcare C-level · 5–10 min" | intro (section 0) | ✓ |
| 2 | Hook "The hospital of the future is a Frontier Firm. Curavias makes it real." + mission + "Every patient's path, in Swiss hands." | `hero` | ✓ |
| 3 | Guardrail pills (advisory · Swiss-resident synthetic · live in PROD) | `hero` | ✓ |
| 4 | Three headline BVA metrics + live capacity squeeze | `hero` | ✓ |
| 5 | "From the org chart to the work chart" — Humans / Agents / On-demand intelligence | `work-chart` | ~ |
| 6 | "How Curavias fits the Microsoft Frontier Firm" — 4-row principle mapping table | `work-chart` | ~ |
| 7 | "Three hospitals, each running as a Frontier Firm" — CuraNova / Curalp / Vialta glyph cards | `hospitals` | ~ |
| 8 | "The agent team behind every hospital · 7 runtime agents" — glyph roster (OOA, DCA, BMCA, CSA, ORSA, SBA, Data-Quality, PO) | `hospitals` | + |
| 9 | "One patient, one flow" — 5-stop journey (ARRIVAL → FORECAST → BED → DISCHARGE → COORDINATE) with agent + human owner per stop | `patient-path` | ~ |
| 10 | "How an agent answers — the DC-INSIGHT pattern" — SIGNAL / UNDERSTANDING / RECOMMENDATION / ACTION / COORDINATION | `patient-path` | + |
| 11 | Worked example "102% → 94%" (deterministic recompute; advisory · HITL · auditable) | `patient-path` | + |
| 12 | "Capacity Forecast — live in 90 days" — Frame & Ground / Build & Prove / Operate & Scale phases | `ninety-day` | ✓ |
| 13 | "Delivered pattern, not a promise" note (OOA already live in PROD) | `ninety-day` | ~ |
| 14 | "The BVA that kick-starts the frontier" — 4 KPI tiles (ROI, payback, net annual, 3-yr net value) | `bva` | ✓ |
| 15 | "Total Cost of Ownership — 3-year" mini-table (ROM / one-time / run / TCO / gross) | `bva` | ~ |
| 16 | "Where the annual value comes from" — value-lever mini-table | `bva` | ~ |
| 17 | "Sensitivity — ROI holds across scenarios" — conservative / base / upside bars | `bva` | + |
| 18 | "Proof it is real as-deployed" — live-in-PROD proof chips | `bva` | ~ |
| 19 | "Decision: kick-start the first frontier" + rail CTA "Ask the PO Agent about the BVA" | `bva` | ~ |

The app's `cio-why-now` seven-decision "Today vs Curavias" table has **no direct mockup
beat**; it is a legitimate app extension of beats 5–6. It is retained (not an orphan to
retire) and only **restyled** for consistency. The parity matrix (M1) records this
decision explicitly so reviewers see it is intentional.

## 6. Phase 1 — content and visual intake

Phase 1 makes the app content model the single, mockup-reconciled source, and lands the
new visual recipes, **before** the section-by-section visual walk.

1. **Content-parity matrix (M1-A).** Produce
   `docs/superpowers/artifacts/2026-08-06-start-content-parity-matrix.md` from §5 —
   every beat mapped to a section, a keep / add / retire decision, and the i18n keys it
   needs. This matrix is the acceptance reference for the rest of the sprint.
2. **Content model updates (M1-B).** Extend the typed structures in `start-content.ts`
   (e.g. `FRONTIER_AGENTS` roster with glyph + caption, a `DC_INSIGHT_BEATS` strip, a
   `WORKED_EXAMPLE` payload, BVA `TCO_ROWS` / `VALUE_LEVERS` / `SENSITIVITY` tables) so
   content stays declarative and testable. All figures reference existing grounded
   evidence (`bva-evidence`, `siteCapacity`); no fabricated numbers.
3. **Design-system recipes (M1-C).** Add / extend the reusable recipes in §9 so every
   mockup device is a design-system primitive.
4. **i18n keys (M1-D).** Add all new keys to en / de / fr / it together; key the section
   eyebrows.

Phase 1 exits when the app renders every reconciled beat with the new recipes (visual
review still pending) and `tsc` + Vitest + the content-model tests are green.

## 7. Phase 2 — per-section visual verify loop

Phase 2 walks each section in the Sprint 27
[local visual-verify loop](../../runbooks/curavias-ux-local-verify-loop.md) against the
shared `http://localhost:5173/start`, in the "within VS Code, sharing context with
GitHub Copilot" mode (read-only `playwright-mcp`):

For each section, in nav order:

1. **Capture before** — screenshot light + dark, desktop (≥ 1280) + narrow (≈ 768).
2. **Compare** — the section against its mockup beat(s) and the atom + pattern gates.
3. **Refactor** — adjust spacing (8 pt grid), elevation, hover / pressed / focus, empty
   / loading / error states, and dark-mode parity to close the gap, editing only the
   section component + its recipe usage.
4. **Verify** — Vite hot-reloads; re-snapshot in the shared browser.
5. **Scan** — `npm --prefix apps/hcc-app-fluent run test:a11y`; fix every axe violation.
6. **Attach evidence** — before / after screenshots on the section's pull request.

One section (or one small section group) per milestone / PR keeps diffs reviewable.

## 8. Per-section gap register

Initial gap read (refined by the M1 parity matrix). Fidelity is the current visual
distance from the mockup, not a defect count.

| Section | P14 eyebrow | P17 rail | Main gap to close |
|---------|-------------|----------|-------------------|
| intro (0) | ✓ keyed at shell | — | key `introEyebrow`; confirm guardrail chips match mockup |
| `hero` | promote to P14 header | metrics → rail | already close; make hero a P14 header; ensure KPI tiles + squeeze match device spec |
| `work-chart` | key eyebrow | cards → rail | render Humans / Agents / On-demand as a device-consistent triad + the 4-row principle table |
| `cio-why-now` | key eyebrow | rows → rail | restyle the seven-decision table to the mini-table recipe; mark as app extension |
| `hospitals` | key eyebrow | cards → rail | glyph hospital cards + **add** the seven-agent roster strip (beat 8) |
| `patient-path` | key eyebrow | stops → rail | 5-stop journey device + **add** DC-INSIGHT beat strip (beat 10) + **add** 102% → 94% worked example (beat 11) |
| `ninety-day` | key eyebrow | phases → rail | three-phase device parity + surface the "already live in PROD" note (beat 13) |
| `bva` | key eyebrow | tiles → rail | KPI tiles + TCO / value-lever mini-tables + **add** sensitivity bars (beat 17) + proof chips + PO rail CTA |

## 9. Design-system recipes touched

New or extended recipes live under
`apps/hcc-app-fluent/src/theme/design-system/` (or the shared narrative recipes) so they
are reusable and gate-checked once:

- **KPI tile** — label + figure + provenance caption (generalise the existing hero tile).
- **Glyph card** — icon glyph + title + stat lines (hospital cards, agent roster).
- **Mini-table** — compact two/three-column tabular device (principle mapping, TCO,
  value levers, decision table) with header row + green-square row markers.
- **Beat strip** — numbered step sequence (DC-INSIGHT SIGNAL → COORDINATION; the 5-stop
  journey shares this).
- **Worked-example callout** — before → after figure with advisory / HITL / auditable
  chips.
- **Sensitivity bars** — conservative / base / upside horizontal bars against the > 60 %
  governance target.
- **Eyebrow header (P14)** — apply the `SectionHeader` `variant="eyebrow"` uniformly,
  including the hero.
- **Proof chips** — live-in-PROD evidence chips (reuse the trust-pill recipe).

No new brand colours; devices compose existing semantic tokens (brand, neutral, RAG,
focus). Status colour only via P5 RAG tones.

## 10. i18n plan

- **Eyebrow keys.** Replace the inline-English `SECTION_META` eyebrows with
  `start.frontier.<section>.eyebrow` keys; the intro `introEyebrow` becomes a key with
  the current literal as its `en` default.
- **New copy.** Every intaken beat (agent roster captions, DC-INSIGHT step labels,
  worked-example strings, TCO / value-lever / sensitivity labels, proof chips) gets keys
  added to `src/i18n/{en,de,fr,it}.json` **together**.
- **Voice ownership.** Wording / voice is owned by the `product-marketing-agent`
  (P-voice), placed by the `ux-design-agent` (P12 rule). New keys use faithful
  translations of the mockup's English copy as the baseline; a follow-up P-voice review
  may refine tone.
- **UTF-8 hygiene.** No mojibake; the `check_mojibake` gate and the mojibake CI job must
  stay green.

## 11. Milestones

| Milestone | Deliverable | Exit |
|-----------|-------------|------|
| **M0** | Confirm the local verify loop runs on this worktree (reuse Sprint 27 runbook; no new enabler) | `npm run dev` serves `/start`; shared-context Playwright captures a baseline |
| **M1** | Phase 1 intake: parity matrix + content model + recipes + i18n keys | app renders every reconciled beat; `tsc` + Vitest + content tests green |
| **M2** | Phase 2 group 1 — `hero` (P14) + `work-chart` | both sections pass atom + pattern gates; before/after evidence; axe clean |
| **M3** | Phase 2 group 2 — `cio-why-now` + `hospitals` (+ agent roster) | gates + evidence + axe clean |
| **M4** | Phase 2 group 3 — `patient-path` (+ DC-INSIGHT + worked example) | gates + evidence + axe clean |
| **M5** | Phase 2 group 4 — `ninety-day` + `bva` (+ sensitivity + proof) | gates + evidence + axe clean |
| **M6** | Conformance close-out: update the brandkit Start conformance table + style-guide notes; full `/start` axe + light/dark sweep | brandkit table shows Start fully P13–P17 conformant; P12 eyebrow follow-up closed |

Each milestone is one squash-merge PR (or a small group), draft-first, human-merged.

## 12. Component boundaries and file map

Changes are confined to the Start frontier area, its i18n, and the shared design-system /
narrative recipes:

```text
apps/hcc-app-fluent/src/
  workspaces/start/
    StartView.tsx                     # key eyebrows; hero as P14 header
    frontier/
      start-content.ts                # + roster, DC-INSIGHT, worked example, BVA tables
      StartHero.tsx                    # P14 header; KPI tile recipe
      WorkChartSection.tsx             # triad + principle mini-table
      CioChallengerSection.tsx         # decision mini-table restyle
      HospitalsSection.tsx             # glyph cards + agent roster strip
      PatientPathLauncher.tsx          # 5-stop beat strip + DC-INSIGHT + worked example
      NinetyDaySection.tsx             # phase device + live-in-PROD note
      BvaDecisionSection.tsx           # TCO/lever mini-tables + sensitivity bars + proof chips
      *.test.tsx / start-content.test.ts   # extend for new content + a11y roles
  theme/design-system/                # KPI tile, glyph card, mini-table, beat strip,
                                      #   worked-example callout, sensitivity bars, proof chips
  workspaces/shared/narrative/        # SectionHeader eyebrow usage (no shell change)
  i18n/{en,de,fr,it}.json             # eyebrow keys + all new copy
docs/
  superpowers/artifacts/2026-08-06-start-content-parity-matrix.md   # M1 output
  brandkit/curavias-ux-patterns.md    # M6 conformance-table + P12 follow-up update
```

Each section component stays a single-purpose unit: one section = one file = one PR-sized
change, consuming shared recipes rather than bespoke CSS.

## 13. Testing and accessibility

- **Unit / content (Vitest).** Extend `start-content.test.ts` and the section
  `*.test.tsx` so every intaken beat has a rendered assertion and every new interactive
  device exposes the right role / name.
- **Accessibility (`NFR-UX-001`).** `npm --prefix apps/hcc-app-fluent run test:a11y`
  (axe-core WCAG 2.1 AA) is a merge gate per section and for the full `/start` sweep at
  M6.
- **Heuristic checklist (`NFR-UX-002`).** Every section passes the Fluent v9 + M365
  checklist (8 pt grid, type ramp, elevation, motion, hover / pressed / focus, explicit
  empty / loading / error states, dark-mode parity).
- **Visual evidence (`NFR-UX-003`).** Before / after screenshots (light / dark, desktop /
  narrow) attached to each section PR.
- **Type + build.** `npm --prefix apps/hcc-app-fluent run lint` (`tsc --noEmit`) and
  `run build` green before merge.
- **Docs.** `npx markdownlint-cli2` + `python scripts/lint/check_mojibake.py` on every
  edited doc; doc SemVer headers per copilot-instructions §9.

## 14. Side-effect posture and approval gates

- **Experience-lane only (`NFR-UX-004`).** Styling + content-presentation change only. No
  backend, data-contract, agent-prompt, or infrastructure change; no PHI; no Astro
  patterns.
- **Read-only browser automation.** The verify loop only inspects and captures; it never
  mutates repo or cloud state.
- **No deploy / delete.** The `ux-design-agent` ceiling is `write`; this sprint touches no
  `deploy` / `delete` tool. No `approved-to-apply` gate is invoked.
- **Human-merge.** Trunk-based; each stream is a draft PR the agent never self-merges.

## 15. Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Content-parity matrix reveals more beats than estimated | Medium | Medium | Matrix is M1's first task; milestones re-scoped from it before Phase 2 starts |
| A mockup device resists a clean Fluent recipe (e.g. sensitivity bars) | Medium | Low | Approach A permits re-expression; fall back to the nearest existing recipe + tokens, never a fork |
| i18n DE/FR/IT copy drifts from P-voice | Medium | Low | Baseline = faithful mockup translation; flag a P-voice follow-up rather than block the visual work |
| Dark-mode regressions from new devices | Low | Medium | Every recipe composes semantic tokens; dark-mode parity is in the per-section gate |
| Scope creep into Backstage / Main | Low | Medium | §3 out-of-scope is explicit; Main is a pointer per the mockup itself |
| Windows pre-commit mojibake hook false-fails | Medium | Low | Run `check_mojibake.py` manually; commit with hooks disabled when the hook misbehaves (documented in the runbook) |

## 16. Traceability

| Requirement | How this sprint advances it |
|-------------|------------------------------|
| `FR-UX-001` | Extends the codified design system with reusable KPI-tile / glyph-card / mini-table / beat-strip / sensitivity recipes |
| `FR-UX-002` | Updates the app style-guide + brandkit pattern catalogue (Start conformance + P12 follow-up) |
| `FR-UX-004` | Reuses the SIT-connected local visual-verify loop for the per-section walk |
| `FR-UX-006` | Executes the ordered polish backlog for the Start surface (the next surface after the OOA reference vertical) |
| `NFR-UX-001` | axe-core WCAG 2.1 AA as a per-section merge gate |
| `NFR-UX-002` | Fluent v9 + M365 heuristic checklist per section |
| `NFR-UX-003` | Before / after visual evidence on every section PR |
| `NFR-UX-004` | Experience-lane-only posture; no backend / data / agent / infra change |

The sprint tracker issue records these IDs; each section PR lists the FR / NFR IDs it
advances per the PR Output Contract.

## 17. Definition of done

- The content-parity matrix is complete and every beat has a keep / add / retire decision
  that is reflected in the app.
- All eight Start sections render their reconciled mockup beats with reused design-system
  recipes; no bespoke one-off CSS device remains.
- The hero is a P14 eyebrow header; section-to-rail handoff (P17) is consistent; the
  brandkit Start conformance table shows P13–P17 conformance and the P12 eyebrow
  follow-up is closed.
- Section eyebrows and all new / changed copy are keyed and localised in en / de / fr /
  it with no mojibake.
- Every section passes the atom + pattern gates and axe AA; before / after evidence is
  attached to each PR; the full `/start` axe + light/dark sweep at M6 is clean.
- `tsc`, Vitest, and `build` are green; all edited docs carry bumped SemVer headers and
  pass markdownlint + mojibake.
- Every stream is a draft PR merged by a human; no self-merge; no deploy / delete.

## 18. References

- Mockup: [`docs/superpowers/ideas/Curavias-Frontier-Showcase.html`](../ideas/Curavias-Frontier-Showcase.html)
- UX pattern catalogue: [`docs/brandkit/curavias-ux-patterns.md`](../../brandkit/curavias-ux-patterns.md)
- App style guide: [`docs/brandkit/curavias-app-style-guide.md`](../../brandkit/curavias-app-style-guide.md)
- Local verify loop: [`docs/runbooks/curavias-ux-local-verify-loop.md`](../../runbooks/curavias-ux-local-verify-loop.md)
- Sprint 27 design: [`docs/superpowers/specs/2026-07-24-sprint-27-curavias-ux-polish-design.md`](2026-07-24-sprint-27-curavias-ux-polish-design.md)
- UX design agent: [`agents/ux-design-agent/AGENT.md`](../../../agents/ux-design-agent/AGENT.md)
- Owning surface: [`apps/hcc-app-fluent/src/workspaces/start/`](../../../apps/hcc-app-fluent/src/workspaces/start/)
- Requirements: [`docs/PRD.md`](../../PRD.md) (`FR-UX-001..006`, `NFR-UX-001..004`)
- Runtime decision: [`docs/adr/0008-agent-runtime-pattern-scope-and-selection.md`](../../adr/0008-agent-runtime-pattern-scope-and-selection.md)
- No PHI in demo scope: [`docs/adr/0016-no-phi-in-mvp-demo-scope.md`](../../adr/0016-no-phi-in-mvp-demo-scope.md)
