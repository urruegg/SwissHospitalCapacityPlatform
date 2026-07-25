# Curavias App — Prototype Parity Review Findings

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-23 |
| **Author** | @urruegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (initial promotion of the session dossier) |

> Working artefact for the Sprint 20 app-parity refactoring. Evidence-based gap
> analysis, screen by screen. **Baseline** = locked prototype
> (`docs/superpowers/ideas/curavias-ux-ideas/prototype/surfaces/*`).
> **Target** = deployed SIT app `https://appsit.curavias.ch` (current branch build).
>
> Method: Playwright captures at 1440x960, demo mode, role lens `HCC.Viewer`,
> `de` locale, `aggregated` scope. Screenshots in `files/shots/`.

## Legend

- **MISSING** — element present in baseline, absent in target.
- **PARTIAL** — present but reduced/simplified vs baseline.
- **DIVERGENT** — present but semantically/visually different.
- **OK** — at parity.

---

## Global shell (observed on all screens)

| Area | Baseline intent | Target (deployed) | Status |
|------|-----------------|-------------------|--------|
| Header ribbon | brand + mode + role lens + language + scope + theme | Present: Curavias, theme (Light), lang (de), scope (aggregated), role lens (HCC.Viewer), Demo toggle, user | OK (shell) |
| Left nav (acts) | START / MAIN / BACKSTAGE / Settings | Start / Hauptbereich / Backstage / Einstellungen | OK |
| MAIN sub-nav | 6 role boards | Belegung/Entlassung/Bettenmanagement/OP-Steuerung/Personal/**Krise (disabled/greyed)** | PARTIAL — Krise present but disabled for HCC.Viewer |
| Copilot rail | full-height docked teal rail w/ FAB collapse | collapsed FAB only (small glyph, right edge); "Agent öffnen" button on board | PARTIAL — rail content is a drawer, not the docked reco rail |
| Footer | golden-thread status line | "Off" selector + v0.1.0 | DIVERGENT (different footer semantics) |
| START role launcher | 6 roles | 5 cards (no Crisis card) | PARTIAL — Crisis launcher missing |

---

## Screen 1 — OOA (Occupancy / Belegung)  `/main/occupancy`

Baseline: `surfaces/01-ooa-occupancy.html` · Target shot: `target-ooa.png` · Baseline shot: `baseline-ooa.png`

### Header block

| Element | Baseline | Target | Status |
|---------|----------|--------|--------|
| Agent label | `MAIN · ooa-agent` (teal eyebrow) | none | MISSING |
| Title | "Occupancy & 72h Forecast" | "Auslastungsprognose (72h)" | DIVERGENT (title-only, localized) |
| Provenance badge | `SIMULATED DATA` amber pill | `simuliert` pill inside handoff banner | PARTIAL (moved into banner) |
| Locale badge | `EN·DE·FR·IT` | (global lang selector only) | MISSING (board-level badge) |
| Access-lens badge | `Access-lens: Bed Ops` | none on board | MISSING |
| Handoff banner | (baseline shows reco chain, not a banner) | "Carried from ooa-agent: Medicine A -> 102% in 72h, site -16 beds" | OK (target adds banner; good) |

### Left main column

| Element | Baseline | Target | Status |
|---------|----------|--------|--------|
| Ward pressure TABLE | 4 wards x (Now, 72h trend arrow, Forecast, Flag pill), clickable rows → rail reco | absent | **MISSING** (core) |
| — Medicine A row | 34/36, 94% → 102% OVER (red, rising) | shown only as a KPI card "Medicine A 102% -9 Betten" | PARTIAL |
| — ICU row | 11/12, 92% → 95% WATCH | absent | MISSING |
| — Surgery B row | 28/40, 70% → 88% WATCH | "Surgery A 88% -3 Betten" card | DIVERGENT (naming + no table) |
| — Cardiology row | 20/30, 67% → 74% OK | absent | MISSING |
| Capacity-flow DIAGRAM | 3-stage: Signal channels (6, w/ icons) → Specialisation streams (4, flagged) → Capacity (current 105/130 81%, forecast 121/130 93%, Gap -16 beds) | absent | **MISSING** (core) |
| — Signal channels | ED arrivals, Admissions/transfers, Elective OR, Planned discharges, LOS signal, Staffing roster | absent | MISSING |
| — Specialisation streams | Emergency&Acute HIGH, Surgery&Perioperative WATCH, Intensive Care WATCH, Cardiology OK | absent | MISSING |
| — Capacity summary | current/forecast/gap tiles | absent | MISSING |
| KPI cards | (not in baseline main column as such) | 3 cards: Medicine A/B, Surgery A | DIVERGENT — target substitutes 3 flat KPI cards for the table+flow |
| Footer explainer | signal-flow narrative paragraph | absent | MISSING (nice-to-have) |

### Copilot rail (right)

| Element | Baseline | Target | Status |
|---------|----------|--------|--------|
| Docked full-height rail | teal-bordered, always docked (collapsible to FAB) | drawer opened via "Agent öffnen" / FAB glyph | DIVERGENT (drawer vs docked rail) |
| Rail header | "● Occupancy Copilot" | (n/a until opened) | MISSING (as docked) |
| Default summary | "Why is pressure rising?" bullets (Medicine A, ICU) | none | MISSING |
| Suggested next step box | "Relieve Medicine A by expediting eligible discharges." | none | MISSING |
| Primary CTA | "See 8 discharge candidates →" (green) | none | MISSING |
| Handoff line | "Handoff → Discharge Coordinator (dca)" | (banner carries this instead) | PARTIAL |
| Per-selection reco panels | Medicine A / ICU / Surgery B / Cardiology / Site gap — each: chip, agent line, read paragraph, numbered levers w/ impact chips, action button, footnote | none (1 plain insight "Medicine A steigt") | **MISSING** (core) |
| "Ask about" chips | "Which ward tips first?", "What if flu peaks early?", "ICU staffing risk" | none | MISSING |
| Chat input | "Ask the Occupancy Copilot…" + send | (only in drawer, TBD) | MISSING (on board) |

### Interaction gaps

- Baseline: clicking a ward row / stream card / capacity gap selects it and swaps the
  rail to the matching agent reco (context pickup). Target has 1 static insight button
  → drawer. **Insight-to-reco routing over multiple contexts is MISSING.**
- Baseline rail stays docked alongside the board; target uses a modal/drawer pattern.

### OOA verdict

Target OOA is a **walking skeleton** (banner + 3 KPI cards + 1 insight + collapsed FAB).
The two core baseline artefacts — **ward-pressure table** and **capacity-flow diagram** —
and the **docked reco rail with per-context recommendations** are entirely absent.
This is the single largest parity gap and is Sprint-1 (foundation) scope per the design.

**Refactor tasks (OOA):**
1. Add ward-pressure table bound to `occupancy-data` payload (rows w/ now/trend/forecast/flag).
2. Add capacity-flow diagram (signal channels → streams → capacity tiles + gap).
3. Replace drawer with docked `CopilotRail` (collapsible to FAB) rendering per-selection reco.
4. Wire row/stream/gap click → `InsightRouter` → agent reco (multi-context).
5. Add "Ask about" chips + rail chat input.
6. Add board header eyebrow (`MAIN · ooa-agent`) + access-lens badge.
7. Populate `occupancy-data` contract to carry ward + flow + capacity (not just 3 channels).

### Deep evidence (rail open, insight click, mode toggle)

Shots: `target-ooa-rail-open.png`, `target-ooa-insight-clicked.png`, `target-ooa-user-mode.png`,
`baseline-ooa-medicineA-reco.png`.

| Behaviour | Baseline | Target | Status |
|-----------|----------|--------|--------|
| Rail content | context chip + "context picked up" line + reasoned paragraph + 3 numbered **levers w/ impact chips** (−6 beds / +3 buffer / −2 in 48h) + primary CTA "Open discharge worklist → dca" + projected-peak footnote + "Ask about" chips + "← Back to summary" | **empty agent-chat drawer**: only `ooa-agent · read` header, close X, input + "Senden" | **MISSING** (rail reco body) |
| Selected-row highlight | clicked ward row highlights + swaps rail to its reco | no table to select; insight click inert | MISSING |
| Insight → reco round-trip | click reveals per-context reco | click "Medicine A steigt" → **no rail change** (no visible round-trip / silent fail) | **MISSING / BROKEN** |
| Primary CTA (handoff) | green "Open discharge worklist → dca" lever | none | MISSING |
| Demo mode banner | golden-thread residual carried | "Carried from ooa-agent: Medicine A -> 102% in 72h, site -16 beds" | OK |
| User mode banner | real context only | "Current capacity context" (role label Demo→Benutzer) | OK ✅ |
| Mode toggle effect | changes orchestration only | banner swap works; data unchanged | OK ✅ |

**Working in target (keep):** two-tier nav, handoff banner + provenance badge, Demo↔User
toggle changes only the banner/orchestration, agent-chat drawer shell w/ agent id, ceiling,
and input, RBAC ceiling surfaced (`ooa-agent · read`).

**Broken/absent in target (build):** ward table, capacity-flow diagram, capacity/gap tiles,
docked rail reco body (summary + per-context levers + CTA + ask-about chips), insight→reco
routing, board eyebrow + access-lens badge, footer explainer.

### Underlying functionality required (data + agent + orchestration)

Evidence from source: `data/roleboard/occupancy-data.ts`, `golden-source-client.ts`,
`workspaces/main/boards/occupancy/occupancy-board.ts`, `copilot-rail/InsightRouter.ts`,
`copilot-rail/rail-context.tsx`, `copilot-drawer/agent-manifest.ts`.

| Layer | Present today | Required for parity | Gap |
|-------|---------------|---------------------|-----|
| **Data contract** | `OccupancyPayload = { siteOccupancyPct, siteDeltaBeds, channels[3] }` | wards[] (now/trend/forecast/flag/beds), signalChannels[6], streams[4] (label/flag/fedBy), capacity{ currentBeds, forecastBeds, totalBeds, gapBeds } | **Enrich contract** — current payload can't express table/flow/capacity |
| **Data source** | `golden-source-client.loadOccupancy` — live fetch if `VITE_GOLDEN_SOURCE_URL`, else synthesized `OCCUPANCY_PINNED` flagged `simulated` | same adapter; enrich the synthesized dataset + live JSON shape | OK pattern ✅; extend payload only |
| **Insights** | `insights()` emits only channels ≥100% (1 insight) | selectable contexts for each ward row + each stream + the site gap | **Broaden `insights()` / add selection handlers** |
| **Agent round-trip** | `routeInsight` → `invokeInsight` → `invokeAgent` (host at `VITE_AGENT_HOST_URL`, else deterministic mock reply) | same round-trip, **rail must render the reply** | Seam OK; **reply is fetched then discarded** (`void routeInsight`) |
| **Reco shape** | `GroundedReply = { answer:string, citations[], refused }` (flat text) | baseline reco = chip + reasoned read + **numbered levers w/ impact chips** + primary CTA (handoff) + projected-peak footnote | **Extend reply contract** to structured levers/CTA (or agent returns structured reco) — else parity loses the lever UI |
| **Rail state** | `rail-context` stores `activeContext` (the insight) only; opens a drawer | store + render the `GroundedReply`/structured reco; docked collapsible rail (FAB) | **Rail doesn't hold/render the agent reply**; drawer≠docked rail |
| **Handoff/orchestration** | `toHandoff`/`fromHandoff` wired; banner carries residual; Demo↔User works | primary CTA in reco triggers handoff to dca (baseline "Open discharge worklist → dca") | Banner OK ✅; **CTA→handoff action not surfaced in rail** |
| **RBAC ceiling** | `ceiling: 'read'` surfaced in drawer header | gate rail actions by ceiling | OK ✅ |

**Root-cause wiring bug:** `OccupancyBoard` calls `void routeInsight(insight, …)` — the
`GroundedReply` promise is awaited nowhere and the answer never reaches the rail. The rail
renders nothing because `rail-context` has no slot for the reply. This must be fixed for
*any* board's insight→reco to work (shared across all 6 roles).

### OOA — per-screen summary

- **Parity level: ~20%** (walking skeleton). Shell/nav/banner/mode-toggle/RBAC = OK; the
  three core artefacts (ward table, capacity-flow diagram, docked reco rail) are absent.
- **Biggest lift:** the docked Copilot rail rendering a **structured, per-context agent
  reco** (summary → levers with impact → handoff CTA). Requires (a) enriched data contract,
  (b) extended reply/reco contract, (c) rail-context holding the reply, (d) fixing the
  discarded-promise wiring. This is shared foundation reused by DCA/BMCA/ORSA/SBA/CSA.
- **Sequencing:** these are Sprint-1 foundation items in the design; fixing them unblocks
  the identical board shape for the other five roles.
- **Quick wins:** board eyebrow (`MAIN · ooa-agent`), access-lens badge, footer explainer,
  broaden `insights()` to wards+streams+gap.

---

## Screen 2 — DCA (Discharge / Entlassung)  `/main/discharge`

Baseline: `surfaces/02-dca-discharge.html` · Target shot: `target-dca.png`

### Board comparison

| Element | Baseline | Target | Status |
|---------|----------|--------|--------|
| Agent eyebrow | `MAIN · dca-agent` | none | MISSING |
| Title | "Discharge Coordination" | "Entlassungsbereitschaft (72h)" | DIVERGENT (localized) |
| Badges | SIMULATED DATA / EN·DE·FR·IT / Access-lens: **Discharge** | `simuliert` (in banner) only | PARTIAL |
| Handoff note | inline "Handoff from ooa-agent · Medicine A 102% · site −16 · 8 candidates" | banner "Carried from ooa-agent…" + **loop-back note** "führt zurück zur Auslastungsprognose" | OK ✅ (loop-back present) |
| Summary metrics | (in tracker) | "Benötigte 16 / Freisetzbare 9 / Restbedarf −7" line | OK-ish (plain text) |
| **Discharge worklist TABLE** | 8 anonymised patients (PT-xxxx) × Ward, Readiness badge (READY/BLOCKED/PENDING), Barrier, Est. free; clickable rows → unblock playbook | absent — replaced by **4 candidate cards** (Ward/blocker/beds) | **MISSING** (core) |
| **Capacity-barriers board** | systemic barriers ranked by bed impact (rank, icon, owner, age, clears-in, flag), click → systemic playbook, loops back to ooa | absent | **MISSING** (core) |
| Insights | per-row unblock playbooks | 3 insight buttons, **2 share identical label** "Entlassung Medicine A beschleunigen" | PARTIAL + minor bug |
| Docked reco rail | per-barrier/patient reco (chip, read, levers, CTA) | empty agent-chat drawer (same as OOA) | MISSING |

### Underlying functionality required

| Layer | Present today | Required for parity | Gap |
|-------|---------------|---------------------|-----|
| Data contract | `DischargePayload = { bedsNeeded, bedsFreeable, residualBeds, candidates[4] }` (candidate = ward/blocker/bedsFreeable/expedite) | worklist[] of anonymised patients (id, ward, readiness enum, barrier, estFreeHours), barriers[] ranked (rank, name, owner, ageHours, clearsIn, bedImpact, flag) | **Enrich contract** — cards can't express worklist rows or ranked barriers |
| Data source | `loadDischarge` — live-or-synthesized, flagged `simulated` | same adapter; extend dataset | OK pattern ✅ |
| Insights | `insights()` = expeditable candidates (dup labels) | per-worklist-row + per-barrier contexts; **deduplicate labels** (include ward+id) | Broaden + fix dup label |
| Handoff | `toHandoff` (residual −7) + `fromHandoff` carries ooa headline; loop-back note wired | primary CTA in reco loops back to ooa (baseline barriers board) | Banner+loop-back OK ✅; CTA→loop action not surfaced |
| Ceiling | `ceiling: 'write'` | gate expedite/unblock actions behind write ceiling + HITL | OK surface ✅; enforce on action |
| Rail reco | (shared) discarded reply, no reply slot | render structured unblock playbook | shared foundation gap |

### DCA — per-screen summary

- **Parity level: ~25%.** Shell/nav/banner/**loop-back**/summary = OK; the two core
  artefacts (anonymised discharge worklist table, ranked capacity-barriers board) and the
  docked reco rail are absent.
- **Domain-specific data needed:** anonymised patient worklist (PHI-safe synthetic IDs) +
  systemic barriers ranked by bed impact — richer than the current 4 flat candidate cards.
- **Reuses OOA foundation:** identical rail/insight-routing fix; DCA adds the worklist +
  barriers UIs and enriched `DischargePayload`.
- **Bug to fix:** duplicate insight-button labels (two Medicine A expedite candidates render
  the same text) — differentiate by ward+candidate id.
- **Write-ceiling note:** unblock/expedite actions must honour `dca-agent · write` + any HITL
  gate (currently ceiling is surfaced but no action is wired).

---

## Screens 3–6 — BMCA / ORSA / SBA / CSA (batch)

All four target boards share the OOA/DCA skeleton (banner + summary line + a few flat cards +
insight buttons + empty agent drawer). Every baseline board shares an identical richer shape:
**eyebrow `MAIN · <agent>` + badges → worklist TABLE (row→playbook) → levers/barriers board
ranked by bed impact (→ systemic playbook) → docked reco rail (chip, read, numbered levers w/
impact, CTA, ask-about chips, chat)**. Gaps below are the delta from that shape.

### Screen 3 — BMCA (Bed management / Bettenmanagement)  `/main/bed-manager`

Baseline: `surfaces/03-bmca-bed-management.html` · Shot: `target-bmca.png`

| Element | Baseline | Target | Status |
|---------|----------|--------|--------|
| **Inbound placement worklist** | 8 anonymised placement requests, row→placement playbook | absent | MISSING |
| **Placement barriers (ranked)** | ranked by bed impact, row→systemic playbook | absent | MISSING |
| Reco rail | per-placement reco | empty drawer | MISSING |
| **Legacy Sprint-11 whiteboard** | (not in baseline) | KPI tiles (87% util, 18 free, 9 SLA-risk), Stations-Heatmap Power BI embed (mock), BMCA-Empfehlung, Live-Zugänge eventstream, Verantwortlich, Szenario | **DIVERGENT** — stacked *below* the skeleton w/ duplicate title "Bettenmanagement — USZ" |
| Structure | one coherent board | **two stacked boards** (parity skeleton + legacy whiteboard) | **CONFLICT — consolidate** |

BMCA is the only "refit" board and is currently a **hybrid**: the parity skeleton and the
legacy Sprint-11 card whiteboard both render. Refit = fold the useful legacy widgets (KPI
tiles, heatmap embed, eventstream) into the RoleBoard shape and drop the duplicate title.
Also note real assets to preserve: **Power BI Direct Lake embed (RLS by hospital)** and
**eventstream: admissions** live feed.

### Screen 4 — ORSA (OR steering / OP-Steuerung)  `/main/or-steering`

Baseline: `surfaces/04-orsa-or-steering.html` · Shot: `target-orsa.png`

| Element | Baseline | Target | Status |
|---------|----------|--------|--------|
| **Elective OR schedule table** | next 72h, post-op ward flagged, row→reslot playbook | absent — 3 flat procedure cards (Orthopedics/General/Cardiac + time + beds) | MISSING |
| **Reslot levers (ranked)** | ranked by beds protected, →systemic playbook | absent | MISSING |
| Summary | (in tracker) | "Fehlende 3 / Verschoben 2 / Frei 2 / Restbedarf −1" | OK-ish |
| Reco rail | per-reslot reco | empty drawer | MISSING |
| Banner + loop-back | carries bmca residual | "Carried from bmca-agent: 4 beds reallocated…" + loop-back | OK ✅ |

### Screen 5 — SBA (Staffing / Personal)  `/main/staffing`

Baseline: `surfaces/05-sba-staffing.html` · Shot: `target-sba.png`

| Element | Baseline | Target | Status |
|---------|----------|--------|--------|
| **Coverage worklist table** | 6 shift gaps, Medicine A relief, row→staffing playbook | absent — 2 flat cards (RN ICU float→Med A 1 FTE; HCA Surgery B→Med B 0.5 FTE) | MISSING |
| **Staffing levers (ranked)** | ranked by beds covered | absent | MISSING |
| Summary | (in tracker) | "Fehlende 1 / Surge 1 / Restbedarf 0" | OK-ish |
| Reco rail | per-lever reco | empty drawer | MISSING |
| Banner + loop-back | carries orsa residual | "Carried from orsa-agent: 2 elective cases deferred…" + loop-back | OK ✅ |

### Screen 6 — CSA (Crisis / Krise)  `/main/crisis`  — **NOT DEPLOYED**

Baseline: `surfaces/06-csa-crisis.html` · Shot: `target-csa.png` (nginx 404)

| Element | Baseline | Target | Status |
|---------|----------|--------|--------|
| Route `/main/crisis` | crisis board | **nginx 404** (no SPA route/board) | **MISSING (whole screen)** |
| Nav "Krise" | 6th board | present but **disabled** for HCC.Viewer lens | RBAC-gated / unbuilt |
| **External signals · Trust-A** | MeteoSwiss/Alertswiss/SED-ETH/BAG feeds → certainty | absent | MISSING |
| **Internal signals** | occupancy/staffing/LOS pressure | absent | MISSING |
| **Potential scenarios + Probability** | signal→scenario→probability mapping (Sprint 21 Trust-A) | absent | MISSING |
| **Scenario queue** | 6 shocks pressure-tested, row→simulation | absent | MISSING |
| **Resilience levers (ranked)** | ranked by beds protected | absent | MISSING |
| Ceiling | `csa-agent · deploy` (Run triggers `csa-simulate`, gated by `approved-to-apply`) | n/a | Confirm HITL on Run |

CSA is Sprint-4 scope and is the most complex board (adds the signal→scenario→probability
pipeline). It is currently **entirely absent** from the deployed app (route 404s). Its
data/agent needs are the largest (external + internal signals, scenario simulation, Cosmos-
backed scenario/run memory per the registry).

### BMCA/ORSA/SBA/CSA — per-screen summaries

- **BMCA ~40% but CONFLICTED** — richest board (real Power BI embed + eventstream to keep)
  but rendered as two stacked boards; **consolidate into one RoleBoard**, add placement
  worklist + ranked barriers.
- **ORSA ~25%** — skeleton; needs elective-OR schedule table + reslot levers.
- **SBA ~25%** — skeleton; needs coverage worklist (shift gaps) + staffing levers.
- **CSA ~0%** — not deployed; whole board + signal→scenario→probability pipeline + Cosmos
  scenario/run memory + deploy-ceiling HITL gate to build (Sprint 4).

---

## Screen 7 — START (`/start`)

Baseline: `surfaces/00-start.html` · Shots: `baseline-start.png` / `target-start.png`

Baseline START is a full **executive product-overview landing** (the C-level entry to the
demo). Target `/start` is a bare **role launcher** — it has the role cards but none of the
narrative. This is the largest single-screen storytelling gap.

| Element | Baseline | Target (`/start`) | Status |
|---------|----------|-------------------|--------|
| Hero band | "Every patient's path, in Swiss hands." + "See the squeeze before it happens. Act before it hurts." + one-shared-view subhead | one line "Koordination der Spitalkapazität…" + showcase disclaimer | **PARTIAL** (headline/value prop missing) |
| Value KPI tiles | `≈3.5M CHF/yr` target value (ROM), `127%` ROI/3yr, `7` specialised copilots | absent | **MISSING** |
| Site-capacity teaser (next 72h) | Medicine A 102%, site −16 beds at peak, breaches 100% ~48h, "first surfaced by Occupancy copilot" | absent | **MISSING** |
| "Why now" — CIO challenger question | quote + **7-decision table** (Today vs With Curavias preview) | absent | **MISSING** (core narrative) |
| Curavias patient-path diagram | copilot at every step (CSA spans · DQ guards · OOA→BMCA→ORSA→SBA→DCA→Recovery) | absent | **MISSING** |
| Role launcher cards | (path implies 7 copilots) | **5 cards**: Belegung `ooa·read`, Entlassung `dca·write`, Bettenmanagement `bmca·write`, OP-Steuerung `orsa·write`, Personal `sba·write` | **PARTIAL** — Crisis card missing (5 of 6) |
| Agent + ceiling label on cards | — | `ooa-agent · read` etc. surfaced on each card | OK ✅ (target enhancement, keep) |
| Demo/mode badge | LIVE / SIMULATED | "Demo — simulierte Golden-Thread-Präsentation" badge | OK |
| Showcase disclaimer | "Not a real product…synthetic data (no PHI)…" | present (localized) | OK |
| BACKSTAGE cross-link | "Executive / C-level view — open BACKSTAGE →" in-context CTA | only the global nav item | PARTIAL (no in-context CTA) |

### START — underlying functionality

- **Value/ROI/site-capacity figures** are showcase ROM numbers — must be **pinned config
  constants flagged as showcase estimates** (not fabricated at runtime, not implying live
  finance). Site-capacity teaser should **reuse the OOA golden-thread pinned slice** (Medicine
  A 102%, −16 beds) so START and OOA agree.
- **7-decision table** + **patient-path** are static editorial content (i18n strings) — no
  agent call; still must carry the provenance/disclaimer framing.
- **Crisis card**: add the 6th launcher; its enabled/disabled state follows the RBAC lens
  (disabled for `HCC.Viewer`, matching the MAIN sub-nav "Krise" treatment).
- Role cards already wired to launch routes (`launch-*` testids) — keep.

### START — Fluent v9 mapping

| Block | Best-fit control |
|-------|------------------|
| Hero band | section + `LargeTitle`/`Title1` `Text` + `Subtitle2` |
| Value KPI tiles | `Card` + `Text size={800}` + `Caption1` |
| Site-capacity teaser | `Card` + `Badge color="danger"` + `ProgressBar` |
| 7-decision table | `DataGrid` / `Table` (columns: #, Decision, Today, With preview) |
| Patient-path diagram | composed `Card` row + `Divider` + `ArrowRight` icons + per-copilot `Badge` (no native flow primitive) |
| Role launcher cards (+Crisis) | keep `Card`; ceiling as `Badge appearance="tint"`; disabled Crisis = `Card` + `Badge` "gesperrt" |
| BACKSTAGE CTA | `Button appearance="subtle"` + `Open16Regular` |

### START — summary

Target START ≈ **20%**: the role launcher fragment exists (and the agent-ceiling labels are a
good addition to keep), but the entire executive narrative — hero, value KPIs, why-now
decision table, patient-path — is missing, plus the Crisis card. Sprint-5 scope. No new agent
wiring; mostly enriched static content + one pinned golden-thread teaser + the 6th card.

---

## Screen 8 — BACKSTAGE (`/backstage`)

Baseline: `surfaces/07-backstage.html` · Shots: `baseline-backstage.png` /
`target-backstage.png` (+ `-story`, `-roles`)

**Divergent — and the target is in some dimensions richer than baseline.** Baseline BACKSTAGE
is a single executive "how it was built" narrative. Target `/backstage` is a **3-tab presenter
whiteboard** (Story / Nachweise / Rollen & RBAC) whose **Nachweise (evidence)** and **Rollen**
tabs are real, repo-grounded additions to **keep**; the parity gap is the **Story** tab
under-delivering vs the baseline proof narrative.

| Element | Baseline | Target (`/backstage`) | Status |
|---------|----------|-----------------------|--------|
| Tab structure | single scroll narrative | `TabList`: Story / Nachweise (default) / Rollen & RBAC (`backstage-nav-*`) | DIVERGENT (target richer) |
| Headline stat tiles | `8` Copiloten von Agenten gebaut · `100%` HITL-gated · `0` echte PHI | absent on Story tab | **MISSING** |
| "Bauplan in einem Satz" pipeline | PLAN→BUILD→TEST→HITL-Gate→RELEASE strip | absent | **MISSING** |
| Four proofs | 4 cards: Von Agenten gebaut · Fabric+FHIR · Governance (Swiss DSG/HITL/`approved-to-apply`) · DEV→SIT→PROD | Story tab: 4 pillars (Von Agenten gebaut · Fabric+FHIR · Schweizer Datenschutz · Dev→SIT→Prod) | **PARTIAL** (text pillars; lost stat tiles + proof depth) |
| Maturation flow | DEV→PR→SIT→HITL→PROD strip | absent | **MISSING** |
| Copilot roster ("die Sie gesehen haben") | 8: OOA/BMCA/DCA/ORSA/SBA/CSA/Data-Quality/Onboarding | absent | **MISSING** |
| **Evidence whiteboard (Nachweise)** | — | BOM/ADR/GA-parity/dependency cards: `T-SHOW 100%`/`T-PROD 88%`/`GA-Paritätslücke 3`, `25 BOM`/`39 ADR`, per-resource readiness (T-SHOW/T-PROD Ready/Blocked), provenance `docs/bom.yaml` + `docs/PRD.md` | **OK ✅ target-only enhancement (keep)** |
| **Roles & RBAC tab** | — | RBAC matrix (`backstage-nav-roles`) | **OK ✅ target-only (keep)** |
| Back-links | "Zurück zu START / Zurück zu MAIN" | global nav | OK |
| Disclaimer | synthetic/no-PHI | present | OK |

### BACKSTAGE — underlying functionality

- **Evidence tab reads real repo provenance** — `docs/bom.yaml` (25 BOM items, resource type /
  category / region / GA status / deps / T-SHOW+T-PROD readiness) and `docs/PRD.md`
  requirement links, plus 39 ADRs. This is genuine, non-fabricated evidence — **keep and
  build on it**; it directly serves the demo's "prove it" goal.
- **Story stat tiles are derivable, not fabricated**: `8` = count of runtime copilots from the
  `AGENTS.md` registry; `100%` HITL = the `approved-to-apply` invariant; `0` PHI = the
  synthetic-data constant. Wire them from source, don't hardcode a literal.
- **GA-parity view** (T-SHOW vs T-PROD, parity gap 3) already computes readiness deltas — a
  strong exec artefact; ensure the blocked items (Container Apps T-PROD, Fabric Data Agent /
  IQ Ontology Preview) trace to their ADRs.

### BACKSTAGE — Fluent v9 mapping

| Block | Best-fit control |
|-------|------------------|
| Tab bar | `TabList` + `Tab` (already) |
| Headline stat tiles | `Card` + `Text size={800}` + `Caption1` |
| Pipeline / maturation strips | composed `Badge`/`Text` + `ChevronRight` icons, or `Breadcrumb` |
| Four-proof cards / Story pillars | `Card` grid (keep) |
| Copilot roster | `Badge` row or `AvatarGroup` |
| Evidence BOM cards | `DataGrid` (sortable by readiness) or `Card` grid; readiness `Badge` (Ready→success / Blocked→danger); provenance `Link` to `docs/bom.yaml` |
| GA-parity toggles (CH Nord × T-SHOW / GA-Parität / BVA) | `TabList` or `SegmentedControl`-style `TabList` |
| Roles & RBAC matrix | `DataGrid` |

### BACKSTAGE — summary

Target BACKSTAGE ≈ **60% and diverging upward**: the **evidence + roles tabs are real,
repo-grounded, and should be kept/extended** (they already beat the baseline on proof depth).
The Story tab is the parity gap — restore the 3 headline stat tiles, the PLAN→…→RELEASE and
DEV→…→PROD strips, and the 8-copilot roster (all derivable from repo sources). Sprint-6 scope.

---

## Cross-cutting: Data & insight requirements to support the target state

The current per-board payloads are thin (3–4 flat items). The desired boards need richer
**contracted** datasets served through `golden-source-client` (live from the Sprint 22
medallion when `VITE_GOLDEN_SOURCE_URL` is set, else synthesized + `simulated` badge). Below:
the **entities**, the **data points** (fields), and the **derived insights** (what the agent
computes and returns as reco) each board requires.

### Shared building blocks (all boards)

- **ScenarioScope** — `{ hospital(s), windowHours, pinned }` (exists). Add multi-hospital +
  time-window selection for `aggregated` scope.
- **Provenance** — `live | simulated` per dataset (exists) — must be per-payload, surfaced by
  the badge.
- **ResidualPressure** — carried role→role (exists): `{ fromAgent, headline, metrics }`. The
  golden thread needs each board's `toHandoff` to emit the residual the next board consumes.
- **GroundedReco (NEW, needed)** — extend `GroundedReply` to a structured reco:
  `{ contextChip, readParagraph, levers: [{ text, impactLabel, impactValue }], primaryCta:
  { label, handoffTo?/action }, projection, citations[], provenance }`. Flat `answer:string`
  cannot render the baseline lever/impact/CTA UI. **This is the key data-shape change.**
  See the refined v2 contract below (derived from all six boards' reco panels).

### Refined `GroundedReco` contract (v2 — covers all 6 boards incl. CSA)

Evidence: reco panels in every `surfaces/0N-*.html`. Impacts are **heterogeneous** (beds,
buffer, time `4h→90m`, routing `→ sba`, trust `Trust-A`/`Lage 2`, probability `~68%`, status
`nominal`/`filtered`), and CTAs come in **three kinds** (handoff / action / navigate).

```ts
type Provenance = 'live' | 'simulated';
type ImpactTone = 'beds' | 'buffer' | 'time' | 'routing' | 'trust' | 'probability' | 'status';
type ChipTone   = 'over' | 'watch' | 'ok' | 'blocked' | 'pending' | 'ranked' | 'signal';
type CtaKind    = 'handoff' | 'action' | 'navigate';

interface RecoContextChip { subject: string; qualifiers?: string[]; status?: string; tone: ChipTone; }
interface RecoLever   { text: string; impact?: { label: string; tone?: ImpactTone }; }         // numbered
interface RecoCta     { label: string; kind: CtaKind; target?: AgentId | string; requiresApproval?: boolean; }

interface GroundedReco {
  agentLabel: string;         // "Occupancy Copilot — context picked up"
  contextChip: RecoContextChip;
  read: string;               // reasoned paragraph
  levers: RecoLever[];        // ordered actions w/ heterogeneous impact chips
  primaryCta?: RecoCta;       // handoff (→dca), action (Release 2 beds), navigate (See lever)
  projection?: string;        // footnote e.g. "Projected peak 102% → 94% if actions taken"
  citations: string[];        // gold.* provenance
  provenance: Provenance;     // drives the live/simulated badge on the reco
  refused?: boolean;          // HITL gate blocked (deploy/delete ceiling)
}
```

- **Back-compat:** keep `GroundedReply` for the free-form chat drawer; `GroundedReco` is the
  structured shape for **insight/row/lever selection**. `rail-context` needs a
  `activeReco: GroundedReco | null` slot and the board must stop discarding the promise.
- **CTA semantics:** `handoff` carries `target` agent + `requiresApproval` for write/deploy
  (BMCA move = HITL-02; CSA Run = `approved-to-apply`); `refused:true` renders the blocked
  state instead of executing.
- **Ask-about chips** are board-level (not per-reco): add `askAbout: string[]` to each
  board payload (e.g. OOA: "Which ward tips first?", "What if flu peaks early?", "ICU staffing risk").

### CSA signal → scenario → probability data model (refined)

CSA is the only board whose *board data* (not just reco) encodes the Trust-A pipeline:

```ts
type Certainty = 'Likely' | 'Possible' | 'Unlikely';       // qualitative
const CERTAINTY_TO_PROBABILITY: Record<Certainty, number> = { Likely: 68, Possible: 31, Unlikely: 6 };

interface ExternalSignal {                     // DC-EXT-SIGNAL-v1 (Sprint 21 Trust-A)
  source: 'MeteoSwiss' | 'BAG/FOPH' | 'Alertswiss/BABS' | 'SED-ETH';
  feed: string;                                 // "STAC + Open-Meteo", "FDSN 5-min poll", "Polyalert CAP"
  status: string;                               // "heat L3/5 Actual", "RSV trend ▲", "danger level 1/5", "quiet"
  trustClass: 'Trust-A';
  lageLevel?: string;                           // "Lage 2"
  certainty: Certainty; probability: number;    // derived via CERTAINTY_TO_PROBABILITY
  feedsLever?: string;                          // "ED-surge lever" | "transfer-hold gate" | "escalation branch"
  licence: string; provenance: string;         // required by the data-quality gate
  filtered?: boolean;                           // Test/quarantined signals do not trigger
}

interface Scenario {                            // e.g. SC-01
  id: string; name: string; bedImpact: number; isSpof: boolean;
  probability: number; triggerSignal?: string; costModel?: string; escalation?: string;
}

interface ScenarioRun {                         // Cosmos-backed (cosmos-mcp), csa-simulate notebook
  id: string; scenarioId: string; params: Record<string, unknown>;
  status: 'draft' | 'running' | 'complete'; result?: Record<string, unknown>;
}
```

- The **certainty→probability** mapping is a shared constant, not a component literal.
- `external_signal` rows must pass the `data-quality-agent` `DC-EXT-SIGNAL-v1` gate (schema,
  dedup, quarantine, provenance, licence). `filtered` signals render but do not arm a lever.
- `ScenarioRun` is the only board needing **persistence** (Cosmos via `cosmos-mcp`); Run is a
  `deploy`-ceiling action gated by `approved-to-apply`.

### Per-board data model

| Board | Entities (Gold tables) | Key data points | Derived insights (agent-computed) |
|-------|------------------------|-----------------|-----------------------------------|
| **OOA** | `ward_pressure`, `signal_channel`, `specialisation_stream`, `capacity_forecast` | ward: now%, 72h-trend, forecast%, flag(OVER/WATCH/OK), beds n/N; channel: id/label/active; stream: label/flag/fedBy[]; capacity: currentBeds, forecastBeds, totalBeds, gapBeds | "why pressure rising" bullets; per-ward levers (step-downs, defer electives); site-gap plan → handoff to dca |
| **DCA** | `discharge_worklist`, `capacity_barrier` | patient: anon id, ward, readiness(READY/BLOCKED/PENDING), barrier, estFreeHours; barrier: name, owner, ageHours, clearsIn, bedImpact, flag | per-patient unblock playbook; ranked barrier remediation; residual → loop-back to ooa |
| **BMCA** | `placement_request`, `placement_barrier`, `bed_state`, `admissions_stream` | request: anon id, from→to ward, priority, waitHours; bed KPIs: util%, freeBeds, target, openDischarges, slaRisk; live admits/discharges (eventstream) | placement playbook; reallocation levers (X beds A→B); HITL-gated move (write) |
| **ORSA** | `elective_or_schedule`, `reslot_lever` | case: id, specialty, slotTime, postOpWard, bedsNeeded, flag; lever: reslot from→to, bedsProtected | reslot playbook; levers ranked by beds protected; residual → loop-back |
| **SBA** | `shift_gap`, `staffing_lever` | gap: unit, role(RN/HCA), shift, fteGap, reliefTarget; lever: move from→to, fte, bedsCovered | staffing playbook; levers ranked by beds covered; surge-bed enablement |
| **CSA** | `external_signal` (Trust-A: MeteoSwiss, Alertswiss/BABS, SED-ETH, BAG/FOPH), `internal_signal`, `scenario`, `scenario_run`, `resilience_lever` | ext signal: source, type, certainty, validFrom/To, licence, provenance; scenario: id, trigger, probability, bedImpact; run: params, result, status; lever: action, bedsProtected | signal→scenario→probability mapping (`DC-EXT-SIGNAL-v1`); scenario simulation (`csa-simulate` notebook); resilience levers ranked; deploy-ceiling + `approved-to-apply` |

### Data provenance & governance points (per non-negotiable principles)

- **No fabricated data:** every field above flows through `golden-source-client`; where the
  medallion table is unpopulated, the layer synthesizes and flags `simulated`. No numbers in
  components.
- **No fabricated insights:** every "derived insight" column is an `agent-host` round-trip
  returning `GroundedReco` (with citations to Gold tables, e.g. `gold.ward_pressure`). Degraded
  responses flagged.
- **PHI-safe:** all patient rows use synthetic anon IDs (PT-xxxx); CSA external signals carry
  licence + provenance metadata (Sprint 21 Trust-A) and must pass the `data-quality-agent`
  `DC-EXT-SIGNAL-v1` gate.
- **RLS:** BMCA's Power BI embed is Direct Lake **RLS by hospital** — the scope selector must
  drive both the golden-source query and the embed filter.
- **Golden-thread reproducibility:** Demo mode pins a scenario slice so the same figures
  (Medicine A 102%, site −16 → −7 → −3 → −1 → 0 across the chain) reproduce deterministically.

### Data-layer refactor tasks (consolidated)

1. Extend each `*-data.ts` payload to the entities/fields above (worklist + ranked-levers +
   board-specific KPIs), keeping the live-or-synthesized adapter pattern.
2. Add the `GroundedReco` structured reply and make the rail render it (fix the discarded
   promise + add a reply slot to `rail-context`).
3. Define the Sprint 22 Gold-table contract (names + columns above) so `golden-source-client`
   live mode has a target schema; document PHI/licence/RLS constraints.
4. CSA: add the signal ingest + scenario/probability model + `scenario_run` (Cosmos) memory.

---

## Worked `GroundedReco` examples (per board)

One canonical instance per board, transcribed verbatim from the locked prototype
reco panels (`surfaces/0N-*.html`). These lock the contract by showing every
`ImpactTone`, `ChipTone`, and `CtaKind` is actually exercised. Strings are the
target copy the enriched `*-data.ts` + `agent-host` must reproduce.

### 1. OOA — Medicine A ward selection (`#reco-emergency`)

```ts
const ooaMedicineA: GroundedReco = {
  agentLabel: 'Occupancy Copilot — context picked up',
  contextChip: { subject: 'Medicine A', qualifiers: ['102% forecast'], status: 'OVER', tone: 'over' },
  read: 'Medicine A tips to 102% within 72h — 6 flu admissions inbound against only 2 planned discharges. Three levers close the gap:',
  levers: [
    { text: 'Expedite 6 discharge-ready patients before 17:00.',        impact: { label: '−6 beds',   tone: 'beds'   } },
    { text: 'Divert 3 low-acuity admits to Medicine B (8% spare).',     impact: { label: '+3 buffer', tone: 'buffer' } },
    { text: 'Flag 2 length-of-stay outliers >9 days for review.',       impact: { label: '−2 / 48h',  tone: 'beds'   } },
  ],
  primaryCta: { label: 'Open discharge worklist → dca', kind: 'handoff', target: 'dca-agent' },
  projection: 'Projected peak 102% → 94% if actions are taken.',
  citations: ['gold.ward_pressure', 'gold.capacity_forecast'],
  provenance: 'simulated',
};
```

Exercises: `tone:'over'`, impacts `beds`/`buffer`, `kind:'handoff'`, `projection`.
Sibling recos (`#reco-icu` WATCH `+2 ICU beds`, `#reco-surgery` WATCH, `#reco-cardio` OK,
`#reco-gap` site −16) reuse the same shape with `tone:'watch'|'ok'`.

### 2. DCA — TTO-meds barrier (`#reco-b-tto`, fastest bed)

```ts
const dcaTtoBarrier: GroundedReco = {
  agentLabel: 'Discharge Copilot — barrier picked up',
  contextChip: { subject: 'TTO meds', qualifiers: ['1 bed', 'fastest'], tone: 'ranked' },
  read: 'One Medicine A patient (PT-4488) is held only by an undispensed take-home script. This is the quickest bed on the board:',
  levers: [
    { text: 'Auto-page pharmacy to expedite the TTO to the front of the queue.', impact: { label: '4h → 90m',  tone: 'time' } },
    { text: 'Pre-fill the discharge summary for e-sign in parallel.',            impact: { label: 'saves 20m', tone: 'time' } },
  ],
  primaryCta: { label: 'Expedite TTO (1 bed)', kind: 'action' },
  citations: ['gold.capacity_barrier', 'gold.discharge_worklist'],
  provenance: 'simulated',
};
```

Exercises: `tone:'ranked'`, impact `time` (`4h → 90m`), `kind:'action'`.
The coordinated-plan reco (`COORDINATED PLAN · 8 beds · 72h`) uses
`primaryCta: { label: 'Publish plan + sync to ooa', kind: 'handoff', target: 'ooa-agent' }`
(loop-back).

### 3. BMCA — staffing-cap barrier → sba (routing handoff, HITL-gated)

```ts
const bmcaStaffingCap: GroundedReco = {
  agentLabel: 'Bed-flow Copilot — barrier picked up',
  contextChip: { subject: 'Staffing cap', qualifiers: ['1 bed', 'aging risk'], tone: 'over' },
  read: 'Ranked last by yield but first by urgency: 1 elective post-op bed (RQ-2208) is physically ready, but Medicine A is at its safe nurse:patient ratio — opening it needs staff. This is beyond bed management, so hand it to sba-agent now so the ward is covered in time:',
  levers: [
    { text: 'Hand the staffing gap to sba-agent (Medicine A late shift).', impact: { label: '→ sba',    tone: 'routing' } },
    { text: "Hold the bed reserved so it isn't reassigned.",              impact: { label: 'safe hold', tone: 'status'  } },
    { text: "Escalate if sba can't cover before 18:00.",                  impact: { label: 'SLA 2h',    tone: 'time'    } },
  ],
  primaryCta: { label: 'Hand to sba-agent →', kind: 'handoff', target: 'sba-agent', requiresApproval: true },
  citations: ['gold.placement_barrier', 'gold.bed_state'],
  provenance: 'simulated',
};
```

Exercises: impact `routing` (`→ sba`, purple chip) + `status` (`safe hold`),
`requiresApproval:true` (the actual bed move is a `write` — HITL-02). Bed-turnaround
barrier reco shows impact `time` `2h → 40m`.

### 4. ORSA — defer low-acuity lever (rank 1)

```ts
const orsaDeferLever: GroundedReco = {
  agentLabel: 'OR-flow Copilot — lever picked up',
  contextChip: { subject: 'Defer low-acuity', qualifiers: ['2 beds', 'rank 1'], tone: 'ranked' },
  read: 'Your highest-yield lever: 2 low-acuity orthopaedic electives (OR-3301, OR-3303) post-op into Medicine A but can safely wait a week. Defer both and protect 2 beds in the 72h window:',
  levers: [
    { text: 'Offer both patients a next-week slot (no clinical harm).', impact: { label: '+2 beds',  tone: 'beds'   } },
    { text: 'Release the OR block for a time-critical case.',           impact: { label: 'OR freed', tone: 'status' } },
    { text: 'Post the protected beds to the ooa live view.',           impact: { label: 'live sync', tone: 'status' } },
  ],
  primaryCta: { label: 'Defer 2 electives (protect 2 beds)', kind: 'action' },
  citations: ['gold.elective_or_schedule', 'gold.reslot_lever'],
  provenance: 'simulated',
};
```

Exercises: `+beds` (protect, not free), `status` impacts. The time-critical lever
hands to sba (`→ sba`, `requiresApproval`) — same routing shape as BMCA.

### 5. SBA — oncology-skill lever (binding constraint, confirm-back → orsa)

```ts
const sbaOncologyLever: GroundedReco = {
  agentLabel: 'Staffing Copilot — lever picked up',
  contextChip: { subject: 'Oncology skill', qualifiers: ['2 beds', 'critical'], tone: 'over' },
  read: 'The binding constraint. OR-3307 and OR-3308 are time-critical oncology cases orsa is proceeding into Medicine A — their 2 post-op beds are useless without an oncology-competent RN. Exactly 1 is free on late shift; secure them now:',
  levers: [
    { text: 'Assign the free oncology RN to the 2 post-op beds (Medicine A late).', impact: { label: '2 beds safe', tone: 'beds'    } },
    { text: 'Confirm back to orsa the beds are staffed & reserved.',               impact: { label: '→ orsa ✓',    tone: 'routing' } },
    { text: 'Flag csa if that RN becomes unavailable.',                            impact: { label: '→ csa',       tone: 'routing' } },
  ],
  primaryCta: { label: 'Secure oncology cover (2 beds)', kind: 'action' },
  citations: ['gold.shift_gap', 'gold.staffing_lever'],
  provenance: 'simulated',
};
```

Exercises: two distinct routing targets (`→ orsa ✓` confirm-back, `→ csa` escalate).
The agency/bank lever hands to csa (`Hand to csa-agent →`, `kind:'handoff'`,
`target:'csa-agent'`).

### 6. CSA — external signal → scenario → probability (navigate CTA)

```ts
const csaHeatRsvSignal: GroundedReco = {
  agentLabel: 'Scenario Copilot — signal picked up',
  contextChip: { subject: 'Heat + RSV → ED surge', qualifiers: ['external signal'], tone: 'signal' },
  read: 'Two Trust-A sources align: MeteoSwiss heat warning L3/5 and BAG/FOPH RSV surveillance rising. Both push the ED surge scenario (F8 heat · F6 respiratory). Certainty Likely maps to ~68% — this is the SC-02 shock, now signal-backed rather than assumed.',
  levers: [
    { text: 'MeteoSwiss STAC + Open-Meteo · heat L3/5 · status Actual.',             impact: { label: 'Trust-A', tone: 'trust'       } },
    { text: 'BAG/FOPH respiratory surveillance · RSV trend ▲.',                      impact: { label: 'Lage 2',  tone: 'trust'       } },
    { text: 'Certainty Likely → probability 68% · feeds the ED-surge lever.',        impact: { label: '~68%',    tone: 'probability' } },
  ],
  primaryCta: { label: 'See the surge-buffer lever →', kind: 'navigate', target: 'reco-lever-buffer' },
  projection: 'External signal → scenario → probability → the resilience lever that absorbs it.',
  citations: ['gold.external_signal', 'gold.scenario'],
  provenance: 'simulated',
};
```

Exercises: `tone:'signal'`, impacts `trust` (`Trust-A`/`Lage 2`) + `probability` (`~68%`),
`kind:'navigate'` (intra-board jump to a lever reco, no agent handoff). The
**filtered** variants prove the `status` tone gates a lever off:

- Civil-alert reco: a `Test` inbound → `{ label: 'filtered', tone: 'status' }` — lever **not** armed; `Possible → ~31%`.
- Seismic reco: `{ label: 'nominal', tone: 'status' }`, danger level 1/5 → watch only; `Unlikely → ~6%`; CTA `kind:'navigate' target:'reco-lever-escalate'` (purple, high-impact).
- Scenario shock recos (`SC-01` oncology sick-call SPOF, ED surge +4, transfer surge) use `agentLabel: '… — shock simulated'`, `impact:'beds'` (`+4 beds`) and, for the combined worst-case, `primaryCta: { label: 'Escalate to site command →', kind:'navigate', target:'START' }` — the only branch that leaves the functional layer.

### Coverage matrix (contract is fully exercised)

| Facet | Values seen across worked examples |
|-------|-------------------------------------|
| `ChipTone` | over (OOA/BMCA/SBA), watch (OOA sib), ok (OOA sib), ranked (DCA/ORSA), signal (CSA), + blocked/pending on DCA patient recos |
| `ImpactTone` | beds, buffer, time (`4h→90m`, `2h→40m`), routing (`→sba`/`→orsa ✓`/`→csa`), trust (`Trust-A`/`Lage 2`), probability (`~68%`/`~31%`/`~6%`), status (`safe hold`/`filtered`/`nominal`/`live sync`) |
| `CtaKind` | handoff (OOA→dca, DCA→ooa, BMCA→sba, SBA→csa; some `requiresApproval`), action (DCA/ORSA/SBA), navigate (CSA intra-board + →START) |
| `provenance` | simulated everywhere in Demo mode (pinned slice); `live` when Gold tables populated |
| `refused` | set true when a `handoff`/`action` with `requiresApproval` hits the HITL/`approved-to-apply` gate unmet |

**Conclusion:** the v2 `GroundedReco` shape is sufficient and necessary — every
prototype reco maps onto it with no leftover fields and no unused enum members.
Locking recommended.

---

## Fluent UI v9 visual-matching review (control + style mapping)

Installed: `@fluentui/react-components@^9.54.17` + `@fluentui/react-icons@^2.0.270`
(Fluent 2 / v9). Cross-referenced against the current v9 catalog
(<https://react.fluentui.dev>, Fluent 2 web/react). Goal: pick the **best-fitting
native control** for every prototype element so parity is achieved with idiomatic
Fluent (accessible, themable, tokenised) rather than hand-rolled `<div>`s.

### Two structural mismatches to fix first

1. **Rail is the wrong Drawer type.** `copilot-drawer/Drawer.tsx` uses
   `Drawer type="overlay" position="end"` — it floats over content and dims the
   page. The prototype rail is **docked/persistent** beside the board. → Switch to
   **`Drawer type="inline" position="end"`** (co-exists with content, no scrim),
   with a collapse control. This alone converts the "empty chat drawer" into the
   docked reco rail.
2. **Boards are flat `Card` + subtle `Button`.** `OccupancyBoard.tsx` renders 3
   `Card`s + a `Button` row. The prototype's core is a **worklist table** and a
   **ranked lever board** — those must be **`DataGrid`**, not Cards, for row
   semantics, keyboard nav, and sortability.

### Shared reco-panel control library (all 6 boards)

| Prototype element (`.reco-*`) | Best-fit Fluent v9 control | Style / token notes |
|-------------------------------|----------------------------|---------------------|
| `reco-chip` status pill (OVER/WATCH/READY/BARRIER/SIGNAL) | **`Badge`** `appearance="tint"` `shape="rounded"` | Map `ChipTone`→`color`: over→`danger`, watch→`warning`, ok→`success`, ranked/handoff→`informative`, signal→`brand`, blocked→`danger`, pending→`warning` |
| `reco-agent` "● Copilot — context picked up" | **`Caption1Strong`** + leading **`PresenceBadge`** `status="available"` | Teal dot = brand token, not `#17B890` literal |
| `reco-read` paragraph | **`Body1`** | `colorNeutralForeground2` |
| `reco-num` numbered circle | **`Badge`** `shape="circular"` `appearance="filled"` `color="brand"` `size="small"` | Replaces the hand-styled 18px circle |
| `reco-action` lever row | **`List` / `ListItem`** (semantic) or flex row | Keyboard-navigable; number badge + text + impact badge |
| `reco-impact` chip (`−6 beds`, `4h→90m`, `→ sba`, `~68%`, `filtered`) | **`Badge`** `appearance="tint"` `size="small"` | Map `ImpactTone`→color: beds/buffer→`success`, time→`informative`, routing→`important`/custom purple, trust/probability→`brand`, status→`subtle` |
| `mock-button` primary CTA | **`Button`** `appearance="primary"` full-width + `ArrowRight` icon | Handoff CTAs get `icon`; purple cross-agent → custom `colorPalettePurple` token |
| `reco-back` "← Back to summary" | **`Button`** `appearance="transparent"` + `ArrowLeft16Regular` | Or `Link` |
| projection footnote | **`Caption1`** | `colorNeutralForeground3` |
| "Ask about" chips | **`TagGroup`** + **`InteractionTag`** (clickable) | Prompts the chat; dismiss off |
| chat input row | **`Textarea`** (auto-resize) + **`Button`** | Upgrade from single-line `Input`; keep `Enter`-to-send |
| provenance `simuliert` badge | **`Badge`** `color="warning"` `appearance="tint"` + **`InfoLabel`** tooltip | Explains the simulated/live source |
| loading state | **`Skeleton`** / `SkeletonItem` | Replace `<Text>Lädt…</Text>` |
| handoff banner (`HandoffBanner`) | **`MessageBar`** `intent="info"` + `MessageBarBody` | Carries residual + provenance `Badge`; loop-back note as `MessageBarActions` `Link` |

### Global shell

| Element | Best-fit Fluent v9 control | Notes |
|---------|----------------------------|-------|
| Left acts nav (START/MAIN/BACKSTAGE/Settings) | **`Nav`** (`@fluentui/react-nav-preview`) or vertical **`TabList`** | Nav preview matches the rail-style act switcher; else `TabList vertical` |
| MAIN 6-board sub-nav | **`TabList`** + **`Tab`**; Krise = **`Tab disabled`** | Disabled Tab already surfaces the RBAC lens |
| Demo ↔ User toggle | **`Switch`** (labelled) or 2-item **`TabList`** | Currently a toggle; keep as `Switch` w/ `label` |
| Scope / language / role-lens selectors | **`Dropdown`** / **`Menu`** + **`Badge`** for lens | Role lens as read-only `Badge appearance="tint"` |
| Theme toggle | **`Switch`** + `WeatherMoon`/`WeatherSunny` icons | Drives `FluentProvider theme` |
| User | **`Avatar`** / **`Persona`** | |
| Footer golden-thread status | **`MessageBar`** `intent="success"` or `Badge` + `Text` | "golden thread intact" state |

### Per-screen control mapping

**1. OOA (`/main/occupancy`)**

| Prototype block | Fluent v9 control |
|-----------------|-------------------|
| Ward-pressure table (Now/72h trend/Forecast/Flag, row→reco) | **`DataGrid`** — columns: Ward `Text`, Now `Text`, 72h `ArrowTrendingUp/Down` icon, Forecast `Text`, Flag `Badge`; `onSelectionChange`/row `onClick` opens the reco |
| Capacity-flow diagram (signals→streams→capacity) | Composed **`Card`** columns + **`Divider`** + `ArrowRight` between stages; signals = **`List`**, streams = `List` w/ flag `Badge`, capacity tiles = `Card` + big `Text` + **`ProgressBar`** (util %) + delta `Badge` — *no native "flow" primitive; compose with grid* |
| Per-ward KPI mini-cards | **`Card`** + `Text size={700}` + `ProgressBar` + `Badge` |

**2. DCA (`/main/discharge`)**

| Prototype block | Fluent v9 control |
|-----------------|-------------------|
| Discharge worklist (anon patients, readiness, barrier, est-free) | **`DataGrid`** — readiness `Badge` (READY→success / BLOCKED→danger / PENDING→warning); row→patient reco |
| Capacity-barriers board (ranked by bed impact) | **`DataGrid`** sorted by `bedImpact` desc, rank `Badge shape="circular"`; row→barrier reco |
| "Auto-sequence by aging & impact →" | **`Button`** `appearance="primary"` |

**3. BMCA (`/main/bed-manager`)**

| Prototype block | Fluent v9 control |
|-----------------|-------------------|
| Placement requests (from→to ward, priority, wait) | **`DataGrid`**; priority `Badge` |
| Placement barriers (ranked) | **`DataGrid`** sorted by bed impact |
| Bed-state KPIs (util%, free, target, SLA-risk) | **`Card`** + `ProgressBar` + `Badge` |
| Live admissions/discharges eventstream | **`List`** (wrap in **`Virtualizer`** if long); keep the existing Power BI Direct Lake embed inside a **`Card`** (iframe, non-Fluent) |
| **Consolidation** | Remove the duplicate "Bettenmanagement — USZ" title; the legacy S11 whiteboard + parity skeleton must merge into one board (preserve embed + eventstream) |

**4. ORSA (`/main/or-steering`)**

| Prototype block | Fluent v9 control |
|-----------------|-------------------|
| Elective-OR schedule (case, specialty, slot, ward, beds, flag) | **`DataGrid`**; flag `Badge` |
| Reslot levers (ranked by beds protected) | **`DataGrid`**/`List`; `→ sba` handoff lever `Badge color="important"` |

**5. SBA (`/main/staffing`)**

| Prototype block | Fluent v9 control |
|-----------------|-------------------|
| Coverage worklist / shift gaps (unit, role, shift, FTE gap) | **`DataGrid`**; role `Badge` (RN/HCA) |
| Staffing levers (ranked by beds covered) | **`DataGrid`**/`List`; `→ orsa ✓` / `→ csa` routing `Badge` |

**6. CSA (`/main/crisis`) — not yet deployed**

| Prototype block | Fluent v9 control |
|-----------------|-------------------|
| Trusted-signals → scenario → probability 3-column flow | **`Card`** columns + `Divider`; external signals = **`List`** w/ `Trust-A` `Badge color="brand"`; scenarios = **`DataGrid`** (probability, bedImpact, SPOF) |
| certainty→probability legend (Likely 68 · Possible 31 · Unlikely 6) | **`InfoLabel`** or **`MessageBar`** `intent="info"` |
| Scenario **Run** (simulate) | **`Dialog`** (params) → **`Spinner`** while running → result; **`MessageBar`** `intent="warning"` for the `deploy`/`approved-to-apply` gate; **`Toast`** on completion |
| `filtered`/`nominal` signals | `Badge appearance="outline" color="subtle"` — visibly de-emphasised, lever disabled |
| Escalation branch → START | **`Button`** `appearance="primary"` + `ArrowExit`/`Open` icon |

### Theming recommendation (stop hardcoding hex)

The prototype's six semantic colours are currently CSS hex. Define a **Curavias
brand theme** so they become tokens:

```ts
// theme/curavias-brand.ts
import { createLightTheme, createDarkTheme, BrandVariants, Theme } from '@fluentui/react-components';
const curavias: BrandVariants = { /* teal ramp seeded from #17B890 → 10..160 */ };
export const curaviasLight: Theme = createLightTheme(curavias);
export const curaviasDark: Theme  = createDarkTheme(curavias);
```

- **Brand teal `#17B890`** → the brand ramp (`colorBrandBackground` etc.) — drives primary CTAs, presence dots, Trust-A badges.
- **danger red `#ff3b30`** → `colorPaletteRedForeground1` / `Badge color="danger"`.
- **warning amber `#ff9f0a`** → `colorPaletteDarkOrange*` / `color="warning"`.
- **success green `#34c759`** → `colorPaletteGreenForeground1` / `color="success"`.
- **informative blue `#365B7D`** → `colorPaletteBlue*` / `color="informative"` (plan/loop-back).
- **routing purple `#8a6fbf`** → `colorPalettePurple*` — the cross-agent handoff accent (`→ sba`/`→ csa`). Expose as a single custom token so all six boards share it.

All `makeStyles` blocks then reference tokens only — no literal hex — which also
makes the Demo/User + light/dark themes switch cleanly via `FluentProvider`.

### Accessibility upshot (why the control swap matters)

- `DataGrid` gives ARIA `grid` semantics + arrow-key nav + sortable headers — the
  clickable-`Card` worklists lose all of that.
- `Badge`/`MessageBar`/`InfoLabel` carry the right roles + contrast tokens for the
  status/provenance chips, versus hand-coloured spans that fail WCAG contrast in
  dark mode.
- This section is the visual/a11y contract the `ux-design-agent` verifies with
  Playwright + axe during the refactor.

---

## Screen 9 (cross-cutting) — the Copilot agent interaction model per MAIN board

> This is the substantial gap surfaced in review: the per-role **Copilot agent**
> is the heart of every MAIN board, and the current app ships a hollow version of
> it. This section is the full interaction contract — show/hide, left-plane →
> recommendation routing, response rendering, actionable-insight provenance, the
> Fabric IQ / Foundry IQ data the agent needs, and the ask-about prompts.

### 9.1 Reference model (prototype) — the target behaviour

Every board (`surfaces/01-ooa` … `06-csa`) ships an identical Copilot rail. The
OOA rail is the reference; the other five are structurally the same with role
copy. Observed behaviour, verbatim from the markup:

1. **Docked, full-height right rail — never an overlay.** Header
   `● <Role> Copilot` + a collapse control (`−`). Collapsing adds a
   `copilot-collapsed` class that shrinks the rail to a thin strip; it does **not**
   disappear while you are on a board. The rail owns the right shell column.
2. **Proactive default state (`#reco-default`, shown on load).** The rail is
   *never empty*: it opens on a "Why is pressure rising?" cause read (2 bullets),
   a "Suggested next step", and a primary CTA (`See 8 discharge candidates →`).
   The agent has already reasoned over the board before the user clicks anything.
3. **Left/centre-plane insights drive the reco.** Clicking a ward row, a
   specialisation stream, or the site-gap card runs the same four steps: (a)
   `classList.remove('copilot-collapsed')` — auto-expands the rail; (b) marks the
   clicked insight `.sel`; (c) hides every `.reco` panel and shows the one matching
   the insight (`#reco-emergency`, `#reco-icu`, `#reco-gap`, …); (d) scrolls the
   rail body to top. **The clicked context selects the recommendation.**
4. **Reco panel = the `GroundedReco` v2 contract** (see §3). Each panel is:
   `reco-back` ("← Back to summary") · status **chip** (tone OVER/WATCH/OK/GAP) ·
   agent line "● Role Copilot — context picked up" · reasoned **read** ·
   numbered **levers** each with a heterogeneous **impact chip**
   (`−6 beds` / `+3 buffer` / `−2 / 48h`) · a primary **CTA** (usually a handoff
   to the next agent, `Open discharge worklist → dca`) · a **projection** footnote
   (`Projected peak 102% → 94% if actions are taken.`).
5. **"Ask about" chip row** — three pre-canned prompts per board (see §9.8).
6. **Chat foot** — free-text input (`Ask the <Role> Copilot…`) + send.
7. **"← Back to summary"** returns the rail to its proactive default reco.

The mental model: the rail is a **standing analyst** (default reco) that
**re-focuses on whatever you click** (context reco) and **answers free questions**
(chat) — three states in one docked surface.

### 9.2 Current app model — what exists, and why it reads as hollow

The app splits this one surface into **two disjoint systems that never meet**:

| Concern | Code today | Behaviour |
| ------- | ---------- | --------- |
| Visible agent surface | `shell/planes/AgentPlane.tsx` → `useAgentInvoker(agent)` + `ConversationView` | 48px icon rail ↔ 360px panel; a free-chat box that starts **empty** |
| Insight routing | `copilot-rail/InsightRouter.ts` `routeInsight()` + `copilot-rail/rail-context.tsx` | Board click calls `openWithContext(insight)` then `invokeInsight(...)` and **discards the returned `GroundedReply`** |

Concrete defects (all confirmed in code):

- **D1 — the reco is thrown away.** `OccupancyBoard.tsx` calls
  `void routeInsight(insight, …)`; `routeInsight` returns a `GroundedReply` that
  nobody stores. `rail-context.tsx` keeps only `activeContext`, never a reply.
  `AgentPlane` reads `useCopilotRail().open` but **not** `activeContext` — so a
  click opens the panel and shows the *unrelated* free-chat turns, not a reco.
- **D2 — no proactive default.** `AgentPlane` renders an empty `ConversationView`
  until the user types. The prototype's "Why is pressure rising?" default is
  absent, so the agent looks inert on load.
- **D3 — reply shape too thin.** `GroundedReply = { answer, citations, refused }`
  is a single text blob. `invokeAgent`'s offline mock returns one fixed German
  paragraph regardless of context. There is no chip / read / numbered levers /
  impact chips / CTA / projection — i.e. no `GroundedReco` (§3).
- **D4 — flat rendering.** `ConversationView` renders plain user/agent bubbles +
  a "Quellen:" citation caption. It cannot render a structured reco.
- **D5 — no ask-about chips** anywhere in the app.
- **D6 — thin insight contexts.** Each `*-board.ts` `insights()` emits only
  `{ id, label, context:{few ids+metrics} }` and OOA filters to `occupancyPct ≥ 100`
  only — so the prototype's WATCH (ICU 95%, Surgery 88%), OK-donor (Cardiology),
  and SITE-GAP contexts never appear. The context carries **no levers, impacts,
  read, tone, or projection**.
- **D7 — CTA/handoff not wired to the reco.** `toHandoff()` exists but the reco's
  primary CTA is not connected to it, so "→ dca" is not actionable.
- **D8 — binary show/hide, no "back to summary".** `AgentPlane` is open/closed
  only; there is no collapse-to-strip-while-docked and no return-to-default.

### 9.3 Show / hide UX — target contract (Fluent)

Keep the agent as a **docked shell plane** (not the overlay `Drawer` — reaffirms
the §6 Fluent finding) with **three explicit states**:

- **Collapsed strip** — a ~48px rail with the bot icon and an **unread/insight
  dot** (`CounterBadge` dot) when a new reco is waiting. Toggle via the header
  `−` / bot button. Persist per session.
- **Default (proactive)** — shows `defaultReco(boardData)` the moment the board
  loads; no user action required.
- **Context** — shows `recoFor(insight, boardData)` when a left-plane insight is
  clicked; the strip auto-expands (mirror `classList.remove('copilot-collapsed')`)
  and a `← Back to summary` (`Button appearance="subtle"` + `ArrowLeftRegular`)
  returns to Default.

Never fully unmount the plane while on a board; collapsing is visual only, so
context is preserved. Respect the RBAC ceiling badge already rendered
(`capabilities.agentCeiling`).

### 9.4 Left-plane → recommendation routing (the wiring fix)

The pipeline that must exist end-to-end:

```text
board insight (left/centre plane)
  → ContextInsight { id, label, context }               // enriched, see §9.6
  → routeInsight(insight): stores activeReco + opens     // stop discarding
  → invokeReco(agent, context)                            // agent boundary
      → Foundry Agent Service (eastus2) <role>-agent      // reasoning/orchestration
          → Fabric IQ da_hospital_capacity (ADR-0034)     // grounded query surface
      → GroundedReco { chip, read, levers[], cta, projection, provenance }
  → AgentPlane renders activeReco (else defaultReco, else chat turns)
```

Minimal code deltas:

- `rail-context.tsx`: add `activeReco: GroundedReco | null` + `setActiveReco`;
  keep `activeContext` for telemetry.
- `InsightRouter.ts`: `routeInsight` awaits the reco and calls `setActiveReco`
  (never `void`).
- `RoleBoard` interface: add `defaultReco(data): GroundedReco` and
  `recoFor(insight, data): GroundedReco` (or resolve both via the agent boundary).
- `AgentPlane.tsx`: render precedence **activeReco → defaultReco → chat turns**;
  add the collapsed-strip + back-to-summary states.
- `agent-manifest.ts`: `invokeReco()` returns `GroundedReco`; the offline mock
  derives structure **from the passed context** (no fabrication at the board).

### 9.5 Response rendering — best-fit Fluent v9 mapping for the chat window

Target: get as close to the prototype reco panel as stable Fluent v9 allows.
Per reco element:

| Prototype element | Best-fit Fluent v9 | Notes |
| ----------------- | ------------------ | ----- |
| `reco-chip` status | `Badge` (`color` by tone: danger/warning/success/brand) | tone from `ChipTone`; carries WCAG contrast tokens |
| `reco-agent` line | `Caption1` + `PresenceBadge` (or `Persona` `size="extra-small"`) | "● Role Copilot — context picked up" |
| `reco-read` | `Body1` | reasoned prose |
| numbered `reco-action` | row: `CounterBadge count={n}` + `Body2` + impact `Badge` | one row per lever; keep number/desc/impact three-up |
| `reco-impact` chip | `Badge appearance="tint"` (tone by `ImpactTone`) | `−6 beds` / `+3 buffer` / `−2 / 48h` |
| primary CTA | `Button appearance="primary"` (+ handoff `→` icon) | fires the `toHandoff` route; `deploy` CTAs gate on HITL |
| projection footnote | `Caption1` (secondary colour) | `Projected peak … → …` |
| refusal / HITL state | `MessageBar intent="warning"` | replaces the ad-hoc `Badge color="danger"` |
| `← Back to summary` | `Button appearance="subtle"` + `ArrowLeftRegular` | returns to default reco |
| "Ask about" chips | `InteractionTag` / `Tag` (clickable) — fallback `Badge` buttons | click fills the input or fires a canned turn |
| chat input + send | `Input` + `Button` (`SendRegular`) | already present; keep |
| chat bubbles | keep `ConversationView`, add a `Card`-based reco block | free Q&A stays as bubbles; structured reco renders as a card |

Package note: an emerging `@fluentui-copilot/react` set (CopilotChat, AI bubbles,
skeletons) exists but is **preview** — do not add it on the parity critical path;
build the reco card from stable v9 primitives above. Revisit post-parity.

Suggested component: a shared `<RecoPanel reco={GroundedReco} />` used by both the
default and context states, so all six boards render identically (mirrors the
prototype's single `.reco` template).

### 9.6 Actionable insights — inventory + provenance (per board)

"Actionable insight" = a clickable element in the left/centre plane whose context
the agent turns into a reco. Current app contexts are thin (D6); the target
enriches each so the agent can ground levers/impacts/projection.

| Board (agent) | Clickable insights (target) | Current app source | Context to send |
| ------------- | --------------------------- | ------------------ | --------------- |
| OOA (`ooa-agent`) | ward rows, specialisation streams, **site-gap** card — OVER/WATCH/OK/GAP | `channels` filtered `≥100%` only | ward id, current%, forecast%, tone, Δbeds, window |
| DCA (`dca-agent`) | discharge candidate rows, blocker groups | `candidates.expedite===true` | candidate id, ward, blocker, bedsFreeable, ETA |
| BMCA (`bmca-agent`) | reallocation proposals, ED-boarder queue | all `reallocations` | from/to ward, beds, boarder count, eligibility |
| ORSA (`orsa-agent`) | deferrable cases, time-critical cases, off-peak slots | `cases.deferable===true` | case id, specialty, slot, bedsImpact, urgency |
| SBA (`sba-agent`) | staff moves, uncovered shifts, agency asks | all `moves` | from/to unit, role, FTE, coverage gap |
| CSA (`csa-agent`) | scenario cards (stress tests), response levers | all `scenarios` | scenario id, probability, bedDayImpact, lever set |

The gap: today the context is **identifiers only**; the reco text (read, levers,
impacts, projection, tone) is not derivable from it. Two options —
(a) the **data layer** supplies `defaultReco`/`recoFor` from enriched Gold
payloads, or (b) the **agent** computes them from the context grounded on Fabric.
Recommendation: **(b) for live/demo** (Foundry + Fabric IQ), with **(a) as the
offline/simulated fallback** so CI and no-backend demos still render structured
recos deterministically.

### 9.7 Data the Copilot needs — Fabric IQ / Foundry IQ

Per the registry + [ADR-0034](../../adr/0034-fabric-iq-demo-scope-artefacts.md):
the reasoning lives in the **Foundry Agent Service (eastus2)** `<role>-agent`; the
**grounding** comes from the **Fabric IQ** data agent `da_hospital_capacity`
(`b2e53c23-…`) over the Gold semantic model. The `ooa-agent` already consumes it
live in demo. Per-board Gold inputs needed to produce a `GroundedReco`:

| Board | Gold tables / measures the agent must query to fill read + levers + projection |
| ----- | ------------------------------------------------------------------------------ |
| OOA | `fact_capacity_baseline` (beds, occ%), `capacity_forecast` (72h occ% per ward), `admissions_forecast` (inbound, seasonality), `discharge_candidates` (ready-now), `los_outliers`, ward adjacency/overflow eligibility |
| DCA | `discharge_candidates` (blocker, bedsFreeable, ETA), `spitex_slots` lead-time, `rehab_transfer_queue`, imaging/pharmacy readiness |
| BMCA | `bed_assignment` (current), `ed_boarders` queue, `ward_capacity` spare, transfer/isolation eligibility |
| ORSA | `or_schedule` (elective vs slot), `case_urgency`/time-critical flags, post-op bed demand, off-peak room availability |
| SBA | `roster` (FTE by unit/shift), `skill_mix` requirements, `sick_calls`, `agency_pool`, surge-bed staffing ratios |
| CSA | `scenario_library` (probability, bed-day impact), `response_levers`, cross-board residual pressures, `simulation-runs` (Cosmos) |

Every reco must carry `provenance` (`live` when Fabric-grounded, `simulated`
offline) and an as-of stamp — mirrors the §5 board-data provenance rule. The
`citations[]` should reference the actual Gold objects (e.g.
`gold.capacity_forecast`, `gold.discharge_candidates`), not placeholder strings.

### 9.8 "Ask about" prompt inventory (all six boards)

Verbatim from the prototype; these seed each board's chip row and bind to a
grounded agent turn (click → fill input or fire canned prompt → `GroundedReply`):

| Board | Ask-about prompts |
| ----- | ----------------- |
| OOA | "Which ward tips first?" · "What if flu peaks early?" · "ICU staffing risk" |
| DCA | "Fastest 5 beds today?" · "Any discharge risk?" · "Spitex lead time" |
| BMCA | "Fastest 2 placements?" · "ED boarders waiting?" · "Any inbound transfers?" |
| ORSA | "Which cases are deferrable?" · "Any time-critical today?" · "Thursday off-peak room?" |
| SBA | "Oncology cover secured?" · "Any agency needed?" · "Night rollover staffed?" |
| CSA | "What breaks first?" · "Is the sick-call covered?" · "Do we need agency?" |

These are `askAbout` (board-level) prompts, distinct from the per-insight reco
(selection-level). They belong on the flat `GroundedReply` chat path, not the
`GroundedReco` panel.

### 9.9 Refactor tasks (feeds sprint sequencing)

- **T-A** — enrich `ContextInsight`/board payloads with tone + lever/impact/
  projection inputs (or delegate to the agent); add missing OOA WATCH/OK/GAP
  contexts (D6).
- **T-B** — add `GroundedReco` + `activeReco` to `rail-context`; stop discarding
  the reco in `routeInsight` (D1).
- **T-C** — build shared `<RecoPanel>` from the §9.5 Fluent mapping; wire
  precedence activeReco → defaultReco → chat (D2, D3, D4).
- **T-D** — three-state docked plane: collapsed strip + auto-expand +
  back-to-summary (D8).
- **T-E** — add the ask-about chip row bound to `GroundedReply` turns (D5).
- **T-F** — wire the reco CTA to `toHandoff` routing (D7).
- **T-G** — ground `invokeReco` via Foundry `<role>-agent` + Fabric IQ
  `da_hospital_capacity`; offline deterministic structured fallback (§9.7).


