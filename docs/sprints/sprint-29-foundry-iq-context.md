# Sprint 29 — Foundry IQ Context Architecture (closeout)

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-27 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Complete |
| **Previous Version** | — (initial) |
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
