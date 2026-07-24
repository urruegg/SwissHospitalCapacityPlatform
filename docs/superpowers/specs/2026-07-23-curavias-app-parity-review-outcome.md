# Curavias App Prototype Parity — Review Outcome

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft (review outcome) |
| **Previous Version** | 1.0.0 (added §7 Copilot agent interaction model; renumbered §8–§10) |
| **Target app** | `apps/hcc-app-fluent` |
| **Sprint** | [Sprint 20 — Curavias App UX Redesign](../../sprints/sprint-20-curavias-ux-redesign.md) |
| **Design spec** | [Curavias App — Prototype Parity Design](2026-07-21-curavias-app-prototype-parity-design.md) (v1.0.1, Approved) |
| **Baseline prototype** | `docs/superpowers/ideas/curavias-ux-ideas/prototype/` (locked) |
| **Deployed target** | `https://appsit.curavias.ch` (SIT, current branch build) |

> **Purpose.** Captures the evidence-based parity review that precedes the Sprint 20
> app-parity build, so the outcome is reviewable **outside the authoring session**.
> It records, per surface: the gap between the locked prototype and the deployed
> app, the locked `GroundedReco` data contract, the per-board data model, the
> **live-evidence data requirements for START and BACKSTAGE**, and the Fluent UI v9
> control mapping. The implementation plan is produced separately via
> `superpowers:writing-plans` and grounded in this document.

---

## 1. Method

* **Baseline** — the locked prototype surfaces (`prototype/surfaces/00-start.html`
  … `07-backstage.html`), the desired target design.
* **Target** — the deployed SIT app, navigated client-side (deep-links return an
  nginx 404; the SPA must be entered at root and navigated via in-app links).
* **Capture** — Playwright at 1440×960, Demo mode, role lens `HCC.Viewer`, `de`
  locale, `aggregated` scope. Screenshots + DOM/text/testid extraction per surface.
* **Scope reviewed** — all three acts: START, MAIN (6 role boards OOA/DCA/BMCA/
  ORSA/SBA/CSA), and BACKSTAGE.

Status legend: **MISSING** (in baseline, absent in target) · **PARTIAL** (reduced)
· **DIVERGENT** (semantically/visually different) · **OK** (at parity).

> Companion evidence: the full screen-by-screen dossier (per-surface gap tables,
> underlying functionality, Fluent mappings) lives in
> [`2026-07-23-curavias-app-parity-findings.md`](2026-07-23-curavias-app-parity-findings.md).

---

## 2. Per-surface parity summary

| Surface | Route | Parity | Headline gaps |
|---------|-------|--------|---------------|
| START | `/start` | ~20% | Role launcher only; hero, value KPIs, why-now decision table, patient-path, and Crisis card all missing |
| OOA | `/main/occupancy` | ~30% | Ward-pressure table + capacity-flow diagram + docked reco rail missing; board is 3 flat cards |
| DCA | `/main/discharge` | ~30% | Discharge worklist + ranked capacity-barriers board + reco rail missing |
| BMCA | `/main/bed-manager` | ~40%, conflicted | Two stacked boards (legacy S11 whiteboard over parity skeleton); consolidate, keep Power BI embed + eventstream |
| ORSA | `/main/or-steering` | ~25% | Elective-OR schedule table + ranked reslot levers missing |
| SBA | `/main/staffing` | ~25% | Coverage worklist (shift gaps) + ranked staffing levers missing |
| CSA | `/main/crisis` | ~0% | Whole board not deployed (route 404s); signal→scenario→probability pipeline + Cosmos scenario/run memory to build |
| BACKSTAGE | `/backstage` | ~60%, diverging up | Story tab under-delivers (stat tiles + build/maturation strips + copilot roster missing); Evidence + Roles tabs are real, repo-grounded additions to keep |

### Cross-cutting wiring findings (all MAIN boards)

* **Discarded reco promise.** Board components call `void routeInsight(insight, …)`
  and discard the returned reply; `rail-context` stores only the active insight,
  never the agent reply. The rail is therefore an empty chat drawer — clicking
  insights is visually inert. Shared bug across all boards.
* **Rail is the wrong Drawer type.** `copilot-drawer/Drawer.tsx` uses
  `type="overlay"` (floats + dims). The prototype rail is docked/persistent →
  `Drawer type="inline" position="end"`.
* **Boards are flat.** Each board is `Card` + `Text` + subtle `Button`. The
  prototype core is a **worklist table** + a **ranked-lever board** + a docked
  reco rail — those must be `DataGrid` + `List` + inline `Drawer`.
* **Data + agent seams exist and are correct.** `golden-source-client` reads live
  from `VITE_GOLDEN_SOURCE_URL` (Sprint 22 medallion) else synthesized `*_PINNED`
  flagged `simulated`; `agent-manifest`/agent-host returns a degraded mock when
  unset. Parity keeps both seams and enriches the payloads.

---

## 3. Locked data contract — `GroundedReco` v2

The flat `GroundedReply = { answer, citations, refused }` cannot render the
prototype's chip, reasoned read, numbered levers with heterogeneous impact chips,
and typed CTA. The parity contract adds a structured reco, transcribed from — and
fully exercised by — every prototype reco panel.

```ts
type Provenance = 'live' | 'simulated';
type ImpactTone = 'beds' | 'buffer' | 'time' | 'routing' | 'trust' | 'probability' | 'status';
type ChipTone   = 'over' | 'watch' | 'ok' | 'blocked' | 'pending' | 'ranked' | 'signal';
type CtaKind    = 'handoff' | 'action' | 'navigate';

interface RecoContextChip { subject: string; qualifiers?: string[]; status?: string; tone: ChipTone; }
interface RecoLever { text: string; impact?: { label: string; tone?: ImpactTone }; }
interface RecoCta   { label: string; kind: CtaKind; target?: AgentId | string; requiresApproval?: boolean; }

interface GroundedReco {
  agentLabel: string;         // "Occupancy Copilot - context picked up"
  contextChip: RecoContextChip;
  read: string;               // reasoned paragraph
  levers: RecoLever[];        // numbered actions with heterogeneous impact chips
  primaryCta?: RecoCta;       // handoff / action / navigate
  projection?: string;        // "Projected peak 102% -> 94% if actions taken"
  citations: string[];        // gold.* provenance
  provenance: Provenance;     // drives the live/simulated badge on the reco
  refused?: boolean;          // HITL gate blocked (deploy/delete ceiling)
}
```

* Keep flat `GroundedReply` for the free-form chat drawer; `GroundedReco` is the
  structured shape for insight/row/lever selection. `rail-context` needs an
  `activeReco: GroundedReco | null` slot and boards must stop discarding the promise.
* `handoff` carries a `target` agent + `requiresApproval` for write/deploy
  (BMCA move = HITL; CSA Run = `approved-to-apply`). `refused:true` renders the
  blocked state instead of executing.
* `askAbout: string[]` is board-level (not per-reco).

**Coverage.** The six boards' worked recos exercise every enum member: chip tones
over/watch/ok/ranked/signal/blocked/pending; impact tones beds/buffer/time
(`4h -> 90m`)/routing (`-> sba`, `-> orsa ✓`)/trust (`Trust-A`)/probability
(`~68%`)/status (`filtered`/`nominal`); CTA kinds handoff/action/navigate. No
leftover fields, no unused members — the shape is sufficient and necessary.

### CSA signal → scenario → probability model

```ts
type Certainty = 'Likely' | 'Possible' | 'Unlikely';
const CERTAINTY_TO_PROBABILITY: Record<Certainty, number> = { Likely: 68, Possible: 31, Unlikely: 6 };

interface ExternalSignal {                     // DC-EXT-SIGNAL-v1 (Sprint 21 Trust-A)
  source: 'MeteoSwiss' | 'BAG/FOPH' | 'Alertswiss/BABS' | 'SED-ETH';
  feed: string; status: string; trustClass: 'Trust-A'; lageLevel?: string;
  certainty: Certainty; probability: number;   // derived via CERTAINTY_TO_PROBABILITY
  feedsLever?: string; licence: string; provenance: string;
  filtered?: boolean;                           // Test/quarantined signals do not trigger
}
interface Scenario    { id: string; name: string; bedImpact: number; isSpof: boolean; probability: number; triggerSignal?: string; }
interface ScenarioRun { id: string; scenarioId: string; params: Record<string, unknown>; status: 'draft' | 'running' | 'complete'; result?: Record<string, unknown>; }
```

`external_signal` rows must pass the `data-quality-agent` `DC-EXT-SIGNAL-v1` gate
(schema, dedup, quarantine, provenance, licence); `filtered` signals render but do
not arm a lever. `ScenarioRun` is the only entity needing persistence (Cosmos via
`cosmos-mcp`); Run is a `deploy`-ceiling action gated by `approved-to-apply`.

---

## 4. Per-board data model (MAIN)

| Board | Entities (Gold tables) | Key data points |
|-------|------------------------|-----------------|
| OOA | `ward_pressure`, `signal_channel`, `specialisation_stream`, `capacity_forecast` | ward now%/72h-trend/forecast%/flag/beds; channel id/label/active; stream flag/fedBy; capacity current/forecast/total/gap beds |
| DCA | `discharge_worklist`, `capacity_barrier` | patient anon-id/ward/readiness/barrier/estFreeHours; barrier name/owner/ageHours/clearsIn/bedImpact/flag |
| BMCA | `placement_request`, `placement_barrier`, `bed_state`, `admissions_stream` | request anon-id/from→to/priority/waitHours; bed util%/free/target/SLA-risk; live admits/discharges (eventstream) |
| ORSA | `elective_or_schedule`, `reslot_lever` | case id/specialty/slot/postOpWard/beds/flag; lever reslot from→to/bedsProtected |
| SBA | `shift_gap`, `staffing_lever` | gap unit/role/shift/fteGap/reliefTarget; lever move from→to/fte/bedsCovered |
| CSA | `external_signal`, `internal_signal`, `scenario`, `scenario_run`, `resilience_lever` | see §3 |

All fields flow through `golden-source-client` (live when `VITE_GOLDEN_SOURCE_URL`
is set, else synthesized + `simulated`). Patient rows use synthetic anon IDs
(`PT-xxxx`); no PHI. Derived insights are agent-host round-trips returning
`GroundedReco` with `gold.*` citations.

---

## 5. START and BACKSTAGE — live-evidence data requirements

> This section answers: *what real data must START and BACKSTAGE expose so they
> show current live evidence rather than static or fabricated content?* Both
> surfaces reuse the same non-negotiable principle as the boards: **no fabricated
> data, no fabricated insights, live-or-simulated badge, source + as-of provenance
> on every metric** (`FR-CX-004`, `FR-CX-006`, `NFR-GOV-006`, `NFR-REL-003`).

### 5.1 START — the only live operational metric is the capacity teaser

START today is a static role launcher. Of its prototype elements, exactly one is a
**live operational** figure; the rest are business-value evidence or editorial.

| START element | Data class | Live source (real data) |
|---------------|-----------|-------------------------|
| Site-capacity teaser (`Medicine A -> 102%`, `site -16 beds`, `breaches 100% ~48h`) | **Live operational** | Same OOA golden source as the board. Add `loadSiteCapacitySummary(scope)` aggregating `capacity_forecast` across wards -> `{ peakWard, peakPct, siteGapBeds, breachEtaHours, firstSurfacedBy: 'ooa-agent' }`. Live via `VITE_GOLDEN_SOURCE_URL` (Sprint 22 medallion Gold), else simulated pinned. **START and OOA must read the same source so the figures agree.** |
| Value / ROI KPIs (`≈3.5M CHF/yr`, `127% ROI/3yr`) | **Business-value evidence** (not live ops) | The **BVA data product** (`data/bva/bva-evidence.ts` -> `bvaHeadlineKpis`), already surfaced on the Backstage `bva` preset. Read from BVA evidence with a `ROM estimate` label + provenance — never inline literals. |
| Copilot count (`7 specialised copilots`) | **Registry-derived** | Live count from the board/agent registry (`LAUNCHER_TILES` + runtime agents in `AGENTS.md`), not a hardcoded number. |
| Why-now CIO decision table (7 rows, Today vs preview) | **Editorial** | i18n content; rows that reference a capacity outcome are illustrative and framed as such. No live metric. |
| Patient-path diagram (copilot at every step) | **Editorial + live badge** | Node badges that assert a capacity figure (e.g. `Med A -> 102% in 72h`) reuse the live `siteCapacitySummary` so they do not become a second hardcoded copy. |
| Role launcher cards + agent-ceiling labels (`ooa-agent · read`) | **Registry-derived (already OK)** | From the board registry; keep. Add the 6th (Crisis) card, RBAC-gated like the MAIN sub-nav. |

**Net:** START needs one new live read (`siteCapacitySummary`, reusing the OOA
golden source), one binding to the existing **BVA data product** for the value
tiles, and a registry-derived copilot count. Everything else is editorial content
that must still carry the showcase/no-PHI disclaimer and, where it states a
capacity number, reuse the live summary. Each metric tile carries a live/simulated
badge + as-of timestamp (`FR-CX-006`).

### 5.2 BACKSTAGE — move evidence from a snapshot to a live provenance feed

BACKSTAGE is the demo's proof surface. Today the Evidence tab reads a **committed
build-time fixture** (`data/evidence/evidence-demo.json`, stamped `as of
2026-07-10`) — a snapshot, not current. "Current live evidence" means each card
must reflect the **actual present state** of the repo and the deployed platform,
provenance-stamped with `source + as-of`. Three tiers, all behind the existing
`loadEvidenceDataset()` seam (ADR-0026 already documents the future swap to Fabric
SQL / Direct Lake):

**Tier 1 — repo-grounded (deterministic; regenerate the fixture on every build/deploy):**

| Evidence | Real source | Notes |
|----------|-------------|-------|
| BOM (25 items, type/category/SKU/deps) | `docs/bom.yaml` | Already the seed (parsed by `scripts/evidence/parsers/bom_parser.py`). Regenerate the app fixture per deploy so it is current. |
| ADR count + status (39) | `docs/adr/*.md` | Count + Proposed/Accepted/Superseded from the files. |
| PRD requirements + which are implemented | `docs/PRD.md` FR/NFR + §7 matrix | Ties evidence cards to realised requirements. |
| Copilot roster + count (`8`) | `AGENTS.md` §1 registry | Runtime copilots; `8` derived, not literal. |
| Region availability (GA vs Preview) | `docs/region-availability.yaml` | Feeds the GA-parity view. |
| `100%` HITL / `0` PHI stat tiles | Repo invariants | `approved-to-apply` gate; synthetic-data constant. Validate by check, do not just assert. |

**Tier 2 — platform-live (the tier that makes it "current", not a snapshot):**

| Evidence | Real source (read-only) | Makes live |
|----------|-------------------------|------------|
| Resource deployment / GA readiness (`T-SHOW`/`T-PROD` Ready/Blocked per BOM) | **Azure Resource Graph** over the SIT/PROD subscriptions (via `azure-mcp`, read ceiling) | Replaces static readiness flags with the real provisioning state + region + SKU. Precedent: `bom.yaml` SKU was corrected `F64 -> F2` via `az resource show` (ADR-0037); a live query keeps the BOM honest continuously. |
| Build / HITL proof (draft-PR count, approvals, `von Agenten gebaut`) | **GitHub API** (PRs, checks, CODEOWNERS approvals, `approved-to-apply` comments) | Proves the `100%` HITL invariant with live counts instead of a claim. |
| Data-platform liveness (`da_hospital_capacity · live`, Fabric IQ ontology) | Fabric REST / Direct Lake ping | Shows the ontology/data-agent is actually reachable. |

**Tier 3 — business value:** the BVA evidence data product (already the `bva`
preset) supplies the boardroom value view.

**Provenance + degradation.** Every card replaces the fixed `as of 2026-07-10`
with a real `source + as-of` stamp and a live/snapshot badge — mirroring the
boards' live/simulated pattern. If a Tier-2 call fails, fall back to the Tier-1
committed fixture flagged `snapshot` rather than blanking the card
(`NFR-REL-003`). No PHI at any tier — governance metadata only.

**Net:** BACKSTAGE's Evidence and Roles tabs are already real and repo-grounded and
should be kept and extended. The live upgrade is to (a) regenerate the repo-grounded
fixture at build so it is current, and (b) add a Tier-2 live read (Azure Resource
Graph + GitHub API) behind the same `loadEvidenceDataset()` seam so readiness and
HITL proof reflect the real platform state — each card provenance-stamped. The
Story tab separately needs its parity content restored (stat tiles, PLAN→…→RELEASE
and DEV→…→PROD strips, 8-copilot roster), all derivable from the Tier-1 sources.

---

## 6. Fluent UI v9 control mapping (summary)

App runs `@fluentui/react-components@^9.54.17`. Pick native controls over
hand-rolled markup for accessibility + theming.

| Prototype element | Fluent v9 control |
|-------------------|-------------------|
| Docked reco rail | `Drawer type="inline" position="end"` (replaces overlay) |
| Worklist / barrier / lever / schedule tables | `DataGrid` (sortable, keyboard, row-click) |
| Status + impact + readiness chips | `Badge` (`appearance="tint"`, tone→color) |
| Numbered lever rows | `List` / `ListItem` + circular `Badge` |
| Primary CTA (handoff/action/navigate) | `Button appearance="primary"` + icon |
| Ask-about chips | `TagGroup` + `InteractionTag` |
| Chat input | `Textarea` + `Button` |
| Handoff banner | `MessageBar` + provenance `Badge` |
| Capacity-flow / patient-path / signal-flow diagrams | Composed `Card` + `Divider` + arrow icons + `ProgressBar` (no native flow primitive) |
| KPI / value / stat tiles | `Card` + large `Text` + `Caption1` |
| CSA scenario Run | `Dialog` + `Spinner` + `MessageBar` (approved-to-apply) + `Toast` |
| Loading | `Skeleton` |

**Theming.** Replace the prototype's six hardcoded hex colours with a **Curavias
brand theme** (`createLightTheme`/`createDarkTheme` from a teal `#17B890` ramp) plus
one custom **routing-purple** token for cross-agent handoffs. Every `makeStyles`
block references tokens only — fixing dark-mode contrast and enabling clean
Demo/User + light/dark switching via `FluentProvider`.

---

## 7. Copilot agent interaction model (per MAIN board)

The per-role Copilot is the heart of every MAIN board and is the largest parity
gap. Full detail (evidence, defects D1–D8, Fluent mapping, provenance, prompts)
is in the companion
[findings dossier §9](2026-07-23-curavias-app-parity-findings.md). Distilled:

**Target behaviour (prototype).** A **docked, full-height right rail** (never an
overlay) with three states: (1) a **proactive default reco** on load
("Why is pressure rising?" + suggested next step + CTA — the rail is never
empty); (2) a **context reco** that swaps in when a left/centre-plane insight
(ward row, stream, site-gap card) is clicked — the click auto-expands the rail
and selects the matching reco, with a "← Back to summary"; (3) **free chat** plus
an **"Ask about"** chip row of three pre-canned prompts. The reco panel is exactly
the `GroundedReco` v2 in §3 (chip · agent line · read · numbered levers with
impact chips · handoff CTA · projection).

**Current app (two disjoint systems).** `AgentPlane` shows an empty free-chat box;
`routeInsight` opens the rail but **discards the returned `GroundedReply`**, and
`AgentPlane` never reads the clicked context. Net effect: clicking an insight
opens an unrelated, empty chat — no reco, no default, no ask-about, flat rendering.

**The wiring fix (routing).** board insight → `routeInsight` (store `activeReco`,
stop discarding) → `invokeReco(agent, context)` → Foundry `role-agent` (eastus2)
grounded by Fabric IQ `da_hospital_capacity` (ADR-0034) → `GroundedReco` →
`AgentPlane` renders **activeReco → defaultReco → chat turns**.

**Rendering (best-fit Fluent v9).** Build a shared `<RecoPanel>` from stable
primitives: status chip → `Badge` (tone colour); agent line → `Caption1` +
`PresenceBadge`; read → `Body1`; each lever → `CounterBadge` + `Body2` + impact
`Badge`; CTA → `Button appearance="primary"` (→ `toHandoff`); projection →
`Caption1`; refusal/HITL → `MessageBar`; ask-about → clickable `InteractionTag`.
Avoid the preview `@fluentui-copilot/react` on the parity critical path.

**Actionable insights + data.** Insights are clickable left/centre-plane elements;
their context must be **enriched** (tone + lever/impact/projection inputs), then
grounded per board on Gold tables via Fabric IQ (`capacity_forecast`,
`discharge_candidates`, `bed_assignment`, `or_schedule`, `roster`,
`scenario_library`, …). Every reco carries `provenance` + as-of and cites real
Gold objects. **Ask-about** prompts (18 total, §9.8 of the dossier) bind to the
flat `GroundedReply` chat path, distinct from the `GroundedReco` selection path.

---

## 8. Recommended sprint sequencing

| Slice | Scope |
|-------|-------|
| S1 | Foundation + OOA walking skeleton: freeze the contract, fix the discarded-reply rail wiring, add `GroundedReco`, docked inline `CopilotRail`, enrich `occupancy-data`, Curavias brand theme |
| S2 | DCA + BMCA (BMCA consolidation, keep Power BI embed + eventstream) |
| S3 | ORSA + SBA |
| S4 | CSA + close the ring (signal→scenario→probability, Cosmos scenario/run, deploy-ceiling HITL) |
| S5 | START (hero, value tiles from BVA, live capacity teaser, why-now, patient-path, Crisis card) |
| S6 | BACKSTAGE (Story-tab parity content + live Tier-2 evidence read + provenance stamps) |

---

## 9. Traceability

This review advances the following requirements (from
[`docs/PRD.md`](../../PRD.md); IDs per the Sprint 20 design spec §16):

| Requirement | Relevance to this review |
|-------------|--------------------------|
| `FR-CX-001` | Docked agent plane (the reco rail wiring fix) |
| `FR-CX-002` | Grounded answers with source context (`GroundedReco.citations`) |
| `FR-CX-003` | Bottleneck explanations on boards + plane (reco read + levers) |
| `FR-CX-004` | Bed state / pressure windows / discharges on boards + START teaser |
| `FR-CX-006` | Source references + timestamps preserved (provenance stamps) |
| `FR-VIZ-001` | Bed-capacity board (occupancy, forecast, DQ signals) |
| `FR-VIZ-002` | OR-steering board |
| `FR-GOV-002` | Access-control via the role access lens (Crisis card gating) |
| `NFR-GOV-006` | Per-visual source citations (START/BACKSTAGE evidence provenance) |
| `NFR-REL-003` | Graceful degradation of live surfaces (snapshot fallback) |
| `NFR-AI-001` | Agent plane outputs remain advisory |
| `NFR-MAINT-001` | Work stays within the experience (app) lane |

No new requirement is introduced; no `docs/PRD.md` §7 matrix change is required by
this review. Any new contract (`GroundedReco`) is an implementation artefact of the
already-approved parity design spec.

---

## 10. Open decisions

* Whether the full evidence dossier (session working artefact) is promoted into the
  repo alongside this outcome, or this outcome is the single durable record.
* Whether BACKSTAGE Tier-2 live reads (Azure Resource Graph, GitHub API) land in the
  parity sprint or as a follow-up, given they add read-only cloud/API dependencies to
  the app (currently a static-web app with no backend).
* Confirmation that the deployed SIT app lags the branch source (the branch already
  contains all six board files and the six-tile launcher, so deployed state ≈ current
  branch skeleton).
