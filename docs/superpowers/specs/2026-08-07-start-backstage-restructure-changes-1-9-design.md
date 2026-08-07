# Curavias START + BACKSTAGE restructure (changes 1-9) - design

| Field | Value |
| ------- | ------- |
| **Version** | 1.1.0 |
| **Date** | 2026-08-07 |
| **Author** | Urs Rueegg |
| **Status** | Approved (decisions D1-D4 locked by user 2026-08-07); ready for writing-plans |
| **Previous Version** | 1.0.0 (initial agent-reviewed design with 4 open decisions) |

> Brainstormed 2026-08-07 (Superpowers `brainstorming`). References: the
> marketing-approved mockup
> [Curavias-Frontier-Showcase.html](../ideas/Curavias-Frontier-Showcase.html),
> the live app `/start` + `/backstage`, and the shared `NarrativeShell` /
> `SectionHeader` narrative kit. This design was reviewed in-character by three
> repo agents before write-up: **ux-design-agent** (IA, spacing, a11y, header
> treatment), **product-marketing-agent** (message impact, keyword emphasis,
> claim consistency), and **product-owner-agent** (change 9 context-ask
> story-typing against the four knowledge classes). Their verdicts and the
> resulting decisions are recorded per change in section 3.
>
> **Scope note**: This is a *restructure + standardisation* design, not new
> product content. It is experience-lane only, additive/reversible, synthetic
> and no-PHI. **Change 9 is documentation only** and is deferred to a separate
> sprint per the user's instruction.

## 1. Goal

Align the app's START and BACKSTAGE planes to the marketing-approved mockup's
information architecture, and standardise the cross-cutting narrative chrome
(spacing rhythm and section-header treatment). Concretely, nine changes:

1. Remove the standalone **Why now** section from START.
2. Move the **BVA** section from START to BACKSTAGE (first part, right after the
   company intro).
3. Move the **90-day roadmap** from START to BACKSTAGE (last part).
4. Adopt the mockup's new **patient-journey** eyebrow / title / lead / worked-example
   copy, while keeping the existing patient-flow visual and routing unchanged.
5. **Language alignment**: audit START + BACKSTAGE and fill i18n gaps so every
   string renders in the user's selected language (en / de / fr / it).
6. **Spacing standardisation**: replace the oversized inter-section whitespace
   with a token-based rhythm and fix the header-to-body gap.
7. **Section-header standardisation + colour-coding**: one header treatment
   across all sections in both planes, with the mockup's colour-highlighted
   title keyword.
8. **Backstage gap analysis**: add the mockup parts the app is missing without
   touching existing content or charts.
9. **Context-ask story-typing** (DOC ONLY, separate sprint): inventory each
   section's clickable Copilot-rail context ask and map it to the Product Owner
   Agent's four knowledge classes, as validation user stories.

## 2. Non-goals

- **Not** reworking the patient-flow visual itself (a separate follow-up).
- **Not** editing existing BACKSTAGE section content, prose, or charts (change 8
  is additive only).
- **Not** implementing change 9 in code - it produces a story backlog only.
- **Not** changing the BVA data binding to the mockup's ROM numbers (see 3.2 -
  the app's data-bound figures are a by-design divergence).
- **Not** touching platform runtime, agents, infra, data, or governance lanes.
- **Not** deleting the retired Why-now assets - they stay as reversible dead data.

## 3. Changes, agent reviews, and decisions

### Workstream A - START restructure (changes 1-4)

Current START order (`start-content.ts` `START_SECTIONS`):
`hero -> challenger -> vision -> work-chart -> hospitals -> cio-why-now ->
patient-path -> ninety-day -> bva`.

Target START order (matches the mockup's START chapter, which has no
Why-now / BVA / 90-day):
`hero -> challenger -> vision -> work-chart -> hospitals -> patient-path`.

#### 3.1 Change 1 - remove Why now

- **Decision**: Drop `cio-why-now` from the `StartSectionId` union,
  `START_SECTIONS`, `SECTION_META`, and the `sectionBody()` switch in
  `StartView.tsx`. Keep `CioChallengerSection.tsx` (Why-now body) and its i18n
  block on disk as reversible dead data (no registry reference).
- **Agent review (ux + marketing, both approve)**: Do **not** keep it as a nav
  item. Both suggested preserving a small urgency signal in START.
- **USER DECISION (D3, locked)**: Remove Why-now and **add nothing** to the other
  sections - no urgency signpost, no copy bridge. The `cio-why-now` section is
  dropped from the registry and its body/i18n stay on disk as reversible dead
  data; no other section copy changes for this change.

#### 3.2 Change 2 - move BVA to Backstage (first part)

- **Decision**: Insert a `bva` part at `BACKSTAGE_PARTS[0]` (first sub-nav part,
  immediately after the `company` intro). Add a thin `BackstageBvaSection`
  wrapper that reuses the existing START BVA body (`BvaDecisionSection.tsx`) so
  the tested data binding is preserved. Remove `bva` from `START_SECTIONS`.
- **Agent review (ux + marketing, both approve as Backstage-2nd)**: BVA belongs
  right after Company because it answers "did Curavias make its own business
  case first?". Keep the BVA disclaimers next to the numbers.
- **Number-consistency risk (marketing, high priority)**: The mockup shows a ROM
  case (**127% ROI, ~6-month payback, CHF 2.57M net annual**); the app's BVA
  tiles data-bind to a realised snapshot (**212% ROI, CHF 4.2M**). Do **not**
  collapse these into one "business case". Label them distinctly - e.g.
  "Decision case / base ROM (public-data calibrated, illustrative, +/-30%)" vs
  "Current evidence snapshot / data-bound (with as-of provenance)" - and let the
  PO rail reconcile them rather than silently choosing one.
- **Resulting decision**: Keep the app's data-bound figures (no regression to
  mockup ROM). **USER DECISION (D4, locked)**: adapt/keep the **real data-bound**
  numbers; the mockup ROM figures are not introduced. The BVA + ROI will be
  refreshed with additional facts in a **separate later follow-up** (out of scope
  here). Because only the data-bound figures are shown, the dual-number labeling
  risk is moot; the BVA disclaimer still travels with the section.

#### 3.3 Change 3 - move 90-day to Backstage (last part)

- **Decision**: Append a `ninety-day` part at the end of `BACKSTAGE_PARTS`
  (mockup order). Add a `BackstageNinetyDaySection` wrapper reusing the existing
  `NinetyDaySection.tsx` body. Remove `ninety-day` from `START_SECTIONS`.
- **Migration note**: `BvaDecisionSection.tsx` calls
  `scrollToSection('ninety-day')`. Because BVA and 90-day both move into
  Backstage, this intra-plane scroll continues to resolve - verify after the move.
- **Agent review (ux + marketing, both approve as Backstage-end)**: It becomes
  the natural conversion / "what next" CTA. Its disclaimer ("delivered pattern,
  not a promise; timeline depends on governance, data access, named owner,
  approval gates") must travel with it.
- **Resulting decision**: Append at Backstage end; carry the disclaimer.

#### 3.4 Change 4 - patient journey copy, visual unchanged

- **Decision**: Update only the patient-journey eyebrow / title / lead /
  worked-example i18n strings to the mockup copy ("Key visual 2 - Patient
  journey" / "One patient, one flow - humans and agents together" + the DC-INSIGHT
  worked example). Keep the existing patient-flow visual component and its
  routing/launcher behaviour untouched.
- **Agent review (ux + marketing, both approve)**: Keep routing untouched;
  verify the visual's accessible name and mobile horizontal-scroll behaviour
  after the copy change.
- **Resulting decision**: Copy-only update; add an a11y check for the visual's
  accessible name + mobile scroll in the verification pass.

### Workstream B - cross-cutting standardisation (changes 5-7)

#### 3.5 Change 5 - language alignment

- **Known gaps**: fr / it miss the vision block; challenger persona prose is
  EN-only; verbatim review quotes are kept in original language with an English
  gloss.
- **Agent review (marketing)**: Continue the **verbatim-quote + English-gloss**
  governance pattern (preserves auditability, avoids fabricating reviewer
  language) but treat it as a *declared* exception: the quote stays original; the
  label, surrounding prose, and gloss labels must render in the selected UI
  language. Label glosses visibly ("Original quote" / "English gloss"), not blended
  into translated prose. No English islands outside that declared exception.
- **Resulting decision**: Produce an i18n coverage matrix (section x en/de/fr/it),
  fill fr/it vision + challenger prose, add visible gloss labels, and add a test
  that fails on any missing key in the four locales for START + BACKSTAGE.

#### 3.6 Change 6 - spacing standardisation

- **Root cause (confirmed)**: `NarrativeShell.sectionFull` forces
  `minHeight: calc(100vh - 150px)` per non-lead section (the oversized gaps on
  short sections); the section-header and body are stacked with no wrapping gap
  (the "Organisation subtitle too close to the hospital cards" bug).
- **Agent review (ux)**: **Soften, do not blindly strip** vertical breathing.
  Make full-height an opt-in for hero / lead / visually dense sections only;
  drive rhythm with **section padding + a standard gap**, not min-height; use
  `100svh` rather than `100vh` if any viewport sizing remains. Recommended tokens:
  - Section vertical padding: 48-64px desktop, 32-40px tablet, 24-32px mobile.
  - Section-to-section gap: 32px (avoid large padding *and* large flex gap).
  - Header -> body gap: 24px desktop, 16px mobile.
  - Header internals: eyebrow -> title 4-8px; title -> lead 8-12px.
  - Card/grid gaps: 16px normal, 24px for split-pane storytelling.
- **Resulting decision**: Map those px targets to the nearest Fluent
  `spacingVertical*` tokens; make `sectionFull` opt-in; add one shared
  header/body wrapper (with the token header->body gap) used by BOTH planes;
  switch any residual viewport sizing to `svh`.

#### 3.7 Change 7 - section-header standardisation + colour-coding

- **Decision**: Extend the shared `SectionHeader` to render a colour-highlighted
  title keyword (the mockup's `<span class="grad">` treatment) and apply the one
  eyebrow+title+lead treatment across all sections in both planes.
- **Agent review (ux)**: Use **structured title parts**
  (`titleParts: [{ text, tone: 'default' | 'accent' }]`), **not** a single
  accent-substring prop - a substring is brittle for i18n, punctuation, repeated
  words, and reordered fr/it titles. a11y rules: keep one real heading element;
  spans inside are fine; do **not** `aria-hidden` the accent span; ensure spaces
  are literal so `getByRole('heading', { name })` reads naturally; gradient text
  needs a solid-colour fallback for forced-colors / high-contrast; test contrast
  as if the gradient were its lightest stop. Consider an optional heading-level
  prop (surface intros h1; narrative sections h2).
- **Agent review (marketing)**: Emphasis clause per title (ready to use):

  | Plane | Section title | Emphasise |
  | ----- | ------------- | --------- |
  | START | You told us capacity forecasting is where it hurts. Here is what it looks like solved. | `Here is what it looks like solved.` |
  | START | What you told us - and what we did about it. | `and what we did about it.` |
  | START | The name is the promise: cura + via | `cura + via` |
  | START | Our vision & mission | (in-card) `capacity never decides who waits` |
  | START | Three hospitals, each running as a Frontier Firm | `Frontier Firm` |
  | START | One patient, one flow - humans and agents together | `humans and agents together` |
  | START | How an agent answers - the DC-INSIGHT pattern | `DC-INSIGHT` |
  | START | That is the stage set. Now watch it run. | `Now watch it run.` |
  | BACKSTAGE | We didn't just build a Frontier Firm. We became one. | `We became one.` |
  | BACKSTAGE | We ran a BVA on ourselves before writing a line of code | `BVA on ourselves` |
  | BACKSTAGE | We have organized our own transformation against the Success Framework. | `Success Framework` |
  | BACKSTAGE | How the product is built & shipped | `built & shipped` |
  | BACKSTAGE | Six lanes, one governed platform | `one governed platform` |
  | BACKSTAGE | Pressure-tested with real people, in real review sessions | `real people` |
  | BACKSTAGE | The Product Owner Agent handles the hard questions | `hard questions` |
  | BACKSTAGE | Your first frontier: capacity forecast in 90 days | `90 days` |

- **Resulting decision**: Implement `titleParts` (structured, tone-tagged) with a
  solid-colour fallback; populate the accent clause per the table above; extend
  the existing `SectionHeader` a11y tests for the multi-span heading name
  (`\s*`-tolerant matcher).

### Workstream C - Backstage gap analysis (change 8)

Mockup BACKSTAGE parts vs app parts:

| Mockup part | App coverage | Action |
| ----------- | ------------ | ------ |
| BVA ("BVA on ourselves") | none (was START) | **Add** (change 2) |
| Success Framework | `success-framework` | keep |
| DevSecOps ("built & shipped") | `devsecops-loop` | keep |
| Six lanes, one governed platform | `solution-design` (IQ planes) - different framing | **KEEP as-is (D1)** - do not add |
| Review sessions ("real people") | `review-sessions` | keep |
| Product Owner Agent ("hard questions") | `po-classes` | keep |
| 90-day ("first frontier") | none (was START) | **Add** (change 3) |
| (app extra) Digital Feedback Loop | `feedback-loop` | keep (not in mockup; retained) |
| (app extra) IQ solution-design deep model | `solution-design` | keep |

- **My initial finding**: `solution-design` already covers "one governed platform",
  so no six-lane gap.
- **Agent review (ux)**: the app's `solution-design` models the **Microsoft IQ
  planes** (work / process / foundry / fabric / gov / sec), a different framing
  from the mockup's **six delivery lanes**; ux suggested adding a concise six-lane
  orientation section.
- **USER DECISION (D1, locked)**: **Keep the existing Frontier Architecture
  (`solution-design`) exactly as-is; do NOT add a six-lane section.** The only
  net-new BACKSTAGE parts are BVA (change 2) and 90-day (change 3). No existing
  BACKSTAGE content or charts are touched.

**Resulting proposed BACKSTAGE order**:
`company(intro) -> bva -> success-framework -> feedback-loop -> solution-design
-> devsecops-loop -> review-sessions -> po-classes -> ninety-day`.

- **USER DECISION (D2, locked)**: 90-day placed at the very **end** of BACKSTAGE
  (mockup order; natural CTA).
- **Watch-out (ux)**: The Backstage sub-nav grows to 8 tabs - validate overflow,
  keyboard tabbing, and localized label widths.

### Workstream D - context-ask story-typing (change 9, DOC ONLY)

The Product Owner Agent review produced a 30-item inventory mapping each
section's clickable context ask to the four knowledge classes
(A retrieveCorpus / B liveProof / C costAnswer / D ontologyQuery), plus refusals
and a validation-story shape. This is captured as a backlog for a **separate
sprint** - no implementation now.

**Validation story shape** (per ask):

> **As a** C-level or hospital-ops user, **I want** to click `<context ask>` in
> `<section>`, **so that** I get a cited PO Agent answer without leaving the
> narrative.
> **Acceptance**: answer returns `GroundedChunk[]` from the expected class
> (A/B/C/D); every claim cites `sourceRef`; class D includes `conceptRef` +
> `goldBinding`; a failed live-proof returns `partial` / `requires-validation`,
> never uncited demo copy.

**Context-ask inventory** (source class in brackets; `!` = requires-validation):

- START / Hero: "Is this real, safe, and not a medical device?" [A (+B)];
  "Where does our data live?" [A + B].
- START / Challenger: "Which review session raised this concern?" [A];
  "What product decision changed because of this feedback?" [A].
- START / Vision: "Why cura + via?" [A]; "Which promises are non-negotiable:
  Swiss, human, advisory?" [A].
- START / Work-chart: "How does Curavias change the org chart into a work chart?"
  [A]; "Why is this a Frontier Firm, not a dashboard?" [A].
- START / Hospitals: "Why these three synthetic hospitals?" [A + D]; "Which
  agents run each hospital, and what can they do?" [A + B].
- START / Patient-path: "What signal -> recommendation -> action -> HITL gate
  applies here?" [A + D]; "Is 102% -> 94% computed or narrative?" [D + A] `!`.
- BACKSTAGE / Company: "What exactly is Curavias?" [A]; "Which PROD surfaces
  prove this exists?" [B + A].
- BACKSTAGE / BVA: "What are ROI, payback, TCO, and confidence band?" [C + A];
  "Which value lever drives the build decision?" [C + A].
- BACKSTAGE / Success-framework: "How did one human plus agents deliver this?"
  [A]; "Can we prove the sprint/PR claims?" [A] `!`.
- BACKSTAGE / Feedback-loop: "For this domain, what signal/action/outcome is
  governed?" [A + D]; "Are outcomes measured today?" [D/B] `!`.
- BACKSTAGE / Solution-design: "Which IQ capabilities are MVP vs roadmap?" [A];
  "Which capabilities are live in PROD now?" [B + A].
- BACKSTAGE / DevSecOps-loop: "Where are the human approval gates?" [A]; "What is
  actually deployed and healthy?" [B].
- BACKSTAGE / Review-sessions: "Who validated this and what changed?" [A]; "What
  risks remain before customer adoption?" [A].
- BACKSTAGE / PO-classes: "Which class answers my question?" [A]; "Show the
  citation shape for ontology answers." [A + D].
- BACKSTAGE / Ninety-day: "What happens in days 0-30, 30-60, 60-90?" [A]; "What
  must be live before claiming value?" [B + C + D].

**Do NOT story-type as grounded yet** (PO refusals): "Will our hospital reach 94%
occupancy?" (needs customer data); "Guarantee ROI/payback for us" (class C
refuses beyond ROM/feed); "Show real patient examples" (PHI refusal); "Is this
legally certified for clinical use?" (status only, not a legal-certification
guarantee).

## 4. Architecture and component impact

- `start-content.ts` - shrink `StartSectionId` union + `START_SECTIONS` to the
  six target sections (remove `cio-why-now`, `ninety-day`, `bva`).
- `StartView.tsx` - drop the three sections from `SECTION_META` + `sectionBody()`.
- `BackstageSubNav.tsx` - add `bva` at `[0]`, `ninety-day` at end, optional
  `six-lanes` (D1); add nav i18n label keys.
- `BackstageView.tsx` - add renderers for the moved sections via thin wrappers
  (`BackstageBvaSection`, `BackstageNinetyDaySection`) that reuse the existing
  START bodies unchanged.
- `shared/narrative/SectionHeader.tsx` - add `titleParts` structured API +
  optional heading-level prop + solid-colour gradient fallback.
- `shared/narrative/NarrativeShell.tsx` - make `sectionFull` opt-in; add the
  shared token-based header->body wrapper; convert residual `vh` to `svh`.
- `shared/narrative/showcase-styles.ts` - reuse `SHOWCASE_ACCENT` for the header
  gradient.
- `i18n/{en,de,fr,it}.json` - fill vision + challenger + gloss-label gaps; add
  moved-section + optional six-lane keys.

## 5. Testing and verification strategy (TDD-first)

- **Registry tests** (`start-content.test.ts`): update the asserted section order
  to the six-section target; add a Backstage-parts order test.
- **Section tests** (`StaticNarrativeSections.test.tsx`,
  `BvaDecisionSection.test.tsx`): update testids/nav expectations for the moved
  sections; add Backstage render tests for the BVA + 90-day wrappers.
- **SectionHeader tests**: add cases for `titleParts` (accent span present, one
  heading element, no `aria-hidden`, `\s*`-tolerant accessible-name match).
- **i18n test**: fail on any missing key across en/de/fr/it for START + BACKSTAGE.
- **Spacing**: snapshot/DOM assertions on the shared header->body wrapper gap; no
  min-height on non-opt-in sections.
- **a11y**: axe AA per section (existing `axe-section.js`), incl. gradient-heading
  contrast fallback and the patient-visual accessible name + mobile scroll.
- **Live verification**: `tsc --noEmit`, full START vitest suite, and Playwright
  screenshots at `http://localhost:5173/start` + `/backstage` in all four locales.
- **Gates reminder**: vitest/npm exits 1 even on success - verify by the
  "N passed" text, not exit code.

## 6. Sequencing

1. Workstream B first (changes 6 + 7) - the shared spacing + header kit both
   planes depend on, lowest-risk, highest-leverage.
2. Workstream A (changes 1-4) - START restructure on top of the new kit.
3. Workstream C (change 8) - Backstage adds (BVA + 90-day wrappers only; the
   existing Frontier Architecture / `solution-design` is kept as-is per D1).
4. Change 5 (i18n) folded into each step as strings move, then a final coverage
   sweep.
5. Change 9 - written to a separate story backlog; no code this sprint.

## 7. Decisions (resolved by user 2026-08-07)

- **D1 - six-lane Backstage section**: **Rejected.** Keep the existing Frontier
  Architecture (`solution-design`) as-is; do not add a six-lane section.
- **D2 - 90-day placement**: **End of Backstage** (mockup order).
- **D3 - Start urgency signpost**: **None.** Remove Why-now and add nothing to
  the other sections.
- **D4 - BVA number framing**: **Keep the real data-bound figures** (no mockup
  ROM regression); BVA + ROI additional-facts refresh is a separate later
  follow-up.

## 8. Risks

- Backstage sub-nav overflow / keyboard / localized-width at 8-9 tabs (change 8).
- Moving BVA + 90-day breaks tests that assert START section order/testids -
  updated in the same change (section 5).
- Gradient headings must not rely on colour alone and must pass forced-colors
  fallback (change 7).
- i18n gloss governance must stay auditable (verbatim quote unchanged; labels
  localized) (change 5).
