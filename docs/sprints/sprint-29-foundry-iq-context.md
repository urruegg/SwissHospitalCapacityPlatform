# Sprint 29 — Foundry IQ Context Architecture (closeout)

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-29 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Complete |
| **Previous Version** | 1.0.0 (initial #399 closeout record) |
| **Design spec** | [`docs/superpowers/specs/2026-07-26-sprint-29-foundry-iq-context-architecture-design.md`](../superpowers/specs/2026-07-26-sprint-29-foundry-iq-context-architecture-design.md) |
| **ADR** | [`docs/adr/0052-app-context-envelope-per-agent-threads.md`](../adr/0052-app-context-envelope-per-agent-threads.md) |
| **Tracker issue** | [#399](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/399) (epic — closed) |
| **Follow-ups** | [#424](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/424) (live SIT lift, Approach B) · [#447](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/447) (PROD app bakes SIT agent-host URL) |

> **Scope.** Make the app's three context tiers (user × agent × grounding)
> consistent by construction: one `ContextEnvelope` per IQ read / agent turn,
> per-(user × agent) conversation threads, a role-first-eligible default board,
> and simulated-but-config-gated per-user RLS / OBO. App-side + docs +
> infra image-tag bumps only. Synthetic data, no PHI
> ([ADR-0016](../adr/0016-no-phi-in-mvp-demo-scope.md)); SIT westus2 + PROD
> switzerlandnorth.

---

## 1. Outcome

Sprint 29 is **complete**. All milestones landed on `main` and the delivered
context architecture is live (simulated + config-gated) on both SIT and PROD.

| Milestone | Deliverable | PR | State |
|-----------|-------------|----|-------|
| M0 | Sprint scaffold + design spec + ADR-0052 relocation | [#412](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/412) | ✅ merged |
| M1 | `ContextEnvelope` type + builder | [#413](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/413) | ✅ merged |
| M2 | Envelope attached to IQ reads (`iqFetch`) + envelope-less ingress guard | [#416](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/416) | ✅ merged |
| M3 | Envelope propagation + ingress guard hardening | [#418](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/418) | ✅ merged |
| M4 | Per-(user × agent) Foundry thread map | [#420](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/420) | ✅ merged |
| M5 | Simulated per-user RLS scope (`applyRlsScope`) + role-first-eligible default board | [#421](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/421) | ✅ merged |
| M6 | PRD 2.1.0 (`FR-CTX-001..004`, `NFR-CTX-001..002`) + traceability | [#423](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/423) | ✅ merged |

Requirements: `FR-CTX-001..004`, `NFR-CTX-001..002` (see
[`docs/PRD.md`](../PRD.md) §7 traceability, at 2.1.0).

## 2. Live evidence (re-verified 2026-07-27)

Read-only re-verification of both environments (Azure CLI + live Playwright
`evidence.spec.ts`):

| Check | SIT (westus2) | PROD (switzerlandnorth) |
|-------|---------------|-------------------------|
| App endpoint `GET /` | ✅ 200 | ✅ 200 |
| Deep-links `/main` `/start` `/backstage` | ✅ 200 | ✅ 200 |
| Container Apps (app + agent-host) | ✅ Running | ✅ Running |
| Agent-host `/agents` | ✅ 7 agents | ✅ 7 agents |
| Fabric F2 | ✅ Active | ✅ Active |
| Cosmos (AAD-only, public disabled) | ✅ | ✅ |
| AI model deployments | ✅ Succeeded | ✅ Succeeded |
| Evidence e2e suite (`evidence.spec.ts`) | ✅ 2/2 | ✅ 2/2 |

Deployed app image: **`hcc-app-fluent:87b2568`** on both environments.

## 3. Deep-link 404 fix (post-milestone)

Live verification surfaced an nginx **SPA deep-link 404**: all client routes
(`/main`, `/start`, `/backstage`) returned 404 on both environments while `/`
and `/index.html` returned 200.

- **Root cause.** The deployed image `5ee02a6` (2026-07-24) **predated** the
  SPA history-fallback fix (`def6fd2` / PR #410, 2026-07-26). Source
  `nginx-default.conf` (`try_files $uri $uri/ /index.html;`) and the Dockerfile
  were already correct; the fix was merged to `main` but not yet deployed.
  (`vite preview` has SPA fallback built in, which is why local runs passed.)
- **Fix.** Built `hcc-app-fluent:87b2568` from `main` via
  `ci-build-app-fluent.yml`, imported it to the PROD ACR (`az acr import`), and
  rolled both Container Apps to it. Deep-links then returned 200 and the live
  evidence suite passed 2/2 on both environments.
- **Source-of-truth.** `appFluentImage` bumped to `:87b2568` in
  [`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam)
  and
  [`infra/environments/prod-swn.bicepparam`](../../infra/environments/prod-swn.bicepparam)
  via **PR #444** so the bicepparams match the deployed reality (drift-analyzer
  stays clean).

## 4. Known flags / follow-ups

- **#447 — PROD app bakes SIT agent-host URL.** `ci-build-app-fluent.yml` builds
  one image (SIT ACR, SIT `VITE_AGENT_HOST_URL`); PROD promotion imports that
  same image, so the PROD app calls the SIT agent-host. Pre-existing (also true
  of `5ee02a6`); deliberately preserved by the scoped #444 fix. Tracked for a
  per-env build or runtime-config correction.
- **#424 — live SIT lift (Approach B).** ADR-0052 records Approach A (simulated)
  as Accepted; lifting the envelope send path, live Foundry threads, live Fabric
  RLS, and OBO to real SIT endpoints is deferred and tracked here.
  **Delivered 2026-07-29 (M1–M6) — see [§6](#6-424--live-sit-lift-approach-b-delivered-2026-07-29).**

## 5. Definition of Done

| # | Criterion | Status |
|---|-----------|--------|
| 1 | M0–M6 delivered and merged to `main` | ✅ |
| 2 | `FR-CTX-001..004` + `NFR-CTX-001..002` in PRD 2.1.0 §7 | ✅ |
| 3 | ADR-0052 recorded (Approach A Accepted; Approach B → #424) | ✅ |
| 4 | Live SIT + PROD re-verification green | ✅ |
| 5 | Evidence e2e suite 2/2 on SIT + PROD | ✅ |
| 6 | Deep-link 404 fixed + bicepparams reconciled (#444) | ✅ |
| 7 | Residual flags tracked (#424, #447) | ✅ |

---

## 6. #424 — Live SIT lift (Approach B) delivered (2026-07-29)

The follow-up tracked in §4 is now delivered. Approach B lifted the envelope
send path, live golden-source read, live per-(user × agent) Foundry threads,
Fabric RLS, and the OBO seam to real SIT endpoints — **evidence-grounded and
config-gated**, honest about what the deployed Fabric/Entra reality can enforce
today. Each rung is real code + config; live per-user enforcement that the
platform cannot yet prove is explicitly deferred, not faked.

> **#424 milestones use their own M1–M6 numbering**, distinct from the §1
> Sprint 29 (#399) M0–M6 table above.

| # | Deliverable | Merge | State |
|---|-------------|-------|-------|
| M1 | Wire `ContextEnvelope` + Foundry thread map into the app send path (no new infra) | [#464](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/464) `0c86920` | ✅ merged |
| M2 | Live golden-source read path — agent-host `GET /golden/{resource}` | `f596cf2` | ✅ merged + live SIT |
| M3 | Live per-(user × agent) thread map via staged `ThreadProvider` seam | [#495](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/495) `dadd7ce` | ✅ merged + live SIT |
| M4 | Fabric RLS — evidence-grounded capability ladder (`SimulatedRlsProvider` default + `FabricDataAgentRlsProvider` rung; multi-site `network` resource; `_rls` block + `X-Rls-*` headers) | [#512](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/512) `583f633` | ✅ merged + live SIT |
| M5 | OBO ingress seam (Entra → Fabric/Foundry) completed in code + config, gated **off** (`OBO_ENABLED=false`); go-live is a config flip per ADR-0057 | [#522](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/522) `62cc2ae` | ✅ merged |
| M6 | Provenance + docs + ADR closeout: PRD §7 #424 traceability row (2.8.0), this section, SIT + PROD parity deploy, close #424 | this PR | ✅ |

**Design + decisions.** [`ADR-0057`](../adr/0057-obo-seam-completion-defer-live-provisioning.md)
records Path B (complete the OBO seam; defer live provisioning). Real per-user
Fabric RLS additionally needs the dynamic-RLS TMDL predicate + deployable persona
source ([#510](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/510)) —
both are the deferred ADR-0057 Path A follow-up. M4/M5 design specs:
[M4 RLS provider](../superpowers/specs/2026-07-28-sprint-29-m4-rls-provider-design.md),
[M5 OBO seam](../superpowers/specs/2026-07-28-sprint-29-m5-obo-seam-design.md).

**SIT + PROD parity (M6).** Both environments were lifted to the M5 agent-host
image **`hcc-agent-host:62cc2ae`** (SIT was at M4 `583f633`, PROD lagged at M2
`f596cf2`). All new capabilities default off/simulated, so the deploy is
behaviour-parity — no live per-user enforcement is switched on. `agentHostImage`
bumped to `:62cc2ae` in
[`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam)
and
[`infra/environments/prod-swn.bicepparam`](../../infra/environments/prod-swn.bicepparam)
so the bicepparams match the deployed reality (drift-analyzer stays clean).

**Residual (deferred, not blocking #424).** ADR-0057 Path A (live Entra OBO
provisioning + #510 dynamic-RLS TMDL) · #510 · #477 (stale PROD Fabric coords) ·
issue #447 (PROD app bakes SIT agent-host URL). All synthetic / no-PHI, westus2
SIT + switzerlandnorth PROD demo scope.
