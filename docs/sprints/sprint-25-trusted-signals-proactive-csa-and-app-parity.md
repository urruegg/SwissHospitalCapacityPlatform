# Sprint 25 — Trusted Signals to Proactive CSA and App Parity

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rueegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (new document) |
| **Design spec** | [`docs/superpowers/specs/2026-07-23-sprint-25-trusted-signals-proactive-csa-parity-design.md`](../superpowers/specs/2026-07-23-sprint-25-trusted-signals-proactive-csa-parity-design.md) |
| **Parent** | Sprint 21 (#247) — refactor scope moves here |
| **Parallel WIP** | #276 (Curavias parity app SIT deploy) — coordinate, do not fork |
| **Workflow** | Trunk-based parallel sprints — [`docs/DEV_WORKFLOW.md`](../DEV_WORKFLOW.md) v1.0.0 + ADR-0038 |
| **Tracker issue** | *to be filed from Appendix A* (backfill number here) |

> **Multi-sprint parallel-work note.** Per `docs/DEV_WORKFLOW.md`: `main` is the
> trunk; this sprint runs on its own worktree `sprint-25/<topic>` created off
> `main` (never stacked on another sprint's branch). Spec + this doc + plan land
> on `main` before execution. One issue -> one branch -> one squash PR; CI is the
> merge gate; a human merges. Other workers see this sprint through the tracker
> issue (Appendix A) and the `sprint-25` label.

---

## 1. Goal

Refactor Sprint 21 Trusted External Signals into a **plugin-based signal
platform** feeding a **probability-and-impact risk-exposure engine** that
**proactively (advisory)** drives the CSA to pre-seed and simulate crisis
scenarios before risk materialises, learns via a **closed capture loop** on the
Fabric IQ ontology, and surfaces per-channel **live-vs-simulated badges** in the
Curavias app — with no fabricated data or insights at the app layer.

## 2. Source baseline

* Design spec (above) — the merged architecture, contracts, requirements,
  decomposition, and evidence.
* Sprint 21 (#247) external-signals design v1.1.0 — the base being refactored.
* Curavias app parity design v1.0.1 — the app seams this sprint consumes.
* AMA review `docs/reviews/2026-07-17-ama-trusted-external-signals-review.md` —
  the real-vs-simulated source evidence.
* Refactor epic `docs/superpowers/ideas/sprint 21 refactor epic.md` — the 8
  requested points.

## 3. Scope

| # | Milestone / task | Lane | Depends on |
|---|-----------------|------|-----------|
| M0 | Branch reconciliation + contract freeze (`SignalProvider`, `signal-providers.yaml`, `DC-RISK-EXPOSURE-v1`, ontology deltas, app badge/board contract); pick canonical parity base; reconcile stranded `sprint-21/m3-medallion` | Platform control | — |
| W1-a | Real-adapter plugins (SED, Alertswiss, MeteoSwiss-bridge) | Data | M0 |
| W1-b | Simulator plugins (BAG, BAFU, SLF, ASTRA, NABEL, Swissgrid, NCSC) | Data | M0 |
| W1-c | Internal-channel plugins (occupancy / discharge / staffing / OR / ED) | Data | M0 |
| W1-d | Medallion `providerKind` + `provenance` extension | Data | M0 |
| W2-e | Risk-exposure engine + `DC-RISK-EXPOSURE-v1` | AI | M0 |
| W2-f | Ontology extension (`SignalProvider`, `RiskExposure`, `ScenarioCandidate`, `TriggerOutcome`) | AI | M0 |
| W2-g | Semantic-model measures + trigger-precision / false-positive KPI | Data | M0 |
| W2-h | Triggering (Activator / poller) for risk breaches | Data | M0 |
| W3-i | `signal-triage-agent` proactive + scenario auto-propose | AI | W1-W2 |
| W3-j | `csa-agent` closed capture loop + Cosmos agent-memory | AI | W1-W2 |
| W3-k | App per-channel badge + CSA/OCA board wiring (coordinate #276) | Experience | W1-W2, #276 seams |
| W4-l | End-to-end synthetic walk-through + precision-KPI evidence | AI | W1-W3 |
| W4-m | Doc + issue reconciliation (PRD, ADR-0039, S21 spec, parity spec, DATA, AGENTS) | Governance | W1-W3 |

Waves 1 and 2 are fully parallel. Wave 3 needs light chain integration. Wave 4 is
closeout. Each slice is offline-testable in CI.

## 4. Key decisions

1. **Approach A** — contract-first freeze (M0), then parallel sub-agent fan-out.
2. **CSA proactive loop is fully advisory** — auto-detect + auto-run simulation;
   scenario onboarding and every mitigation stay `approved-to-apply` (HITL). No
   capacity / roster / bed / lever mutation. CSA board shape unchanged.
3. **Plugin shape** — one `SignalProvider` interface + `signal-providers.yaml`
   registry; `kind = real-adapter | simulator | internal`; **provenance derived
   from kind at ingest** and immutable through medallion + app.
4. **Closed loop = capture loop** — ontology-linked facts + Cosmos memory fed
   back as grounding; **trigger-precision / false-positive KPI; no model
   training**.
5. **Internal channels are first-class providers** (`trustTier=internal`) for a
   unified risk view.
6. **New Sprint 25 + own tracker issue**; parent #247, parallel #276 (coordinate,
   do not fork).
7. **No new MCP server** — reuses `github-mcp`, `fabric-mcp`, `cosmos-mcp`.
8. **New ADR-0039 (proposed)** records the plugin + risk-exposure +
   proactive-advisory + capture-loop decisions.

## 5. Parallel-work coordination

* **#276** — the app-layer wave-3 task rebases onto the canonical parity base
  chosen in M0 and builds on #276's frozen `RoleBoard` / badge /
  `agent-host-client` seams. If those seams are not frozen when wave 3 starts,
  task W3-k is blocked and re-sequenced after #276's freeze; signal/data waves
  proceed regardless.
* **`sprint-21/m3-m9` worktrees** — waves 1-2 extend those outputs; M0 verifies
  they are current on `main` first and un-strands `m3-medallion`.
* **Control-plane files** — CODEOWNERS-gated PRs; no allow-list change.

## 6. Definition of Done

* [ ] M0 complete: branches reconciled, canonical parity base chosen, all seams
      frozen and committed to `main`.
* [ ] Every source onboarded as a plugin; provenance derived at ingest and
      immutable end-to-end.
* [ ] Real adapters live for SED / Alertswiss / MeteoSwiss-bridge; simulators for
      the rest; internal channels emitting.
* [ ] `DC-RISK-EXPOSURE-v1` engine emits `gold.ext_fact_risk_exposure`;
      breaches raise candidate scenarios.
* [ ] Proactive advisory loop: triage auto-proposes, CSA auto-runs; onboarding +
      mitigation gated by `approved-to-apply`; no state mutation.
* [ ] Capture loop records trigger-to-outcome facts + memory; precision KPI in the
      semantic model.
* [ ] Per-channel badge live on CSA + OCA boards via live agent-host round-trips;
      no hardcoded domain data or insight strings.
* [ ] All CI gates green (markdownlint, link-check, mojibake, ontology-conformance,
      eval-goldens, external-signals, csa-checks, app Vitest + Playwright/axe).
* [ ] `FR-EXT-015..022` + NFRs in `docs/PRD.md` §7; golden-tasks carry
      `requirement:` front-matter.
* [ ] Docs bumped per SemVer; ADR-0039 merged; #247 commented; tracker issue
      linked.

---

## Appendix A — Ready-to-file sprint-tracker issue

> File via `.github/ISSUE_TEMPLATE/sprint-tracker.yml`. Backfill the resulting
> issue number into the header of this doc and the design spec once the shell /
> `gh` is available.

**Title:** `Sprint 25 — Trusted Signals to Proactive CSA and App Parity (S21 refactor)`

**Labels:** `sprint-25`, `type:epic`, `lane:data`, `lane:ai`, `lane:experience`,
`status:planning`, `deploy:sit`

**Milestone:** `Sprint 25`

**Body:**

```markdown
## Sprint goal
Refactor Sprint 21 Trusted External Signals (#247) into a plugin-based signal
platform + probability/impact risk-exposure engine + proactive-advisory CSA loop
+ closed capture loop on the Fabric IQ ontology, surfaced in the Curavias app
with per-channel live-vs-simulated badges. No fabricated data/insights.

## Design spec
docs/superpowers/specs/2026-07-23-sprint-25-trusted-signals-proactive-csa-parity-design.md

## Sprint doc
docs/sprints/sprint-25-trusted-signals-proactive-csa-and-app-parity.md

## Parent / parallel
- Parent: #247 (Sprint 21 external signals — refactor scope moved here)
- Parallel WIP: #276 (Curavias parity app SIT deploy) — coordinate, do not fork

## Branch
sprint-25/trusted-signals-proactive-csa (worktree off main; DEV_WORKFLOW v1.0.0 + ADR-0038)

## Scope (waves)
- M0: branch reconciliation + contract freeze + canonical parity base
- W1: real-adapter / simulator / internal plugins + medallion provenance
- W2: risk-exposure engine + DC-RISK-EXPOSURE-v1 + ontology + semantic KPI + triggering
- W3: triage proactive + CSA capture loop + app per-channel badge/board wiring
- W4: e2e synthetic walk-through + precision KPI + doc/issue reconciliation

## Key decisions
- Approach A (contract-first freeze, then parallel fan-out)
- CSA loop fully advisory (auto-detect + auto-run; HITL onboarding + mitigation)
- SignalProvider plugin + provenance-from-kind at ingest (immutable)
- Capture loop + precision KPI, no model training
- Internal channels as first-class providers
- No new MCP server; new ADR-0039 (proposed)

## Requirements
FR-EXT-015..022, NFR-EXT-PROV-001, NFR-EXT-ADV-001, NFR-EXT-KPI-001

## Definition of Done
See sprint doc §6.

## Gates
markdownlint, link-check, mojibake, ontology-conformance, eval-goldens,
external-signals, csa-checks, app Vitest + Playwright/axe. CI green = merge proof;
human merges.
```

**Child issues (file after the epic, one per wave slice):**

| Label | Slice |
|-------|-------|
| `sprint-25` `lane:platform` | M0 branch reconciliation + contract freeze |
| `sprint-25` `lane:data` | W1-a/b/c/d plugins + medallion provenance |
| `sprint-25` `lane:ai` | W2-e/f + W3-i/j engine + ontology + agents |
| `sprint-25` `lane:data` | W2-g/h semantic KPI + triggering |
| `sprint-25` `lane:experience` | W3-k app badge + CSA/OCA boards (coordinate #276) |
| `sprint-25` `lane:governance` | W4-l/m e2e + doc/issue reconciliation |
