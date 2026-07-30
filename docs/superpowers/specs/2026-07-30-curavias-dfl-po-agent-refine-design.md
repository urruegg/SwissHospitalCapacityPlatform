# Curavias — Digital Feedback Loop refine + Backstage/Start vertical narrative (design)

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-30 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | none (initial) |

## 1. Context and problem

The Backstage **Digital Feedback Loop (DFL)** shipped in Sprint 35 diverged from
the approved mockup. The build targeted the wrong concept (the "Living Infinity"
`living-infinity-brand-linked-v3.html`). The correct, final target is the
Fluent-styled **signal simulation** captured in
[`docs/superpowers/ideas/digital-feedbackloop/digital-feedback-loop-final.html`](../../ideas/digital-feedbackloop/digital-feedback-loop-final.html)
(source: brainstorm `backstage-fluent-signal-simulation-v5.html`), kept next to
the source eBook PDF and anchored by
[`docs/superpowers/ideas/digital-feedbackloop/README.md`](../../ideas/digital-feedbackloop/README.md).

Two reframings drive this refactor:

1. **The right-hand panel is the Product Owner Agent.** The mockup's static
   "detail" column is really the `product-owner-agent` answering for the domain
   the user selects — a grounded, cited, evidence-based insight with business
   value (signal -> IQ -> action -> measured outcome). The app already routes a
   DFL domain click into `useCopilotRail().openWithReco(...)`; the panel should
   surface that grounded answer in place.
2. **Start and Backstage should become vertical scroll narratives.** Each is a
   single scrollable page of stacked sections, with a Main-style sticky section
   nav, an intro header + description, and a header + tagline + description on
   every section.

## 2. Goals

- Rebuild the DFL loop to **v5 parity**: four domain cards around a central
  Microsoft IQ core, with animated signal (cyan, inward), action (green,
  outward) and outcome (amber, return) flows, a journey strip, and an
  animation-behaviour note. Legible in **light and dark**; honours play/pause and
  `prefers-reduced-motion`.
- Make the DFL right column the **live Product Owner Agent** grounded answer:
  read -> cited evidence -> value, updating on domain select, with an
  "Open in Copilot" affordance that expands the full docked rail.
- Turn **Backstage** into a vertical scroll narrative: intro header +
  description; a sticky Main-style section `TabList` (scrollspy); every section
  wrapped with a header + tagline + description; the DFL is the flagship section.
- Define the pattern so **Start** can adopt it next (fast-follow).

## 3. Non-goals

- No change to the app shell (global header, left workspace rail, Start/Main/
  Backstage/Settings switch), to agents, MCP, or infrastructure.
- No role-gating of Backstage sections — Backstage is a showcase surface.
- No new data contracts or persistence. Reuse the existing golden source, BVA
  evidence, and `GroundedReco` machinery. Provenance stays `simulated`.
- Not building the Start restructure in this slice (design captured; separate
  implementation).

## 4. Decisions (from brainstorming)

| # | Question | Decision |
|---|----------|----------|
| Q1 | Scope / sequencing | **B** — Backstage + DFL first; Start as fast-follow. |
| Q2 | Scroll / nav model | **Scrollspy single page** — stacked sections, sticky top `TabList` highlights the current section and clicking scrolls to it. |
| Q3 | Mirror of Main "role selection" | **Visual pattern only** — a sticky Fluent `TabList` section switcher; Backstage sections are not role-gated. |
| Q4 | DFL right panel | **Inline grounded PO Agent answer** (reuse `buildReco`/`RecoPanel`) + "Open in Copilot" to expand the docked rail. |
| Q5 | DFL loop fidelity | **Full v5 parity**, dark-mode legible, motion-safe. |
| Q6 | Insights + value depth | **Surface a concrete business-value figure** per domain from BVA evidence where one exists; qualitative otherwise. |
| Q7 | Backstage section set | **DFL now**, stack existing Opportunities; stub Solution Design / Frontier (Sprint 36/37) as placeholders. |
| Q8 | Sprint / branch | Own design spec (this doc); implement on a worktree, preview on the `sprint-27` dev server. |

## 5. Design — shared vertical-narrative shell

A small, reusable pattern used by Backstage (now) and Start (next):

- **`NarrativeShell`** — renders an intro header (title + description), a sticky
  section `TabList`, and the stacked section children. It owns a scrollspy
  (an `IntersectionObserver` over the section anchors) that sets the active tab
  as sections cross a top threshold. Selecting a tab calls `scrollIntoView`
  (`behavior: 'smooth'`, downgraded to `'auto'` under `prefers-reduced-motion`).
- **`SectionHeader`** — a header + tagline + description block placed at the top
  of every section, so each section is self-describing.
- **Section registry** — an ordered list `{ key, labelKey, anchorId }` that feeds
  both the `TabList` and the stacked sections (single source of truth, mirroring
  `MainSubNav`'s `BOARDS` array).
- **Routing / deep-link** — keep `/backstage`; support `/backstage#<section>` and
  preserve back-compat for `/backstage/:widget` by scrolling to the matching
  section anchor on mount (no functional regression for existing links).

The nav visually mirrors `MainSubNav` (Fluent `TabList`), satisfying "similar to
Main's role selection", but without role gating.

## 6. Design — DFL section (v5 parity)

- **Section head** — `SectionHeader` with header "Digital feedback loop",
  tagline "Watch trusted signals become governed action through Microsoft IQ",
  and a one-line description. Tools live on the head row: a `SIMULATED / NO PHI`
  badge, an All loops / Selected domain segmented toggle, and a play/pause
  button.
- **Loop canvas** — aspect ratio 900/510, radial-gradient background using
  neutral tokens. Contains:
  - Four domain cards in the corners (27% x 31%): category label + icon, Curavias
    title, Microsoft label, SIGNAL text, ACTION text, and a return (loop-back)
    line. Cards are buttons (`aria-label` = Curavias label, `aria-pressed`).
  - A central **Microsoft IQ** core (25%): "Microsoft IQ" + "data, knowledge,
    context, decisions" + five IQ pills (Work / Foundry / Fabric / Process /
    Governance) that light up for the selected domain + a "Human approval before
    action" chip.
  - **Flows**: SVG rails (viewBox 900x510) — signal (cyan, inward), action
    (green, outward), return (amber dashed) with SIGNAL / ACTION labels; animated
    traveling dots via SMIL `animateMotion` + `mpath`. Play/pause toggles
    `svg.pauseAnimations()` / `unpauseAnimations()`; `prefers-reduced-motion`
    hides the dots and thickens the rails.
  - **Focus mode**: "Selected domain" dims non-selected streams; "All loops"
    shows all. The canvas keeps `data-testid="feedback-loop-canvas"` and
    `data-stream-mode` for the existing test contract.
- **Journey strip** — Data points -> Microsoft IQ -> Action packet -> Human
  approval -> Measured outcome.
- **Note** — the animation-behaviour explainer.
- **Layout** — loop (1fr) + PO Agent panel (right, ~300px); stacks vertically on
  narrow viewports.

## 7. Design — right panel is the Product Owner Agent

- On domain select, build a `GroundedReco` with the existing `buildReco(domain)`
  and render it inline through a compact `RecoPanel`: agent line
  "Product Owner Agent", context chip, grounded **read**, **levers** with hover
  evidence, **citations** (`hcp:*` / `gold.*`), a **value** line/metric, and the
  `simulated` provenance + advisory-only framing.
- The four "phases" of the mockup (signal packets arrive -> Microsoft IQ makes
  sense -> action returns -> outcome closes the loop) become the narrative
  scaffold of the answer, populated from the domain's grounded content.
- **Value (Q6)** — where a grounded BVA figure exists for a domain (via
  `data/bva/bva-evidence`), surface it as a `RecoMetric` / lever impact; else
  keep the read qualitative. Never invent numbers.
- **Deep-dive** — a primary "Open in Copilot" affordance calls
  `openWithReco(insight, reco)` to expand the full docked rail (unchanged global
  behaviour).
- **Default state** — with no explicit selection, the panel shows the default
  domain (command-center) answer, matching the mockup's initial state.

## 8. Data flow

- `feedback-loop-model` supplies the domains, their IQ layers, and citation ids.
- `buildReco(domain)` (today in `DigitalFeedbackLoopSection`) maps a domain to a
  `GroundedReco`; it moves to a small shared helper so both the inline panel and
  the docked rail use one source of truth.
- BVA figures come from `data/bva/bva-evidence` (`bvaHeadlineKpis`), mapped per
  domain only where a defensible figure exists.
- No new persistence; provenance is `simulated`.

## 9. Accessibility and motion

- Section nav: `TabList` with the active section reflected as the selected tab;
  keyboard operable; click scrolls (instant under reduced motion).
- DFL: the SVG is decorative (`aria-hidden`); domain buttons expose `aria-label`
  and `aria-pressed`; the PO Agent panel is `aria-live="polite"` so its answer is
  announced on select; motion honours `prefers-reduced-motion` and play/pause;
  colour contrast meets WCAG 2.1 AA in light and dark themes.

## 10. Testing

- Preserve the `DigitalFeedbackLoop` unit contract: selecting a domain emits it
  once; the mode toggle sets `data-stream-mode`; pause swaps to play.
- Update `backstage-view.test` for the vertical narrative — assert the intro
  header, the section `TabList`, and each section anchor by test id; keep the
  `/backstage/:widget` deep-link scrolling to the right section.
- Add tests: the PO Agent panel renders the grounded reco for the selected
  domain (read + citations present); "Open in Copilot" calls the rail.

## 11. Traceability

- **FR-POA-001**, **FR-POA-002** — Product Owner Agent grounded, cited answers.
- **FR-CX-004**, **FR-CX-006** — provenance badges and showcase UX.
- **NFR-GOV-006** — traceability / provenance on every surfaced figure.
- **ADR-0043** — Product Owner Agent on the Foundry IQ knowledge layer.

## 12. Risks and open items

- Scrollspy + routing rework can touch `backstage-view.test` (route-switch ->
  scroll). Mitigation: keep `/backstage/:widget` as a deep-link that scrolls to
  the section anchor, so existing links and most assertions hold.
- Sprint 36 (Solution Design) and Sprint 37 (Frontier) sections are stubbed here
  and filled when that content is integrated.
- SMIL pause/resume differs slightly across engines; if it misbehaves, fall back
  to CSS motion-path animation gated by `animation-play-state`.
- The final mockup + PDF + anchor README currently live in the root working
  copy's ideas folder; reconcile onto the implementation branch at commit time.

## 13. Rollout

1. Backstage vertical-narrative shell + DFL section (v5 + PO Agent panel) — this
   spec.
2. Start adopts the same `NarrativeShell` + `SectionHeader` pattern — fast-follow
   spec.
