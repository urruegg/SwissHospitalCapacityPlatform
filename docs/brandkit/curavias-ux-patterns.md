# Curavias UX Design Patterns (Fluent v9)

| Field | Value |
|-------|-------|
| **Version** | 1.2.0 |
| **Date** | 2026-07-31 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | 1.1.0 (added narrative/showcase patterns P13-P17 from the Backstage build); this bump records Start as a live adopter of P13-P17 and adds the Start narrative-surface conformance note |
| **Sprint** | 27 — Curavias App UX Polish (tracker #365) |
| **Applies to** | `apps/hcc-app-fluent` (internal app, app.curavias.ch) |

> The catalogue of **composed UX patterns** used across the Curavias internal app.
> Where [`curavias-app-style-guide.md`](curavias-app-style-guide.md) defines the
> *atoms* (tokens, recipes, the per-screen heuristic gate), this document defines
> the *molecules and organisms* — the repeatable component + layout patterns that
> make every agent role board feel like one product. It is the reference the
> [`ux-design-agent`](../../agents/ux-design-agent/AGENT.md) grounds on for
> experience decisions and that the
> [`product-marketing-agent`](../../agents/product-marketing-agent/AGENT.md)
> grounds on for copy-in-context. Realises `FR-UX-002`; conformance is enforced
> through `NFR-UX-002` (the consistency review gate).

---

## 1. How to use this catalogue

- Each pattern has an **intent** (why it exists), an **anatomy** (the parts, in
  render order), an **implementation** anchor (the component / recipe that owns
  it), and **rules** (what makes a use conformant).
- Reuse the named component before building a new one. A new board is assembled
  from these patterns — it does not invent its own layout language.
- Every pattern composes from the tokens and recipes in the
  [style guide](curavias-app-style-guide.md); never hard-code spacing, radii,
  elevation, motion, or colour.
- All sample content is **simulated / generic** — no PHI
  ([ADR-0016](../adr/0016-no-phi-in-mvp-demo-scope.md)).

---

## 2. Pattern catalogue

### P1 — Board layout skeleton

- **Intent** — every MAIN role board reads top-to-bottom in the same order, so a
  user who learns one board can operate all of them.
- **Anatomy** (render order): `HandoffBanner` → `GroundingNotice` → `BoardHeader`
  → one or more stacked **card panels**.
- **Implementation** — the board view composes the skeleton; card panels use the
  card surface (P3). See `CsaView`, `OccupancyView`, `BedManagerBoard`.
- **Rules** — the four skeleton elements always appear in this order; a board adds
  content only inside card panels, never above the header.

### P2 — Board header

- **Intent** — a consistent identity + trust strip at the top of every board.
- **Anatomy** — `MAIN · <agent>` eyebrow (`Caption1`) · board title (`Title3`,
  from an i18n key) · provenance badge (P9) · access-lens badge (P11).
- **Implementation** — `boards/occupancy/BoardHeader.tsx`, reused by every board.
- **Rules** — the title comes from `t('board.<board>')`; the agent eyebrow uses
  the technical agent id; both badges are always present.

### P3 — Card panel surface

- **Intent** — one concern per card; visually grouped, raised, focusable.
- **Anatomy** — neutral background · `ds.radii.card` · `ds.elevation.card` ·
  `ds.space.l` padding; raises on hover, focus ring on `:focus-within`.
- **Implementation** — the `surfaceCard` recipe (style guide §2) or the board's
  local `card` style built from `ds`.
- **Rules** — never nest cards more than one level; a KPI strip (P6) may be a card
  or a row of tiles, but not both.

### P4 — Trusted signals panel

- **Intent** — show the external + internal evidence that feeds a board's
  recommendations, with provenance visible at a glance.
- **Anatomy** — a shared panel split into **External signals · Trust-A** and
  **Internal signals**; each row is `[icon] label · detail — [RAG status badge]
  [provenance icon]`.
- **Implementation** — `boards/occupancy/SignalsPanel.tsx` driven by the
  `BoardSignal` model (`data/roleboard/occupancy-data.ts`); reused by the
  Occupancy and Scenario boards.
- **Rules** — signals are **informational** (not clickable); the icon comes from
  the shared `SIGNAL_ICONS` map; external sources carry the `Trust-A` marker;
  provenance follows P9. Do not fork a bespoke signal list per board.

### P5 — RAG status badge

- **Intent** — one status-colour vocabulary across the whole app.
- **Anatomy** — `RagBadge` rendering a short status label in a filled pill; tone
  drives the colour via `ragColors` (`ChipTone`: `ok` / `watch` / `over` /
  `signal` / `muted`).
- **Implementation** — `RagBadge.tsx` + `ragColors` in `theme/curavias-theme.ts`.
- **Rules** — status colour is expressed **only** through `RagBadge` tones; never
  hand-roll a coloured chip. Green = ok, amber = watch, red = over/breach.

### P6 — KPI / stat tile

- **Intent** — a scannable headline metric.
- **Anatomy** — label (`Caption1`) + value (large `Text`) + optional delta with a
  RAG tone (P5).
- **Implementation** — the `statTile` recipe (style guide §2); grouped with the
  `boardGrid` recipe.
- **Rules** — one metric per tile; the delta tone reuses the RAG vocabulary.

### P7 — Operational worklist / queue table

- **Intent** — a dense, actionable list (placement requests, scenario queue,
  discharge worklist) that hands off to the Copilot rail.
- **Anatomy** — uppercase `Caption1` column headers · each row is
  `role="button"` with an `aria-label` · a RAG-coloured status column (P5) ·
  click routes to the rail (P10).
- **Implementation** — e.g. `ScenarioQueueTable.tsx`, `PlacementRequestsTable`.
- **Rules** — every row is keyboard-operable (`Enter` / `Space`); the status
  column uses RAG tones; selection opens the rail with row context — the table
  never mutates state itself.

### P8 — Ranked lever / recommendation board

- **Intent** — present the response options a copilot recommends, in a
  deliberate (curated) order, each with its impact and a single call to action.
- **Anatomy** — per-lever row: `[icon] label` · impact value · optional handoff
  badge (`→ <target>`) · SPOF / risk marker; a summary line; a primary CTA
  (e.g. "View resilience plan →"); an optional "absorbed" progress footer.
- **Implementation** — e.g. `ResilienceLeversBoard.tsx`.
- **Rules** — render the curated array order (do not re-sort in the view); the
  CTA and any lever selection route through the Copilot rail (P10).

### P9 — Provenance & grounding

- **Intent** — the user always knows whether they are looking at live or
  simulated data, and whether the board degraded.
- **Anatomy** — the `BoardHeader` provenance badge (`Simulated data` amber /
  `Live data` green) + a `GroundingNotice` degraded banner when the live source
  is unavailable.
- **Implementation** — `provenanceBadge` recipe · `boards/GroundingNotice.tsx` ·
  the `useDataSource` toggle that flips simulated ↔ live.
- **Rules** — the provenance badge is **never** removed or faked; a board reacts
  to the data-source toggle (its load effect depends on `source`); no fabricated
  "live" state; no PHI ([ADR-0016](../adr/0016-no-phi-in-mvp-demo-scope.md)).

### P10 — Copilot rail handoff

- **Intent** — every actionable element on a board flows into the same
  conversational surface, keeping the human in the decision seat.
- **Anatomy** — selecting an insight (scenario, table row, lever, CTA) calls
  `routeInsight` with a reco + context; the rail opens and the agent reply
  renders as a **grounded artefact** (a `RecoPanel` block), not a plain bubble.
- **Implementation** — `copilot-rail/` (`useCopilotRail`, `InsightRouter`,
  `RecoPanel`, `GroundedReply`).
- **Rules** — recommendations are **advisory** ("Vorschlag / Vorschau — der
  Mensch entscheidet"); the rail never auto-executes a deploy / delete action.

### P11 — Journey-ordered navigation + access lens

- **Intent** — the board tabs mirror the patient journey, and the UI communicates
  the role scope the user is operating under.
- **Anatomy** — `MainSubNav` tabs in journey order — Occupancy → Bed management →
  OR steering → Staffing → Discharge → **Scenario** — each gated by
  `capabilities.nav`; the access-lens badge (P2) names the active lens.
- **Implementation** — `workspaces/main/MainSubNav.tsx` · `auth/rbac-model.ts`.
- **Rules** — the tab order is the journey order; a tab is `disabled` (not hidden)
  when the role lacks its nav capability; sensitive *actions* stay behind their
  own role guard even when the informational board is visible.

### P12 — Multilingual labels

- **Intent** — the app speaks EN / DE / FR / IT with one key vocabulary.
- **Anatomy** — every user-facing string resolves through an i18n key; no
  hard-coded copy in components.
- **Implementation** — `src/i18n/{en,de,fr,it}.json`.
- **Rules** — add a key to **all four** locale files together; keep proper UTF-8
  (no mojibake); the wording / voice of each label is owned by the
  `product-marketing-agent` (P-voice), placed by the `ux-design-agent`.

> **Narrative / showcase surface patterns (P13-P17, added v1.1.0)** — anchored
> from the Sprint 27 Backstage build. These govern the **full-surface narrative**
> experiences (**Backstage and Start** both adopt them today). They compose the
> same tokens and recipes as P1-P12 and are the showcase counterpart to the P1
> board skeleton.

### P13 — Vertical narrative surface (showcase)

- **Intent** — a storytelling surface reads as one governed scroll: an intro that
  sets the stage, then one layer per topic, all under one persistent section nav.
- **Anatomy** (render order): full-width sticky section nav (P15) → an **intro
  rendered as the first section** (`Company` / setting-the-stage) → stacked layer
  sections, each self-described by a P14 header.
- **Implementation** — `workspaces/shared/narrative/NarrativeShell.tsx`; the
  surface passes `sections`, `introTitle` / `introEyebrow` / `introDescription`,
  `initialKey`, and `leadingGroupCount` (P16). `BackstageView` and `StartView`
  compose it today.
- **Rules** — the intro is section 0 (a nav item, not a floating hero); every
  section owns a stable `key` used for the nav value, the scroll-anchor id, and
  the scrollspy; content is centred in an up-to-1280 px column with
  `clamp(16px, 4vw, 48px)` gutters.

### P14 — Narrative section header (eyebrow variant)

- **Intent** — every layer introduces itself the same way, in an editorial voice.
- **Anatomy** (render order): **eyebrow** (`<Surface> · <topic>`, uppercase,
  `fontWeightBold`, `#12765F`, with a 22x3 px green `::before` dash) → **title**
  (`fontSizeBase600`, may be a quote / statement) → **lead** (`Body1`, full
  content width).
- **Implementation** — `SectionHeader` with `variant="eyebrow"`; the default
  variant (title → tagline → lead) stays for board-style headers.
- **Rules** — the title and lead are **not** width-capped (they use the content
  column via `flexGrow: 1`); copy avoids em-dash line-breakers; wording / voice is
  owned by the `product-marketing-agent`, placed by the `ux-design-agent`.

### P15 — Full-width sticky section nav

- **Intent** — the section switcher stays anchored below the header ribbon and
  always visible, while looking like the Main sub-nav (P11 tab language).
- **Anatomy** — a **full-width band** (`colorNeutralBackground2`, 1 px bottom
  border, **no** shadow) that is `position: sticky; top: 0`; inside it a centred
  `navInner` (up-to-1280 px + gutters) holding a Fluent `TabList` with the green
  underline indicator.
- **Implementation** — the `navBar` + `navInner` recipe in `NarrativeShell`.
- **Rules** — the band spans the full content width but the tabs align to the
  content column; tab style matches `MainSubNav` (plain tabs, no drop shadow);
  scroll is smooth and reduced-motion-aware.

### P16 — Storytelling scroll (one section per screen)

- **Intent** — on a normal desktop each layer is read on its own screen; the
  opening pair (setting-the-stage intro + first layer) share one screen.
- **Anatomy** — sections from index `leadingGroupCount` onward get a
  `min-height: calc(100vh - ~150px)` so one fills the viewport; the first
  `leadingGroupCount` sections render inside one full-height **lead group** (space
  between them) whose nav tabs both scroll to the group top, so a later section
  never peeks.
- **Implementation** — `NarrativeShell` `sectionFull` + `leadGroup` +
  `scrollTargetFor`; `BackstageView` passes `leadingGroupCount={2}` (Company +
  Frontier Firm share the first screen); `StartView` passes `leadingGroupCount={2}`
  (Overview intro + hero share the first screen).
- **Rules** — only the surface sets the group size; sections taller than the
  viewport keep their natural height (scroll within); tune the min-height offset
  so the next section stays off-screen.

### P17 — Context-click to the Copilot rail (no Ask buttons)

- **Intent** — the user investigates by clicking the **context** (a card, badge,
  domain, plane), not a separate button; the docked Product Owner Agent opens
  with a grounded, cited answer.
- **Anatomy** — every meaningful card / chip is a `<button>` that calls
  `rail.openWithReco(insight, reco)`; there is **no** "Ask the ..." button.
- **Implementation** — `useCopilotRail().openWithReco` from the section
  components (`BackstageNarrativeSections`, `SolutionDesignSection`,
  `DigitalFeedbackLoopSection`); grounded recos carry `citations` +
  `provenance: 'simulated'`.
- **Rules** — clickable context is a real button (focus ring; `aria-pressed`
  where it is a selection); the reco is advisory-only and cited (P10 voice);
  display-only evidence (tables, diagrams, credits) need not be clickable.

---

## 3. Per-board conformance matrix

A board is conformant when it uses each applicable pattern. `✓` = in use;
`—` = not applicable to that board.

| Board (agent) | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | P11 | P12 |
|---------------|----|----|----|----|----|----|----|----|----|-----|-----|-----|
| Occupancy (`ooa-agent`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| Bed management (`bmca-agent`) | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| OR steering (`orsa-agent`) | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Staffing (`sba-agent`) | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Discharge (`dca-agent`) | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Scenario (`csa-agent`) | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Backstage narrative surface

The Backstage surface uses the **surface-level** narrative patterns end-to-end:
**P13** (narrative shell), **P15** (sticky full-width section nav), and **P16**
(storytelling scroll, `leadingGroupCount={2}` — the Company intro + Frontier Firm
share the opening screen). Each layer then uses the **per-layer** patterns below.
`✓` = in use; `—` = not applicable.

| Backstage layer | P14 header | P17 rail | Layer content pattern |
|-----------------|------------|----------|------------------------|
| Company (setting the stage) | ✓ | — | intro copy (eyebrow + quote title + lead) |
| Frontier Firm (Success Framework) | ✓ | ✓ | split — numbered principle rows + "in numbers" card |
| Digital Feedback Loop | ✓ | ✓ | animated Microsoft IQ loop (domain cards + core) |
| Solution design (IQ operating model) | ✓ | ✓ | governed board — five IQ layers between gov / sec lanes |
| DevSecOps loop | ✓ | ✓ | DEV / OPS dual-loop SVG with HITL gate |
| Review sessions | ✓ | ✓ | sessions table + focus-domain cards + practitioner grid |
| Product Owner Agent | ✓ | ✓ | four lettered knowledge-class cards (A / B / C / D) |

> **P12 (i18n) follow-up** — the Backstage narrative copy is currently
> English-only (inline defaults + `en.json`); DE / FR / IT keys for the Backstage
> sections are a tracked follow-up before that surface is fully P12-conformant.

### Start narrative surface

The Start surface (Sprint 37 Frontier-Firm content, incorporated and re-layered
onto the shell in Sprint 27) uses the **surface-level** patterns end-to-end:
**P13** (narrative shell), **P15** (sticky full-width section nav), and **P16**
(storytelling scroll, `leadingGroupCount={2}` — the Overview intro + hero share
the opening screen). The docked **Product Owner Agent** rail (P10 / P17) is
present throughout `/start`.

| Start layer | P14 header | Layer content pattern |
|-------------|------------|------------------------|
| Overview (intro) | ✓ | page title + eyebrow + lead + guardrails (synthetic / advisory / no-PHI) |
| Hero + squeeze | — (own showcase header) | value hook + three BVA metrics + live `siteCapacity` squeeze card |
| Operating model (org → work) | ✓ | Humans / Agents / On-demand work modes + Frontier-Firm principle |
| CIO challenge (why now) | ✓ | the seven operational-decisions "Today vs Curavias" table |
| Three hospitals | ✓ | CuraNova / Curalp / Vialta cards + seven-agent roster |
| Patient path (launcher) | ✓ | RBAC-gated wave-band journey → `/main/<role>` (P11 handoff) |
| 90-day frontier | ✓ | Frame & Ground / Build & Prove / Operate & Scale phases |
| BVA (the decision) | ✓ | KPI tiles + TCO + value levers + sensitivity + proof (rail CTA) |

> **Start i18n status** — section titles / bodies are localized in **all four**
> locales (`start.frontier.*` in `en/de/fr/it`); only the P14 **eyebrow kickers**
> are English inline defaults — a small tracked follow-up before Start is fully
> P12-conformant.

---

## 4. Consistency review gate

A board or surface exits review only when **both** gates hold:

1. The **atom gate** — every item in
   [style guide §3](curavias-app-style-guide.md) (8 pt grid, type ramp,
   elevation, motion, interaction + async states, dark-mode parity, WCAG AA).
2. The **pattern gate** — the surface uses the applicable patterns above:
   - the P1 skeleton in order, with a P2 header carrying both badges;
   - status colour expressed only through P5 RAG tones;
   - signals via the shared P4 panel (no bespoke fork);
   - provenance + grounding per P9 (badge present, reacts to the data-source
     toggle, no PHI);
   - actionable elements hand off to the Copilot rail per P10 (advisory voice);
   - navigation + labels per P11 / P12 (journey order, four locales, no
     hard-coded copy).
   - for a **narrative / showcase surface** (Backstage and Start): the P13
     shell with a P15 sticky full-width nav, P14 eyebrow headers, P16
     storytelling scroll, and P17 context-click rail handoff (no Ask buttons).

---

## 5. Ownership & RACI

These patterns are **anchored to two agents** so that experience and message stay
consistent and stringent:

| Concern | `ux-design-agent` | `product-marketing-agent` |
|---------|-------------------|---------------------------|
| Pattern anatomy, layout, component reuse (P1–P17 structure) | **A / R** | C |
| Accessibility (WCAG) + i18n placement | **A / R** | C |
| Brand-token / RAG colour usage (P5) | **A / R** | C |
| Label wording, voice, advisory framing, disclaimer (P10, P12) | C | **A / R** |
| Rendered copy-in-context review (Playwright) | **A / R** | C |

**Handoff** — the `product-marketing-agent` owns the words in a label / reco /
disclaimer; the `ux-design-agent` places them into the pattern and verifies the
rendered result. New patterns are proposed by the `ux-design-agent` through the
`brainstorming` → `writing-plans` flow and added to this catalogue in the same PR.

---

## 6. Related documents

- [`curavias-app-style-guide.md`](curavias-app-style-guide.md) — tokens, recipes,
  and the per-screen heuristic gate (the atoms this catalogue composes).
- [`Curavias-Brand-Guidelines.md`](Curavias-Brand-Guidelines.md) — brand, colour,
  and voice foundations.
- [`agents/ux-design-agent/AGENT.md`](../../agents/ux-design-agent/AGENT.md) —
  the experience-lane owner that grounds on this catalogue.
- [`agents/product-marketing-agent/AGENT.md`](../../agents/product-marketing-agent/AGENT.md)
  — the message owner that grounds on this catalogue for copy-in-context.
- [`docs/PRD.md`](../PRD.md) — `FR-UX-002` / `NFR-UX-002` and the wider `FR-CX-*`
  / `FR-VIZ-*` UX requirements.
