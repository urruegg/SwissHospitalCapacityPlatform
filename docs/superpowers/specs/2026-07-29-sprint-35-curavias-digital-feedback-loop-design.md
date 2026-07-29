# Sprint 35: Curavias Digital Feedback Loop in Backstage - Design

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-29 |
| **Author** | Urs Rueegg (with GitHub Copilot) |
| **Status** | Approved for planning |
| **Previous Version** | n/a (initial design) |
| **Sprint** | Sprint 35 - Curavias Digital Feedback Loop |
| **Issue** | [#536](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/536) |
| **Lane** | Experience (`apps/hcc-app-fluent/**`) |

---

## 1. Goal

Add an executive-facing **Digital Feedback Loop** as a distinct, full-width
section in **Backstage > Story**. The section shows how real operational signals
become grounded recommendations through Microsoft IQ, return to hospital
operations under human control, and produce measured outcomes that improve the
next decision.

This is an additional part of the Backstage story. It is **not** a fourth
Backstage tab and does not replace the existing Story, Evidence, or Roles &
access content.

## 2. Approved design decisions

The 2026-07-29 Superpowers brainstorm established these binding decisions:

* **D1 - Audience:** executive and customer presentation, with enough evidence
  detail to support architecture and product-owner questions.
* **D2 - Composition:** a "Living Infinity" layout with four Curavias domains
  around a central Microsoft IQ core.
* **D3 - Placement:** a separate full-width section inside the existing
  Backstage Story tab; no new Backstage navigation item.
* **D4 - Domain language:** lead with Curavias healthcare language and retain
  the corresponding Microsoft Digital Feedback Loop labels.
* **D5 - Causality:** cyan observations flow inward, a green proposed action
  flows outward, and an amber measured outcome returns to close the loop.
* **D6 - IQ center:** Work IQ, Foundry IQ, Fabric IQ, Process IQ, and Governance
  IQ are visible and causally connected, not decorative badges.
* **D7 - Copilot:** selecting a domain routes context to the existing Backstage
  `product-owner-agent` rail. The visual does not implement a second chat.
* **D8 - Safety:** Product Owner Agent output stays grounded, cited,
  advisory-only, PHI-free, and subject to human decision.
* **D9 - Motion:** all-loop and selected-loop modes support play/pause and
  `prefers-reduced-motion`; comprehension never depends on motion alone.
* **D10 - Reuse:** the same visual component can render in an unframed
  presentation route without duplicating domain data or behavior.

## 3. Experience architecture

### 3.1 Backstage composition

`StoryTab` remains the Story composer. It mounts a new
`DigitalFeedbackLoopSection` between the existing delivery narrative and the
Copilot roster. This position connects "how Curavias ships" to "how Curavias
learns" before the story introduces the agent roster and platform pillars.

The section has three visible regions:

1. **Section header and controls:** title, one-line purpose, simulation status,
   all-loop/selected-loop segmented control, and play/pause icon button.
2. **Living Infinity canvas:** four selectable domain nodes, central Microsoft
   IQ core, persistent orientation rails, and animated signal/action/outcome
   markers.
3. **Flow legend:** Data points -> Microsoft IQ -> Proposed action -> Human
   approval -> Measured outcome.

The Product Owner Agent remains the shell's existing right-side `AgentPlane`.
It is not nested inside the section.

### 3.2 Standalone presentation

`/present/feedback-loop` renders the same `DigitalFeedbackLoop` component in a
full-bleed presentation composition outside `AppShell`. It keeps the Curavias
brand mark, simulation controls, synthetic/no-PHI badge, and the explanatory
legend. It omits Backstage navigation and the Agent plane.

The standalone route is a presentation surface, not a second product workflow.
Domain selection remains available, but Copilot context routing is disabled
because no `CopilotRailProvider` is mounted there.

## 4. Domain and IQ model

The visual reads from a typed, immutable domain catalog. Display strings use
i18n keys; IDs and context values remain language-neutral.

| Domain | Curavias label | Microsoft label | Signal | Proposed action | Outcome | Active IQ |
| ------ | -------------- | --------------- | ------ | --------------- | ------- | --------- |
| `care-ecosystem` | Engage care network | Engage customers | referrals, partner capacity | coordinate placement | continuity, access | Work, Fabric, Process, Governance |
| `command-center` | Optimize patient flow | Optimize operations | occupancy, 72-hour demand | rebalance, coordinate | wait time, utilization | Foundry, Fabric, Process, Governance |
| `frontier-workforce` | Empower care teams | Empower employees | skills, staffing, workload | mobilize capacity | workload, adoption | Work, Fabric, Process, Governance |
| `care-innovation` | Transform care delivery | Transform products | outcomes, telemetry | improve pathway | quality, adoption | Foundry, Fabric, Process, Governance |

Each domain also owns:

* a stable visual position and accessible label;
* a Product Owner context label;
* a grounded recommendation card compatible with `GroundedReco`;
* citation references to repository or governed evidence;
* a deterministic animation-path ID.

No runtime clinical values or PHI are embedded in this catalog. The sprint uses
synthetic explanatory labels only.

## 5. Component boundaries

### 5.1 `feedback-loop-model.ts`

Owns `FeedbackLoopDomain`, `FeedbackLoopDomainId`, `IqLayer`, mode types, and
the four-domain catalog. It has no React, rail, or browser dependency.

### 5.2 `DigitalFeedbackLoop.tsx`

Owns the visual and interaction state:

* selected domain;
* `all` or `selected` stream mode;
* playing or paused state;
* keyboard selection and focus state;
* the SVG paths and motion markers.

Its public contract is presentation-only:

```ts
interface DigitalFeedbackLoopProps {
  domains: readonly FeedbackLoopDomain[];
  onDomainSelect?: (domain: FeedbackLoopDomain) => void;
  presentationMode?: boolean;
}
```

It must not import `useCopilotRail`, `useConversation`, or agent-runtime code.

### 5.3 `DigitalFeedbackLoopSection.tsx`

Adapts the visual to Backstage. It maps a selected domain to a
`ContextInsight` and `GroundedReco`, then calls the existing
`useCopilotRail().openWithReco(...)`. This is the only new Product Owner rail
integration point.

The context envelope carries stable, non-PHI fields:

```ts
{
  domainId,
  signalIds,
  proposedActionId,
  outcomeId,
  iqLayers,
  source: 'backstage-digital-feedback-loop'
}
```

### 5.4 `FeedbackLoopPresentationView.tsx`

Provides the unframed `/present/feedback-loop` composition and delegates all
visual behavior to `DigitalFeedbackLoop`.

## 6. Interaction and state flow

1. The section initially shows all four loops and selects `command-center` as
   the narrative default without opening the Copilot rail.
2. The user clicks or keyboard-activates a domain.
3. `DigitalFeedbackLoop` updates its selected state and invokes
   `onDomainSelect(domain)`.
4. `DigitalFeedbackLoopSection` creates the typed `ContextInsight` and the
   domain's grounded `GroundedReco`.
5. `openWithReco` opens or updates the existing Backstage Product Owner Agent
   rail.
6. The rail shows status/provenance, recommendation text, citations, follow-up
   prompts, and the explicit advisory/human-decision posture.
7. In selected-loop mode, only the selected domain's markers animate; static
   rails for all domains remain visible for orientation.

Switching domains replaces the active context and recommendation atomically.
There is no network call required for the deterministic demonstration card.
Free-form questions continue through the existing Product Owner Agent
conversation path.

## 7. Visual and motion behavior

The visual uses Fluent UI v9 primitives, existing Curavias design-system
recipes, and semantic theme tokens. The dominant colors are:

* Curavias green `#17B890` for proposed actions;
* Curavias blue `#365B7D` for structure and IQ framing;
* Curavias cyan `#1FA9D6` for inbound observations;
* Curavias amber `#E8A200` for measured outcomes.

Static rails and labels carry meaning when animation is paused. The SVG is
decorative where the adjacent interactive domain controls already expose the
same semantics. Domain controls are real Fluent buttons with stable dimensions,
visible focus, selected state, and concise accessible names.

At narrow widths the composition changes from the spatial infinity canvas to a
stacked sequence: Microsoft IQ summary first, followed by the four domain
controls. No label is placed over an SVG path, and no horizontal page scroll is
introduced.

When `prefers-reduced-motion: reduce` is active, markers render at meaningful
rest positions and do not animate. Play/pause remains operable and reports its
state through its accessible name.

## 8. Empty, error, and fallback behavior

* **Empty domain catalog:** render a compact unavailable state with no controls;
  do not render an empty SVG.
* **Missing recommendation mapping:** select the domain visually but do not
  open the rail; log a development warning and preserve the prior rail state.
* **Animation unavailable:** static rails, labels, and flow legend remain the
  complete explanation.
* **Standalone route:** never assumes the rail context exists.
* **Translation fallback:** English keys provide the fallback; IDs are never
  shown as customer-facing labels.

## 9. Accessibility and responsible UI

* The section is a labelled landmark with a level-3 heading under Story.
* Domain selection uses buttons, not clickable SVG groups.
* `aria-pressed` communicates the selected domain.
* Tab reaches every domain and control once; Enter/Space activates.
* Color is reinforced by SIGNAL, ACTION, and OUTCOME text labels.
* Live animation does not generate repetitive screen-reader announcements.
* Serious or critical WCAG 2.1 AA axe findings block completion.
* Product Owner recommendations retain citations, provenance, advisory text,
  and human-approval semantics from the existing rail contract.

## 10. Verification strategy

### Unit and component checks

* Catalog contains exactly four unique domain IDs and all five IQ layers are
  represented.
* Selecting a domain updates `aria-pressed` and calls `onDomainSelect` once.
* Mode and play controls update accessible state.
* Reduced motion suppresses animated markers.
* Backstage adapter emits the expected non-PHI context envelope and grounded
  recommendation.

### Playwright checks

* `/backstage/story` contains one distinct feedback-loop section and keeps only
  the three existing Backstage navigation items.
* Each domain selection opens or updates the `product-owner-agent` rail with the
  matching context and citations.
* All-loop, selected-loop, play, and pause controls work.
* `/present/feedback-loop` renders the reusable unframed composition.
* Desktop and narrow screenshots show no overlap or clipping.
* Axe reports no serious or critical WCAG 2.1 AA violation on both routes.

### App gates

From `apps/hcc-app-fluent`:

```powershell
npm test
npm run lint
npm run build
npx playwright test tests/e2e/feedback-loop.spec.ts
npx playwright test tests/e2e/a11y.spec.ts
```

## 11. Delegation model

Delivery uses `subagent-driven-development` after the implementation plan is
approved. Shared types, selectors, and public props land first. Three workers
then operate on bounded file sets:

1. **WS-A - Visual model and component.** Catalog, presentation component,
   controls, motion, and component tests.
2. **WS-B - Backstage and Product Owner bridge.** Story composition, rail
   adapter, i18n, and context-routing tests.
3. **WS-C - Presentation and verification.** Standalone route, responsive
   behavior, Playwright interaction/visual/a11y coverage.

Each worker starts from current `main`, uses TDD, runs focused checks, and opens
a human-reviewed PR. No subagent self-merges. WS-B and WS-C depend on the shared
WS-A contract; they may proceed in parallel only after that contract lands.

## 12. Scope and traceability

This sprint advances existing requirements only:

* `FR-POA-001`, `FR-POA-002`, `FR-CX-006`;
* `FR-UX-001`, `FR-UX-004`;
* `NFR-POA-001`, `NFR-POA-004`;
* `NFR-UX-001` through `NFR-UX-004`.

No new FR/NFR ID, agent prompt, backend service, data contract, Fabric asset,
Azure resource, or infrastructure change is introduced. The prototype files in
ignored `.superpowers/` state are design evidence only and are not production
inputs.

## 13. Definition of Done

* The loop is a separate full-width Backstage Story section, not a new tab.
* All four domains expose signal, proposed action, and measured outcome.
* Microsoft IQ visibly includes all five agreed IQ layers.
* Every domain updates the existing Product Owner Agent rail with matching,
  cited, advisory context.
* All-loop, selected-loop, pause, and reduced-motion behavior pass tests.
* Desktop and narrow layouts remain readable without overlap.
* Standalone presentation reuses the same component and catalog.
* Unit/component, lint, build, Playwright, screenshot, and axe gates pass.
* Delivery remains experience-lane only and uses synthetic, non-PHI content.
