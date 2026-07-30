# Sprint 36: Curavias Backstage - full showcase (Solution design + Frontier-Firm narrative) - Design

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-29 |
| **Author** | Urs Rueegg (with GitHub Copilot) |
| **Status** | Approved for planning |
| **Previous Version** | 1.0.0 (Solution-design section only; extended to the full Backstage showcase - keeps DFL + SD, adds the Frontier-Firm narrative) |
| **Sprint** | Sprint 36 - Curavias Backstage full showcase |
| **Issue** | [#540](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/540) |
| **Lane** | Experience (`apps/hcc-app-fluent/**`) + a governance reconciliation workstream (`docs/SD.md`, `docs/GLOSSARY.md`) |

---

## 1. Goal

Deliver the **full Backstage Story showcase** - the "company behind the product"
narrative - as distinct, full-width sections in **Backstage > Story**. This sprint
**keeps** the Digital feedback loop ([Sprint 35](2026-07-29-sprint-35-curavias-digital-feedback-loop-design.md),
merged) and the **Solution design - IQ operating model** board (this spec,
sections 2-14), and **adds** the product-marketing Frontier-Firm Backstage
narrative (section 15), all routing to the docked Product Owner Agent rail.

It is additional content within the existing Backstage Story tab. It is **not** a
fourth Backstage tab; the Evidence and Roles tabs are unchanged.

### 1.1 Full Backstage Story composition (approved order)

| # | Section | Source | Notes |
| - | ------- | ------ | ----- |
| 1 | Backstage hero - "We didn't just build a Frontier Firm. We became one." | new (B1) | intro |
| 2 | Success Framework - 4 transformation principles + numbers (1 human, 29 sprints, SIT->PROD, 100% human-merged) | new (B2) | the transformation |
| 3 | Digital feedback loop - signals -> Microsoft IQ -> governed action | Sprint 35 (kept) | the living system |
| 4 | Solution design - IQ operating model (5 IQ layers + Governance/Security lanes) | this spec sections 2-14 | primary architecture; six-lanes folded in as a companion |
| 5 | DevSecOps loop - DEV<->OPS + HITL gate + DEV->SIT->PROD | new (B3) | how it is built |
| 6 | Review sessions & people - 7 sessions + named practitioners | new (B5) | pressure-tested |
| 7 | Product Owner Agent - the four knowledge classes (A/B/C/D) | new (B6) | explains the docked rail |

**Overlap resolutions:** the PM "six lanes" architecture (B4) is **folded into the
Solution design section** (row 4) as a compact companion mapping to the IQ
layers/lanes - not a competing diagram; the **DevSecOps loop** (row 5) stays its
own section (the build-process visual), complementary to the DevSecOps IQ layer;
the **PO knowledge classes** (row 7) are an explainer for the already-docked rail.

Sections 2-14 below specify the Solution-design board (unchanged from v1.0.0);
section 15 specifies the added Frontier-Firm Backstage narrative sections.

## 2. Approved design decisions

Established across the 2026-07-29 Superpowers visual-companion iterations (v1-v8):

* **D1 - Placement:** a separate full-width section inside the existing Backstage
  Story tab; no new Backstage navigation item; sibling to the feedback loop.
* **D2 - Model shape:** five stacked IQ layers between two cross-cutting lanes.
* **D3 - Layers and order:** `Work IQ -> Process IQ -> Foundry IQ -> Fabric IQ ->
  DevSecOps IQ`. Process IQ is its **own layer** (not a spine).
* **D4 - Lanes:** a **Governance** lane (left) and a **Security** lane (right),
  each spanning every layer.
* **D5 - Capability tiers:** each layer/lane lists **MVP** (delivered, green
  check badges) and **Target** (roadmap, dashed badges) capabilities.
* **D6 - One card language:** every card (5 layers + 2 lanes) is a white surface
  with a colored left accent, a tinted icon tile, and tinted check-marked
  capability badges color-coded to that card.
* **D7 - Brand + Fluent:** Curavias brandkit tokens + Fluent UI v9 primitives +
  Fluent icons (mapped to `@fluentui/react-icons`); the Curavias mark heads the
  section.
* **D8 - Context routing:** the section header, every plane header, and every
  capability badge route a typed context to the existing `product-owner-agent`
  rail.
* **D9 - Safety:** PO Agent output stays grounded, cited, advisory-only,
  PHI-free; a human decides.
* **D10 - Reuse:** the same component renders in a standalone presentation route.

## 3. Color and icon system (brandkit-exact)

Colors are the Curavias brandkit roles; text colors are AA-safe on white.

| Scope | Accent | Text | Fluent icon (`@fluentui/react-icons`) |
| ----- | ------ | ---- | ------------------------------------- |
| Work IQ | Green `#17B890` | `#12765F` | `Board` |
| Process IQ | Teal `#1FA9D6` | `#176C8A` | `Flow` |
| Foundry IQ | Blue `#365B7D` | `#365B7D` | `Bot` |
| Fabric IQ | Teal `#1FA9D6` | `#176C8A` | `Database` |
| DevSecOps IQ | Slate `#6B7A88` | `#4A5A68` | `BranchFork` |
| Governance lane | Violet `#5A6CF0` | `#4A46C7` | `ClipboardTaskList` |
| Security lane | Red `#E30613` | `#C70713` | `ShieldKeyhole` |
| MVP badge | Green | Green | `CheckmarkCircle` |
| Target badge | (dashed, per-layer color) | per-layer | `Target` |
| Section / model | Blue-cyan mark | - | `Layer` + Curavias mark |
| PO Agent rail | Blue `#365B7D` | - | `PersonChat` |

Process IQ and Fabric IQ currently share teal. Full five-way distinctness is an
optional refinement (e.g. Fabric to a deeper cyan) and is **not** blocking.

## 4. IQ-model catalog (data)

The section reads from a typed, immutable catalog. Display strings use i18n keys;
IDs and context values remain language-neutral. No PHI, no live clinical values.

| Plane | Curavias tagline | MVP capabilities | Target capabilities |
| ----- | ---------------- | ---------------- | ------------------- |
| `work` | experience & role-based control plane | Fluent UI command center; In-app Copilot rail; Role surfaces (6 copilots); Agent-boss HITL approval | Work IQ M365 context |
| `process` | patient-flow journey through the role copilots | OOA->DCA->BMCA->ORSA->SBA->CSA; Golden-thread steering; Cross-role handoffs | What-if simulation overlay |
| `foundry` | orchestrated role agents, closed-loop learning | Copilot orchestrator; Agents per role (x6 + PO + BVA); Grounded on GroundedChunk; Closed-loop learning | - |
| `fabric` | ontology, semantic data & steering signals | Medallion + Direct Lake; Data Agents (`da_hospital_capacity`); Data Quality gate + trust score | Ontology (GA); KIS / Epic / SAP ingestion |
| `devsecops` | a product team of agents that build agents | Human agent boss (gated); GitHub delivery plane + CLI Copilot; MCP allow-list; Agents build their Foundry-IQ relatives | - |
| `gov` (lane) | policy & compliance | Swiss residency; Advisory-only; No-PHI; Evidence audit; DSG / CH-C01..C10 | - |
| `sec` (lane) | Zero Trust protection | Zero Trust; Managed identity; RBAC least-priv; Key Vault secrets; Private endpoints | - |

The **Process IQ golden thread** narrative is `Medicine A -> 102% occupancy in
72h -> site -16 beds` - one signal steered end to end.

## 5. Component boundaries

### 5.1 `solution-design-model.ts`

Owns `IqPlaneId`, `IqPlane`, `Capability`, `CapabilityTier` (`mvp` | `target`),
the `IQ_PLANES` catalog, and the `SolutionDesignContext` envelope type. No React,
rail, or browser dependency.

### 5.2 `SolutionDesignBoard.tsx`

Owns the visual and local interaction state (selected context; active card). Its
public contract is presentation-only:

```ts
interface SolutionDesignBoardProps {
  planes: readonly IqPlane[];
  onContextSelect?: (ctx: SolutionDesignContext) => void;
  presentationMode?: boolean;
}
```

It must not import `useCopilotRail`, `useConversation`, or agent-runtime code.
Headers and badges are real Fluent-styled `<button>` elements with `aria-pressed`.

### 5.3 `SolutionDesignSection.tsx`

The Backstage adapter. Maps a selected context to a `ContextInsight` +
`GroundedReco` and calls the existing `useCopilotRail().openWithReco(...)`. This
is the only new Product Owner rail integration point.

The context envelope carries stable, non-PHI fields:

```ts
{
  scope,            // 'model' | 'work' | 'process' | 'foundry' | 'fabric' | 'devsecops' | 'gov' | 'sec'
  kind,             // 'plane' | 'capability'
  capabilityId,     // present when kind === 'capability'
  tier,             // 'mvp' | 'target' when kind === 'capability'
  source: 'backstage-solution-design'
}
```

### 5.4 `SolutionDesignPresentationView.tsx`

Provides the unframed `/present/solution-design` composition and delegates all
visual behavior to `SolutionDesignBoard`.

## 6. Interaction and context flow

1. The section initially selects the `work` plane header and shows its grounded
   answer, without opening the Copilot rail on first paint.
2. The user clicks or keyboard-activates a **section header**, **plane header**,
   or **capability badge**.
3. `SolutionDesignBoard` updates its selected state and invokes
   `onContextSelect(context)`.
4. `SolutionDesignSection` builds the typed `ContextInsight` + grounded
   `GroundedReco` and calls `openWithReco`.
5. The existing Backstage Product Owner Agent rail opens or updates, showing the
   routed context, a grounded answer with status/provenance, citations, an
   advisory note, and follow-up prompts.
6. Selecting another element replaces the active context atomically; the active
   card raises and the selected control shows `aria-pressed`.

A plane context yields a plane-level answer; a capability context yields a
capability-level answer carrying its MVP/Target tier. Free-form questions
continue through the existing Product Owner Agent conversation path.

## 7. Backstage composition and standalone reuse

`StoryTab` mounts `<SolutionDesignSection />` as its own full-width section,
after the Digital feedback loop section, before the Copilot roster. `NAV_ITEMS`
and `WIDGETS` in `BackstageView` are unchanged (no new tab).

`/present/solution-design` renders `SolutionDesignBoard` in a full-bleed
composition outside `AppShell` (Curavias mark, section title, legend). Domain
selection remains available; rail routing is disabled there because no
`CopilotRailProvider` is mounted.

## 8. Empty, error, and fallback behavior

* **Empty catalog:** render a compact unavailable state; do not render an empty
  board.
* **Missing capability/answer mapping:** select the element visually but do not
  open the rail; log a development warning and preserve the prior rail state.
* **Standalone route:** never assumes the rail context exists.
* **Translation fallback:** English keys provide the fallback; IDs are never
  shown as customer-facing labels.

## 9. Accessibility and responsible UI

* The section is a labelled landmark with a level-3 heading under Story.
* Headers and badges are buttons; `aria-pressed` marks the active context.
* Tab reaches every header and badge once; Enter/Space activates.
* Color is reinforced by MVP/Target text and the check/target icons.
* Serious or critical WCAG 2.1 AA axe findings block completion.
* Product Owner recommendations retain citations, provenance, advisory text, and
  human-decision semantics from the existing rail contract.
* At narrow widths the three-column board (Governance lane / layers / Security
  lane) stacks to a single column with the lanes above and below the layers; no
  label overlaps and no horizontal page scroll is introduced.

## 10. Model reconciliation (governance workstream)

The v8 model **inverts** the current [`docs/SD.md`](../../SD.md) §2, where
Governance IQ is a stacked layer and Process IQ is a spine. WS-D reconciles
`docs/SD.md` §2 and `docs/GLOSSARY.md` to the new model - Process IQ as a layer;
Governance and Security as cross-cutting lanes - so the canonical docs and the
Backstage visual agree (`NFR-DOC-001`). This is an additive/refining doc change
(MINOR version bump on both docs); it introduces no new FR/NFR ID and renames no
existing anchor. If the reviewer prefers, WS-D may be split to a fast follow-on
PR, but the section must not ship asserting a model the SD doc contradicts.

## 11. Verification strategy

### Unit and component checks

* Catalog has 5 layers + 2 lanes with unique IDs; every plane has >= 1 MVP
  capability; tiers are `mvp` | `target`; no PHI-shaped strings.
* Selecting a plane header emits a `plane` context once and sets `aria-pressed`.
* Selecting a badge emits a `capability` context carrying `capabilityId` + tier.
* The Backstage adapter maps each context to the expected non-PHI envelope +
  grounded recommendation and calls `openWithReco`.

### Playwright checks

* `/backstage/story` contains one distinct solution-design section and keeps
  only the three existing Backstage navigation items.
* Clicking the section header, a plane header, and a capability badge each opens
  or updates the `product-owner-agent` rail with the matching context and
  citations.
* `/present/solution-design` renders the reusable unframed composition.
* Desktop and narrow screenshots show no overlap or clipping.
* Axe reports no serious or critical WCAG 2.1 AA violation on both routes.

### App gates

From `apps/hcc-app-fluent`:

```powershell
npm test
npm run lint
npm run build
npx playwright test tests/e2e/solution-design.spec.ts
npx playwright test tests/e2e/a11y.spec.ts
```

## 12. Delegation model

Delivery uses `subagent-driven-development` after the plan is approved. Shared
types, selectors, and public props land first (WS-A). Then:

1. **WS-A - Catalog + board component.** `solution-design-model.ts`,
   `SolutionDesignBoard.tsx`, and component tests.
2. **WS-B - Backstage + PO bridge.** `SolutionDesignSection.tsx`, `StoryTab.tsx`,
   i18n, and context-routing tests.
3. **WS-C - Presentation + verification.** Standalone route, responsive
   behavior, Playwright interaction/visual/a11y coverage.
4. **WS-D - Governance reconciliation.** `docs/SD.md` §2 + `docs/GLOSSARY.md`.
5. **WS-E - Frontier-Firm narrative sections.** `backstage-narrative-content.ts`
   * the B1/B2/B3/B5/B6 section components + the six-lanes companion inside the
   Solution design section + i18n + Playwright/a11y (section 15).

Each worker starts from current `main`, uses TDD, runs focused checks, and opens
a human-reviewed PR. No subagent self-merges. WS-B and WS-C depend on the WS-A
contract; WS-D is independent and may run in parallel; WS-E depends on WS-B (the
StoryTab mount point) and reuses the SD context-routing pattern.

## 13. Scope and traceability

Advances existing requirements only:

* `FR-POA-002`, `FR-CX-006`;
* `FR-UX-001`, `FR-UX-004`;
* `NFR-POA-001`, `NFR-POA-004`;
* `NFR-UX-001` through `NFR-UX-004`;
* `NFR-DOC-001` (WS-D reconciliation);
* `FR-GOV-004` (review-session governance evidence, section 15.5).

No new FR/NFR ID, agent prompt, backend service, data contract, Fabric asset,
Azure resource, or infrastructure change is introduced. The prototype files in
ignored `.superpowers/` state are design evidence only and are not production
inputs.

## 14. Definition of Done

* The full Backstage Story renders the seven-section composition of §1.1 in order
  (hero, Success Framework, Digital feedback loop [kept], Solution design [kept],
  DevSecOps loop, Review sessions & people, PO knowledge classes); still no fourth
  tab, Evidence + Roles unchanged.
* The Digital feedback loop (Sprint 35) and Solution design sections are preserved
  and unbroken.
* Five IQ layers + Governance and Security lanes render with per-layer MVP/Target
  badges and the one shared card language; the six-lanes companion maps into it.
* The section header, every plane header, every capability badge, and every
  narrative section route matching, cited, advisory context to the existing
  Product Owner Agent rail.
* Desktop and narrow layouts remain readable without overlap.
* Standalone presentation reuses the same component and catalog.
* Review-session external links use `rel="noopener"`; synthetic/no-PHI +
  advisory-only stay visible.
* `docs/SD.md` + `docs/GLOSSARY.md` reconciled to the new model.
* Unit/component, lint, build, Playwright, screenshot, and axe gates pass.
* Delivery remains experience-lane (plus the scoped WS-D governance edit) and
  uses synthetic, non-PHI content.

## 15. Frontier-Firm Backstage narrative sections

These sections are added to the Backstage Story tab in the composition order of
§1.1, around the kept Digital feedback loop (Sprint 35) and Solution design
(sections 2-14) sections. Each is a focused Fluent v9 + Curavias design-system
component reading its copy from a typed `backstage-narrative-content.ts` model
(i18n keys; no PHI), and each routes to the docked Product Owner Agent rail using
the same `openWithReco` pattern as the Solution design section. Source content is
the product-marketing draft `docs/superpowers/ideas/Curavias-Frontier-Showcase.html`
(Backstage chapter), intaken as a reviewed BOM.

### 15.1 Backstage hero (B1)

"We didn't just build a Frontier Firm. We became one." An intro band with the
Curavias mark; no data binding.

### 15.2 Success Framework (B2)

Four transformation principles (organize around outcomes; human-agent teams;
trust & governance by design; evidence-first) plus a numbers panel (1 human, 29
sprints, SIT->PROD, 100% human-merged). The numbers are provenance-labelled
`as-built` facts, not live data.

### 15.3 DevSecOps loop (B3)

The DEV<->OPS build loop (plan/code/build/test <-> release/deploy/operate/monitor)
with the central HITL gate (PR + Issue + approved-to-apply) and the
DEV->SIT->PROD delivery strip. Rendered as an accessible Fluent/SVG figure with a
text-equivalent legend.

### 15.4 Six-lanes companion (B4, folded into section 4)

Not a standalone section: a compact six-lane strip (Experience, API & agent
runtime, Data platform, AI & decision, Integration, Governance) rendered inside
the Solution design section, each lane mapping to its IQ layer/lane - so there is
one architecture diagram, not two.

### 15.5 Review sessions & people (B5)

The seven documented review sessions (perspective challenged + date) and the
named-practitioners grid (name, competency, contribution, consented LinkedIn
link). External links open in a new tab with `rel="noopener"`. This is governance
evidence (`FR-GOV-004`).

### 15.6 Product Owner Agent knowledge classes (B6)

An explainer for the already-docked rail: the four knowledge classes (A Corpus,
B Live-proof, C Cost, D Ontology), with a CTA that opens the rail. No new agent
behavior.

Each narrative section carries `data-testid="backstage-<id>"`, is keyboard- and
screen-reader-accessible, passes axe at WCAG 2.1 AA, and keeps the synthetic/
no-PHI + advisory-only posture visible.
