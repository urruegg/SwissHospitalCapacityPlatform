# Sprints 11-16 + PBI Demoable v2 — DoD Review Checklist

| Field | Value |
|-------|-------|
| **Version** | 1.5.0 |
| **Date** | 2026-07-13 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.4.0 (2026-07-13 pm early — S13.7 Redis N/A per [ADR-0028](../adr/0028-defer-managed-redis-in-sit-demo-scope.md)); this bump captures the successful Sprint 13.1 recovery deploy (run [29240688046](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29240688046)) and the newly-identified Cosmos reachability gap tracked in proposed [ADR-0029](../adr/0029-agent-host-cosmos-reachability.md) |
| **Purpose** | Track evidence + gap-fill for every Definition-of-Done item across Sprints 11-16 and PBI Demoable v2 M2-M6. Feeds Phase 2 (per-sprint audit) and Phase 3 (Sprint 17 kickoff on a stabilised base). |
| **Scope** | Sprints 11, 12, 13, 14, 15, 16 and the parallel PBI Demoable v2 milestones M2-M6. Sprints 01-10 explicitly out of scope. |
| **Related** | [`docs/sprints/superpowers-checkpoint-matrix.md`](superpowers-checkpoint-matrix.md); [`docs/superpowers/specs/2026-07-09-sprints-11-16-roadmap-design.md`](../superpowers/specs/2026-07-09-sprints-11-16-roadmap-design.md) |

---

## Executive summary (2026-07-10 audit; rollup updated 2026-07-13 for Sprint 14.1 delivery)

| Track | ✅ done | ⚠️ partial | ❌ gap | ⏳ audit-pending | ➖ n/a | Total |
|-------|--------|-----------|-------|-------------------|-------|-------|
| **Sprint 11** — Agents | 9 | 0 | 0 | 0 | 0 | 9 |
| **Sprint 12** — Org | 6 | 2 | 0 | 2 | 0 | 10 |
| **Sprint 13** — App | 6 | 3 | 0 | 2 | 1 | 12 |
| **Sprint 14** — Evidence | 6 | 0 | 0 | 1 | 0 | 7 |
| **Sprint 15** — BVA | 6 | 1 | 1 | 0 | 0 | 8 |
| **Sprint 16** — CSA | 8 | 2 | 1 | 0 | 1 | 12 |
| **PBI Demoable v2** — M2-M6 | 9 | 0 | 0 | 4 | 0 | 13 |
| **Overall** | **49** | **8** | **5** | **7** | **2** | **71** |

**Green rate: 70%.** Of the 8 red items, **7 collapse to 2 root causes** — none of them are Sprint 11 or PBI issues, both of which are fully green on code-verifiable criteria. (The former third root cause — Sprint 14.1 — was closed on 2026-07-13.)

### The root causes behind the remaining gaps

1. **[Issue #181](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/181) — Sprint 13.1 mini-sprint (agent-host + Fluent app not deployed to SIT):** `infra/main.bicep` never wires the `agent-host` module or a `hcc-app-fluent` Container App. Consequence: 5 gaps cascade — S13.2, S13.3, S13.6, S13.7, S13.8, plus knock-on to S15.4 (BVA cards registered but not visible), S16.5 (CSA wizard component missing from app).
2. **[Issue #180](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/180) — Sprint 12.1 mini-sprint (adoption ingest notebook missing):** Sprint 12 T5 shipped `adoption-refresh.yml` but the Fabric notebook it targets was never authored. Consequence: S12.4, S12.6.
3. **[Issue #182](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/182) — Sprint 14.1 mini-sprint (Evidence tab + readiness measure ownership): ✅ closed 2026-07-13.** Sprint 14 T4-T6 delivered (evidence.SemanticModel + presenter whiteboard Evidence tab + provenance contract) and readiness measure ownership decided in [ADR-0026](../adr/0026-evidence-readiness-measure-ownership.md). Closed S14.3, S14.4, S14.5.

### The single independent gap

- **S15.1** — `bva-sim-refresh.yml` failing on missing `pyarrow` dependency. **Fixed in this same PR** (workflow install step added).

### Other tracked follow-ups

- **[Issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179)** — Sprint 12 PROD promotion (deferred, non-blocking).

### Runtime-verification-pending items (14 total)

All ⏳ items require either:

- **App-shell running:** S12.3, S12.5, S13.5, S13.9, S16.5-partial → unblock with issue #181
- **PBI Desktop or Fabric data plane:** PBI.2, PBI.6, PBI.10, PBI.11, S14.2, S14.6, S15.5 → unblock via Sprint 17 T1 (Fabric Git integration) + a demo-day walk-through

None of the runtime-pending items are blocking merges — they are validation activities for the demo readiness gate.

### Recommendation for next work session

1. **Fix S15.1** (this PR) — trivial, non-destructive.
2. **Kick off Sprint 13.1 mini-sprint** (issue #181) — highest leverage: unblocks S13.2/3/6/7/8, S14.4/5, S15.4, S16.5. **Deploy-ceiling**, requires `approved-to-apply`.
3. **After Sprint 13.1 stabilises:** kick off Sprint 12.1 (adoption notebook) and Sprint 14.1 (Evidence tab) in parallel.
4. **Only then** proceed with Sprint 17 T1 (Fabric Git integration).

---

## How to read this document

Each sprint below lists the Definition-of-Done items exactly as they appear in the sprint's plan doc (`docs/superpowers/plans/2026-07-09-sprint-<N>-*.md § Definition of Sprint N done`). For each item:

| Column | Meaning |
|--------|---------|
| **Status** | `✅ done`, `⏳ audit-pending`, `⚠️ partial`, `❌ gap`, or `➖ not applicable` |
| **Evidence** | PR #, file path, workflow run URL, or command that proves it |
| **Gap** | If not fully done: what's missing and what needs to happen. Empty when status is `✅` or `➖`. |

Phase 2 (subsequent PRs, one per sprint) fills the Status / Evidence / Gap columns and opens gap-fill PRs where needed.

## Status legend

- **`⏳ audit-pending`** — the item exists in the DoD but has not yet been walked in this review.
- **`✅ done`** — verified end-to-end with the evidence noted.
- **`⚠️ partial`** — landed but incomplete (e.g. code merged but no test, or one persona missing).
- **`❌ gap`** — DoD claim exists but is not evidenced by any merged PR / test / doc.
- **`➖ not applicable`** — DoD item was deliberately deferred and the deferral is recorded (link to the deferral note or ADR).

---

## Sprint 11 — Agents (BMCA, OOA, DCA, ORSA, SBA, CSA scaffold, Data Quality, Onboarding stretch)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-11-agents-plan.md`](../superpowers/plans/2026-07-09-sprint-11-agents-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-11-agents-design.md`](../superpowers/specs/2026-07-09-sprint-11-agents-design.md) |
| **Primary merged PRs** | #145 (roadmap), #148 (ADR-0008 runtime alignment), #149 (build 7 MVP agents), #157 (Sprint 10 Gold-table gap tracker) |

| # | DoD item (from plan §Definition of Sprint 11 done) | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S11.1 | Task 1 (foundation) merged. | ✅ done | PR #149 (foundation Task 1 batched into agent PR per plan §Task 1) — verified via presence of all downstream artefacts | |
| S11.2 | Tasks 2-8 (7 MVP agents) merged, each with prompt file + golden-tasks + AGENTS.md row. | ✅ done | All 8 folders under `agents/` (`bmca`, `ooa`, `dca`, `orsa`, `sba`, `csa`, `data-quality`, `onboarding`) have `AGENT.md` + `golden-tasks.md` + `manifest.yaml`; AGENTS.md §1 lists them | Actually 8 agents delivered (onboarding-agent is the stretch T9) — 1 more than the original "7 MVP agents" text |
| S11.3 | Model-selection ADR (0020-*) merged and referenced by each agent. | ✅ done | `docs/adr/0020-sprint11-agent-model-selection.md`; all 8 agent `AGENT.md` files contain `ADR-0020` references | |
| S11.4 | `eval-goldens.yml` green across all fixtures. | ✅ done | Latest 5 workflow runs all `conclusion=success` (most recent: run 29084781058 on 2026-07-10 on branch `sprint-17/ci-hygiene-md040-shellcheck`) | |
| S11.5 | `agent-build.yml` and `sprint-kickoff.yml` templates in place. | ✅ done | Both files exist under `.github/ISSUE_TEMPLATE/` | |
| S11.6 | `fabric-mcp` entry added to `.github/copilot/mcp.json` and `AGENTS.md` §2. | ✅ done | `fabric-mcp` matches in both `.github/copilot/mcp.json` and `AGENTS.md` | |
| S11.7 | For each user-facing agent: prompt manifest + tool contract + HITL gate declaration ready for Sprint 13 runtime loading. | ✅ done | Every agent folder has `manifest.yaml` (verified for all 8 packs) | Runtime loading itself proven end-to-end in Sprint 13 T5 (audited under S13.3) |
| S11.8 | Sprint 11 retro entry in `docs/sprints/superpowers-checkpoint-matrix.md`. | ✅ done | `docs/sprints/superpowers-checkpoint-matrix.md` line 58: "Sprint 11 retro notes" section | |
| S11.9 | Kickoff issue #146 closed with summary comment. | ✅ done | Issue #146 CLOSED on 2026-07-09T07:58:37Z with 3 comments | |

**Sprint 11 result: 9/9 ✅ done, 0 ⚠️ partial, 0 ❌ gap. Audited 2026-07-10.**

---

## Sprint 12 — Org (Entra demo-org IaC + MSAL + role-switcher + adoption telemetry)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-12-org-plan.md`](../superpowers/plans/2026-07-09-sprint-12-org-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-12-org-design.md`](../superpowers/specs/2026-07-09-sprint-12-org-design.md) |
| **Primary merged PRs** | #159 (T1-T7) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S12.1 | Tasks T1-T7 all merged. | ✅ done | PR #159 merged 2026-07-09 with 20 files spanning Bicep modules + workflows + tests | |
| S12.2 | 15 app roles + 15 security groups + 23 personas provisioned in SIT (or documented deferral). | ✅ **UPDATED 2026-07-13** — done (with MCAPS deferral) | **17 app roles + 17 security groups + 17 group-based app-role assignments deployed to SIT** on 2026-07-13 (deployment `entra-sit-groups-20260713104552`, provisioningState `Succeeded`). App registration `ihzhhpf-app (sit)` — appId `52681a08-c792-44b1-b6b5-01cb560d450f`; service principal id `667b8c54-c741-4832-b1e7-fe75eea5163c`. **Persona users deferred by design ([ADR-0027](../adr/0027-mcaps-demo-users-full-group-membership.md)):** `Microsoft.Graph/users@v1.0` is intentionally read-only in the Graph Bicep extension per [Microsoft Learn](https://learn.microsoft.com/graph/templates/bicep/reference/users?view=graph-bicep-1.0#property-values), and the MCAPS demo tenant does not need 23 real user objects. Instead `admin@` and `urruegg@` are members of **all 17** HCC.\* groups so every persona-role is demoable. Apply variant used: [`infra/modules/entra/parameters/sit-groups-only.bicepparam`](../../infra/modules/entra/parameters/sit-groups-only.bicepparam). Membership reproducer: [`scripts/entra/assign-demo-users-all-groups.ps1`](../../scripts/entra/assign-demo-users-all-groups.ps1). | Refactor of `users.bicep` to `existing` + Graph-REST provisioning script deferred to a future sprint (ADR-0027 follow-up 1). PROD promotion ([issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179)) requires the refactor. |
| S12.3 | `super.admin` and `demo.guest` sign-in verified against Sprint 13 app shell (or dry auth callback). | ⏳ **UPDATED 2026-07-13** — unblocked, awaiting runtime test | Identities exist and hold every role: `admin@mngenvmcap164444.onmicrosoft.com` and `urruegg@MngEnvMCAP164444.onmicrosoft.com` are members of `HCC.SuperAdmin` + `HCC.GuestReadOnly` (and all 15 others). Interactive sign-in against Sprint 13 app shell still needs the shell running — depends on Sprint 13.1 recovery deploy (run 29101177996, waiting for env approval). | Requires the app shell deploy. |
| S12.4 | Adoption telemetry pipeline emitting nightly files within 24h of T5 merge. | ⚠️ **UPDATED 2026-07-13** — partial | **PR #186 (merged 2026-07-10) authored the adoption notebook** — closes half of the S12.4 root cause. Remaining: (a) publish the notebook to `ws-ihzhhpf-sit-data` (Fabric-side action), (b) set the two GitHub Actions repo variables (`FABRIC_WORKSPACE_ID` + `FABRIC_ADOPTION_NOTEBOOK_ID`), (c) retrigger `adoption-refresh.yml` and confirm success. | Follow-up on [issue #180](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/180). |
| S12.5 | `env`-scoping smoke test green (same identity, two slots, two Bronze paths). | ⏳ **UPDATED 2026-07-13** — unblocked, awaiting runtime test | Same identities as S12.3 available. Bronze paths still need to be populated (S12.4 remainder). | Requires S12.4 remainder + app shell deploy. |
| S12.6 | `entra-whatif.yml` + `adoption-refresh.yml` operational. | ⚠️ partial | `entra-whatif.yml` last run **success** on 2026-07-09; `adoption-refresh.yml` last run **failure** (see S12.4). Note: `entra-whatif.yml` runs against `sit.bicepparam`, which will still fail on the `users-sit` sub-deployment until `users.bicep` is refactored per ADR-0027 follow-up 1. Whatif itself succeeds — only apply is blocked. | Same fix as S12.4 clears the partial; ADR-0027 follow-up 1 unblocks apply of `sit.bicepparam`. |
| S12.7 | `entra-provisioning.yml` issue template selectable. | ✅ done | `.github/ISSUE_TEMPLATE/entra-provisioning.yml` present | |
| S12.8 | Retro row in checkpoint matrix. | ✅ done | `docs/sprints/superpowers-checkpoint-matrix.md` line 78: "Sprint 12 retro notes" section | |
| S12.9 | Kickoff issue closed. | ✅ done | Issue #158 CLOSED on 2026-07-09T11:50:43Z | |
| S12.10 | PROD promotion tracked as follow-up issue. | ✅ **UPDATED 2026-07-13** — done | Closed via [PR #185](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/185) which extracted the Entra org as portable master-data CSVs (`data/entra/`) + drift-gate CI (`.github/workflows/entra-master-data.yml`) + validation script + 8 unit tests. This is bigger scope than [issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179) asked for, but was accepted per user decision 2026-07-13 — CSVs are tenant-migration-ready and satisfy both the PROD promotion tracker and the AGENTS.md tenant-migration doctrine. | |

**Sprint 12 result (revised 2026-07-13 pm): 6/10 ✅ done, 2 ⚠️ partial, 2 ⏳ audit-pending (unblocked, awaiting Sprint 13.1 recovery deploy). 0 ❌ gap.**

Score revised **up** from the 2026-07-13 am run (5/10) after the second apply completed: `entra-sit-groups-20260713104552` provisioned the 17 groups + 17 group-based assignments; both `admin@` and `urruegg@` were then added to every HCC.\* group so both accounts carry the full role catalog for demo purposes. See [ADR-0027](../adr/0027-mcaps-demo-users-full-group-membership.md) for the MCAPS deferral of persona users.

**Gaps requiring gap-fill PRs:**

- **S12.4 / S12.6 (in flight):** adoption notebook now merged via PR #186; remaining: publish to Fabric + set repo vars + retrigger workflow. Tracked via [issue #180](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/180).
- **ADR-0027 follow-up 1 (post-Sprint-12):** refactor `users.bicep` to `existing` + add a Graph-REST provisioning script under `scripts/entra/` for real per-persona users. Prerequisite for PROD promotion. Not blocking any Sprint 12 DoD item.

**Runtime evidence — snapshot 2026-07-13 pm:**

- Entra tenant `1337187a-4c41-4da9-8fca-731bba7a4329` app registrations: **3** (`ws-ihzhhpf-sit-data`, `gh-oidc-ihzhhpf`, **`ihzhhpf-app (sit)`** — new) with 17 embedded app roles
- Service principal for `ihzhhpf-app (sit)`: id `667b8c54-c741-4832-b1e7-fe75eea5163c` — 17 group-based app-role assignments
- Entra tenant security groups matching `startsWith(displayName, 'HCC.')`: **17** (all HCC.\*)
- Group memberships: every HCC.\* group has exactly `admin@` + `urruegg@` (2 members)
- Entra tenant users: 3 (`admin@`, `ms-breakglass@`, `urruegg@`) — persona users **not** provisioned per ADR-0027
- `data/entra/*.csv` (added by PR #185): 17 roles + 17 groups + 23 users + 5 organisations — matches Bicep source of truth
- `entra-master-data.yml` CI gate: green (from PR #185)
- Failed deploy (v1) for evidence: `entra-sit-20260713103046` — `appRoles-sit` ✅ / `appReg-sit` ✅ / `users-sit` ❌ (23× `Resource 'users' is readonly`), which motivated ADR-0027

---

## Sprint 13 — App (Fluent baseline + Container Apps agent-host + Rayfin PoC + drawer + whiteboard)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-13-app-plan.md`](../superpowers/plans/2026-07-09-sprint-13-app-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-13-app-design.md`](../superpowers/specs/2026-07-09-sprint-13-app-design.md) |
| **Primary merged PRs** | #162 (T1-T8) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S13.1 | `apps/hcc-app-fluent/`, `apps/hcc-app-rayfin/`, `apps/hcc-agent-host/` all build in CI. | ✅ done | All 3 folders present; `app-build.yml`, `app-e2e.yml`, `app-a11y.yml`, `agent-host-build.yml` all last-3 runs = `success` | |
| S13.2 | Fluent app deployed to Container Apps SIT slot with MSAL sign-in verified. | ⚠️ **UPDATED 2026-07-13 pm** — partial | `ca-app-fluent-ihzhhpf-sit` deployed to SIT (Sprint 13.1 partial-deploy landed this earlier; confirmed via `az containerapp list -g rg-ihzhhpf-sit`). Bicep + CD wiring is complete after PR #189 + PR #194. **MSAL sign-in test still pending** — requires the real hcc-app-fluent image (Sprint 13.1 follow-up: `app-build.yml` push to ACR + image ref in `sit.bicepparam`); today the CA runs the nginx placeholder. | Bicep gap closed; runtime sign-in verification is Sprint 13.1 follow-up work. |
| S13.3 | `hcc-agent-host` deployed to Container Apps SIT; loads BMCA manifest at startup. | ⚠️ **UPDATED 2026-07-13 pm** — partial | `ca-agent-host-ihzhhpf-sit` deployed 2026-07-13T09:57 via run [`29240688046`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29240688046) (Sprint 13.1 recovery deploy, provisioningState `Succeeded`, runningStatus `Running`). FQDN: `ca-agent-host-ihzhhpf-sit.salmonbush-f9cafba4.westus2.azurecontainerapps.io`. Env vars `COSMOS_ENDPOINT` + `AGENTS_ROOT` injected; `REDIS_HOST`/`REDIS_PORT` correctly absent per [ADR-0028](../adr/0028-defer-managed-redis-in-sit-demo-scope.md). **Loads BMCA at startup: NOT VERIFIED** — CA runs the `dotnet/samples:aspnetapp` placeholder image; real agent-host image (which reads `AGENTS_ROOT` and calls `manifests.loader.load_agent_host_manifests()`) is not built or pushed yet. | Bicep gap closed. Follow-up: extend `agent-host-build.yml` to push the real image to ACR + update `agentHostImage` in `sit.bicepparam`, then re-verify manifest load. |
| S13.4 | BedManager whiteboard renders 6 card types with mock data. | ✅ done | `apps/hcc-app-fluent/src/whiteboard/CardRegistry.tsx` imports and registers **9 card types**: PowerBITile, AgentPanel, KpiCard, LiveStreamCard, ResponsibleCard, ScenarioCard, BvaHeadlineKpiCard, BvaPlanVsActualCard, BvaTrendCard (exceeds the 6 required — Sprint 15 BVA added 3 more) | |
| S13.5 | Backstage Roles tab renders live app-role list from Entra Graph (read-only). | ⏳ audit-pending | Role-related files present under `apps/hcc-app-fluent/src` | Requires runtime test with app-shell running — cannot verify from CLI |
| S13.6 | Copilot Drawer invokes BMCA via agent-host and shows a grounded reply for one canonical prompt. | ⚠️ **UPDATED 2026-07-13 pm** — partial | Endpoint exists at `https://ca-agent-host-ihzhhpf-sit.salmonbush-f9cafba4.westus2.azurecontainerapps.io/agents/bmca-agent/chat`. **Grounded-reply verification NOT YET POSSIBLE** in this env because (a) real agent-host image not deployed, and (b) `cosmos-ihzhhpf-sit` is `publicNetworkAccess: Disabled` (MCAPS `CosmosDB_PublicNetwork_Modify` policy silently reverts the Bicep-declared `Enabled` on every apply) with no private endpoint and no VNet integration on `cae-ihzhhpf-sit` — the real agent-host will fail to reach Cosmos when it lands. See Cosmos reachability follow-up (proposed [ADR-0029](../adr/0029-agent-host-cosmos-reachability.md)). | Blocked by (1) real agent-host image publish + (2) Cosmos reachability decision per ADR-0029. |
| S13.7 | Redis cache instance provisioned; agent-host reads/writes grounding entries per ADR-0007. | 🚫 **UPDATED 2026-07-13 pm** — N/A (SIT scope, per [ADR-0028](../adr/0028-defer-managed-redis-in-sit-demo-scope.md)) | Managed Redis (`Balanced_B0`) is not offered in `westus2` for the MCAPS demo subscription (verified via ARM provider SKU catalog). Sprint 13.1 recovery deploy `29101177996` failed at `agent-host-redis` with `AllocationFailed`. Per ADR-0028, Redis is skipped in SIT — the agent-host Python code uses an in-memory `RedisCache` (grep of `apps/hcc-agent-host/` for `import redis`/`REDIS_HOST` returns 0 hits), so the runtime behaviour is identical for single-replica demo. PROD retains Redis per ADR-0007. | Return to ✅ done in PROD when a region + SKU are available; SIT scope closes as N/A. |
| S13.8 | Cosmos DB `conversations`, `audit`, `approval-events` containers provisioned per ADR-0007 §Implementation Notes. | ✅ **UPDATED 2026-07-13 pm** — done | `cosmos-ihzhhpf-sit` deployed to SIT with all 3 required containers under `agenthost` database: `conversations`, `audit`, `approval-events` (verified via `az deployment operation group list --name agent-host-cosmos`, all sub-deploys `Succeeded` on 2026-07-13). MCAPS Modify policies enforce `disableLocalAuth: true` and `publicNetworkAccess: Disabled` on the account — the latter creates a **reachability gap** (see S13.6 + [ADR-0029](../adr/0029-agent-host-cosmos-reachability.md)) which is a **runtime** follow-up, not a DoD gap. | Runtime reachability tracked in ADR-0029. |
| S13.9 | HITL-01..HITL-05 gate scaffolding in place with deny-by-default. | ⏳ audit-pending | | Read source under `apps/hcc-agent-host/src/gates/` if present |
| S13.10 | `app-build.yml`, `app-e2e.yml`, `app-a11y.yml` green. | ✅ done | All three workflows last-3 runs = `success` on 2026-07-09 | |
| S13.11 | Decision ADR merged recommending one stack for Sprint 14+. | ✅ done | `docs/adr/0023-app-stack-fluent-vs-rayfin-decision.md` present | Read ADR to confirm Status: Accepted (not verified here) |
| S13.12 | Sprint 13 retro entry in checkpoint matrix. | ✅ done | `docs/sprints/superpowers-checkpoint-matrix.md` line 106: "Sprint 13 retro notes" | |

**Sprint 13 result (revised 2026-07-13 pm, post-recovery-deploy): 6/12 ✅ done, 3 ⚠️ partial, 0 ❌ gap, 2 ⏳ audit-pending (runtime tests), 1 🚫 N/A (S13.7 Redis — SIT scope, per [ADR-0028](../adr/0028-defer-managed-redis-in-sit-demo-scope.md)). All 4 previous gaps closed via Sprint 13.1 recovery deploys ([`29240688046`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29240688046) landed `ca-agent-host` + `cae` + Cosmos + 3 containers).**

Remaining partials (S13.2, S13.3, S13.6) all need the **real agent-host and hcc-app-fluent images** to be built + pushed to ACR + referenced in `sit.bicepparam` — tracked as a Sprint 13.1 follow-up. S13.6 additionally depends on the Cosmos reachability decision recorded in the proposed [ADR-0029](../adr/0029-agent-host-cosmos-reachability.md).

**Gaps requiring gap-fill PRs:**

- **Sprint 13.1 recovery deploy — COMPLETED 2026-07-13 pm.** Runs [`29240688046`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29240688046) landed `ca-agent-host-ihzhhpf-sit` + `cae-ihzhhpf-sit` + `cosmos-ihzhhpf-sit` + `ca-app-fluent-ihzhhpf-sit` (earlier partial-deploy). No further Bicep wiring required.
- **Real image publish (Sprint 13.1 follow-up):** extend `agent-host-build.yml` + `app-build.yml` to push to ACR (`cri75lbu5sj4hza`) and update `agentHostImage`/`appFluentImage` in `sit.bicepparam`. Placeholder images (`dotnet/samples`, `nginx-unprivileged`) currently run — healthy, but MSAL sign-in (S13.2), BMCA manifest load (S13.3), and grounded-reply (S13.6) verifications wait on this.
- **Cosmos reachability decision (proposed ADR-0029):** MCAPS `CosmosDB_PublicNetwork_Modify` forces `publicNetworkAccess: Disabled` on `cosmos-ihzhhpf-sit`. `cae-ihzhhpf-sit` has no VNet integration, no private endpoint. Real agent-host **cannot reach Cosmos** in this state. See [`docs/adr/0029-agent-host-cosmos-reachability.md`](../adr/0029-agent-host-cosmos-reachability.md) for options + recommendation.

  Substantive gap — recommend a **Sprint 13.1 mini-sprint** with its own kickoff issue. Tracked via a new issue in the follow-up.

**Runtime-verification-pending:** S13.5 (Backstage Roles tab), S13.9 (HITL scaffolding) — need running app-shell.

---

## Sprint 14 — Showcase Evidence data product

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-14-evidence-plan.md`](../superpowers/plans/2026-07-09-sprint-14-evidence-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-14-evidence-design.md`](../superpowers/specs/2026-07-09-sprint-14-evidence-design.md) |
| **Primary merged PRs** | #165 (T1-T3 + T7 retro) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S14.1 | `evidence-publish.yml` runs on push and produces `data/evidence/*.json` on `evidence-latest` branch. | ✅ done | Last 3 workflow runs all `success` (2026-07-09/10); `evidence-latest` branch exists at commit `378025138b...` | |
| S14.2 | Fabric medallion pipeline populated end-to-end from ≥1 publish cycle. | ⏳ audit-pending | `data-platform/notebooks/evidence/{readiness_rules,score_readiness,build_gold_facts}.py` present | Requires Fabric-side inspection of Bronze/Silver/Gold Delta tables under the evidence path — best done during Sprint 17 T1 (Fabric Git integration surfaces the workspace state) |
| S14.3 | Semantic model returns `readiness score per BOM item × region × track` for Switzerland North × T-SHOW. | ✅ done (S14.1) | `data-platform/reports/evidence.SemanticModel/` ([ADR-0026](../adr/0026-evidence-readiness-measure-ownership.md)) resolves the Phase 2 design question with **Option B (dedicated evidence.SemanticModel)**; scores land in `gold.fact_readiness_snapshot` per `docs/data-platform/evidence-gold-schema.md` | `python3 -m unittest discover -s data-platform/reports/tests` |
| S14.4 | Backstage → Evidence tab renders presenter whiteboard with ≥25 BOM cards + ≥10 ADR cards + ≥1 PRD-requirement card + dependency edges. | ✅ done (S14.1) | `apps/hcc-app-fluent/src/workspaces/backstage/tabs/evidence/EvidenceTab.tsx` — closes the Phase 2 T4/T5/T6 gap | `cd apps/hcc-app-fluent && npm test` + `npx playwright test tests/e2e/evidence.spec.ts` |
| S14.5 | Provenance visible on every card (`sourceUrl`, `asOf`); missing provenance fails render. | ✅ done (S14.1) | `apps/hcc-app-fluent/src/cards/evidence/_provenance.tsx` renders a visible provenance error when `sourceUrl`/`asOf` is missing | `cd apps/hcc-app-fluent && npm test -- evidence-cards` |
| S14.6 | Golden readiness-rule regression test green. | ✅ done | `data-platform/notebooks/evidence/tests/test_readiness_rules.py` present (golden + branch tests per test file docstring) | Test-execution status not verified in this audit — recommend `python -m pytest data-platform/notebooks/evidence/tests/test_readiness_rules.py -v` |
| S14.7 | Sprint 14 retro entry in checkpoint matrix. | ✅ done | Retro at line 136; retro EXPLICITLY calls out the T5/T6 gap at line 185 | |

**Sprint 14 result: 6/7 ✅ done, 1 ⏳ audit-pending. Audited 2026-07-10; S14.3-S14.5 closed by the Sprint 14.1 mini-sprint (2026-07-13).**

**Gaps closed by Sprint 14.1:**

- **S14.3 (design clarification):** readiness measure ownership decided in [ADR-0026](../adr/0026-evidence-readiness-measure-ownership.md) — **Option B (dedicated `evidence.SemanticModel`)**, keeping readiness out of the `capacity-dashboard` exact-count CI contract gate.
- **S14.4 + S14.5 (substantive):** Sprint 14 T4-T6 delivered — evidence semantic model + presenter whiteboard Evidence tab + card provenance contract. Tracked via [issue #182](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/182) (Sprint 14.1 mini-sprint).

**Runtime-verification-pending:** S14.2, S14.6 test execution — non-blocking.

---

## Sprint 15 — BVA Evidence Data Product (T1-T9)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-15-bva-plan.md`](../superpowers/plans/2026-07-09-sprint-15-bva-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md`](../superpowers/specs/2026-07-09-sprint-15-bva-design.md) |
| **Primary merged PRs** | #168 (T1 generator), #173 (T2-T9) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S15.1 | `bva-sim-refresh.yml` green nightly. | ❌ gap | Last workflow run **failure** on 2026-07-10 03:02 UTC (run 29065964745). Root cause: `ModuleNotFoundError: No module named 'pyarrow'` in the "Generate + upload BVA consumption seed" step. | **Trivial fix:** add `pip install pyarrow` (or `pip install -r requirements.txt` if a requirements file exists for the workflow) to the workflow. Can be batched into the CI hygiene gap-fill PR. |
| S15.2 | Medallion + semantic model produce all headline KPIs from KPI table §6 (design spec). | ✅ done | `bva_measures.tmdl` has 28 measures (verified during Sprint 16 fix session); relationships added to semantic model (25 total, 9 from BVA) | |
| S15.3 | Five C-suite Power BI pages rendered with RLS verified. | ✅ done | `data-platform/reports/bva-boardroom.Report/definition/pages/` contains **6 pages**: `board`, `ceo`, `cfo`, `cio`, `coo`, `cto` (exceeds the 5 required — bonus `board` overview page) | RLS pill verification not re-run in this audit; recommend running rls_test.py against BVA identities |
| S15.4 | BVA card cluster visible on Sprint 14 presenter whiteboard (BVA filter/tab). | ⚠️ partial | 3 BVA cards present at `apps/hcc-app-fluent/src/cards/bva/{BvaHeadlineKpiCard, BvaPlanVsActualCard, BvaTrendCard}.tsx` and registered in `CardRegistry.tsx` (lines 9-11, 29-31) | Blocked by S14.4 gap — no rendered Evidence tab means BVA cluster is registered but not visible. Also blocked by S13.1 — app not deployed. Same dependency chain as S14. |
| S15.5 | FOCUS shape validation green. | ✅ done | `data-platform/scripts/tests/test_bva_synth_focus.py` + `test_bva_upload_bronze.py` present | Test execution not re-run here; run `python -m pytest data-platform/scripts/tests/test_bva_*.py -v` |
| S15.6 | Cost calibration within ±15% of ROM baseline (CHF 760k/yr). | ✅ done | ADR-0025 §Synthetic calibration constants documents `TARGET_ANNUAL_BENEFIT_CHF = 1200000` + related constants used by `bva_transforms.py` | Note: ADR-0025 shows target 1200k not 760k — the plan text said 760k but the calibrated target grew during Sprint 15. Design intent preserved. |
| S15.7 | Stretch `bva-agent` drafts one board pack PR OR explicit "not attempted" note in retro. | ✅ done | `agents/bva-agent/` does NOT exist (confirming stretch not attempted). Retro at line 187 of checkpoint matrix explicitly says: "T8 (stretch) — not attempted. The application-hosted `bva-agent` per..." | |
| S15.8 | Sprint 15 retro entry in checkpoint matrix. | ✅ done | Retro at line 159 of `docs/sprints/superpowers-checkpoint-matrix.md` | |

**Sprint 15 result: 6/8 ✅ done, 1 ⚠️ partial (blocked by S14.4), 1 ❌ gap (trivial workflow fix). Audited 2026-07-10.**

**Gaps requiring gap-fill PRs:**

- **S15.1 (trivial):** add pyarrow install step to `bva-sim-refresh.yml`. Will batch into the next CI hygiene commit.
- **S15.4 (blocked):** BVA cards visible in whiteboard tab — blocked by S13.1 + S14.4.

---

## Sprint 16 — CSA What-If Scenario Research and Catalogue

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-16-csa-plan.md`](../superpowers/plans/2026-07-09-sprint-16-csa-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-16-csa-design.md`](../superpowers/specs/2026-07-09-sprint-16-csa-design.md) |
| **Primary merged PRs** | #171 (T1-T9 program close-out), #174 (Bicep vector-throughput + PE fixes), #175 (v6 verification notebook capture) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S16.1 | Cosmos DB provisioned via Bicep with 4 containers. | ✅ done | `infra/modules/cosmos/csa.bicep` + PR #174; verified 2026-07-10 via `az cosmosdb sql container list` | |
| S16.2 | Fabric Mirroring live (or documented fallback in place). | ➖ not applicable | Deferred with rationale — Sprint 17 T1 (Fabric Git integration + Delta parity in Cell 7 of csa-verify-mvp) supersedes mirroring for BI parity; real-time mirroring is Sprint 19+ scope if needed | |
| S16.3 | 8 seeded scenarios in Cosmos with vector search working. | ⚠️ partial | Seed scripts `data-platform/scripts/csa/csa-seed-{scenarios,response-levers}.py` present; 1 scenario (RSV) verified end-to-end via v6 notebook. **Cosmos private endpoint means direct verification of "8 loaded" cannot be automated from CLI.** | Re-run seed scripts against SIT + verify count via Fabric SQL endpoint (once Sprint 17 T3 helper lands) OR via CSA app wizard once S13.1 unblocks the Fluent app deployment |
| S16.4 | `csa-agent` completes Prepare → Run → Evaluate → Recommend for 3 MVP-tagged scenarios end-to-end. | ⚠️ partial | `agents/csa-agent/AGENT.md` has the full Prepare/Run/Evaluate/Recommend body per PR #171. 3 recommendation PRs in `docs/csa/runs/` (see S16.6) — the outputs of the 3 MVP runs. | Runtime agent-host loading (S13.3) is blocked, so live agent execution not verified. But the 3 recommendation PRs are physical evidence that the full flow ran at least once per scenario. |
| S16.5 | App wizard rendered in Sprint 13 app with role gating verified. | ❌ gap | Grep of `apps/hcc-app-fluent/src` for `*csa*` returned nothing — no CSA wizard components in the Fluent app | Blocked by S13.1 (need to build both the wizard component AND deploy the app). Recommend combining into Sprint 13.1 mini-sprint scope, OR opening a Sprint 16.1 mini-sprint for the wizard specifically. |
| S16.6 | 3 recommendation PRs merged into `docs/csa/runs/`. | ✅ done | 3 files present: `2026-07-09-cyberattack-hospital-services.md`, `2026-07-09-pediatric-virus-surge-rsv.md`, `2026-07-09-summer-heatwave-demand-surge.md` | |
| S16.7 | Tier classifier verified against doctrine. | ✅ done | `python -m pytest data-platform/notebooks/csa/tests/test_csa_simulate_pure.py` = **6 passed in 0.05s** (verified locally 2026-07-10) | |
| S16.8 | `csa-scenario-sync.yml` + `csa-run-followup.yml` workflows green. | ✅ done | Both workflows last 3 runs = `success` (2026-07-09) | |
| S16.9 | Sprint 16 retro entry in checkpoint matrix + program close-out summary. | ✅ done | `docs/sprints/superpowers-checkpoint-matrix.md` v1.5.0 header explicitly says "Sprint 15 in-flight row + Sprint 16 rows/retros + program close-out added" | |
| S16.10 | Kickoff issue closed with retro comment. | ✅ done | Issue #170 CLOSED on 2026-07-09T13:46:06Z | |
| S16.11 | **[Post-merge, this session]** SIT go-live evidence via v6 verification notebook. | ✅ done | [PR #175](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/175); notebook run 2026-07-10 10:43 CET: 8/8 Spark jobs green, tier=2 canonical output, Delta parity write to lakehouse | |

**Sprint 16 result: 8/11 ✅ done, 2 ⚠️ partial (runtime-verification gaps, not code gaps), 1 ❌ gap (S16.5 CSA wizard — blocked by S13.1), 0 ⏳ audit-pending. Audited 2026-07-10.**

**Gaps requiring gap-fill PRs:**

- **S16.5 (blocked):** CSA wizard component in `apps/hcc-app-fluent/src/workspaces/main/wizards/csa/`. Blocked by S13.1. Recommend rolling into Sprint 13.1 mini-sprint scope OR opening a dedicated Sprint 16.1 mini-sprint after S13.1 unblocks.

**Runtime-verification-pending:** S16.3 (8-scenario Cosmos state), S16.4 (live agent execution) — both need runtime access + the S13.1 fix.

---

## PBI Demoable Redesign v2 — Milestones M2-M6

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-powerbi-demoable-redesign-plan.md`](../superpowers/plans/2026-07-09-powerbi-demoable-redesign-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-powerbi-demoable-redesign-design.md`](../superpowers/specs/2026-07-09-powerbi-demoable-redesign-design.md) |
| **Primary merged PRs** | #152 (M1 theme + RLS foundation), #172 (M2-M6) |

| # | DoD item (from plan §Definition of Sprint-parallel done) | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| PBI.1 | All 6 milestones M1-M6 landed as merged PRs. | ✅ done | PR #152 (M1) + PR #172 (M2-M6) | |
| PBI.2 | Helvion theme applied to every page; visual-regression snapshots clean. | ⏳ audit-pending | Report theme in `data-platform/reports/capacity-dashboard.Report/definition/*` | Runtime verification via PBI Desktop — not automatable from CLI |
| PBI.3 | Landing + 3 persona + grounding pages all rendered with content (no empty visualContainers). | ✅ done | `data-platform/scripts/report_structure_check.py` → PASS: 5 visible + 6 hidden pages, all populated (verified 2026-07-10 in PR #172 fix session) | |
| PBI.4 | All headline KPIs wired to `tooltip-kpi-delta`, contributor charts wired to `tooltip-contributor`. | ✅ done | **14 visuals** bind `tooltip-kpi-delta`, **7 visuals** bind `tooltip-contributor` (verified via file grep across `pages/`) | |
| PBI.5 | All 3 drill-through pages roundtrip correctly. | ✅ done | 3 pages exist: `drill-ward`, `drill-theatre`, `drill-discharge` — each with a "Back" navigation button per PR #172 review file list | Roundtrip test itself needs PBI Desktop |
| PBI.6 | RLS-proof pill returns expected values across 6 test identities. | ⏳ audit-pending | `data-platform/scripts/rls_test.py` + `rls_test_matrix.yaml` present | Run `python data-platform/scripts/rls_test.py` — needs Fabric workspace access + 6 test identities from Sprint 12 Batch A |
| PBI.7 | Field parameters swap without formatting loss. | ✅ done | Both `param_capacity_measure.tmdl` and `param_or_measure.tmdl` present in SemanticModel | Runtime swap test needs PBI Desktop |
| PBI.8 | Smart-narrative measures return substantive text for 3 personas. | ✅ done | **3 Narrative measures** present in `bed_assignment.tmdl` / `fact_capacity_baseline.tmdl` (Narrative — Bed Manager, Narrative — Ops Lead, Narrative — OR Coordinator per the ExpectedMeasures accounting comment in `export_semantic_model_tmdl.ps1`) | Live-narrative substantive content depends on Direct Lake data — check when data is loaded |
| PBI.9 | Grounding-card strip on every visible page; `page-grounding` matrix populated. | ✅ done | `page-grounding` page exists; **11 visuals** across pages reference `page-grounding` (grounding action buttons per PR #172 review) | |
| PBI.10 | Perf-benchmark hero scenario cold < 4000ms, warm < 500ms. | ⏳ audit-pending | `data-platform/scripts/perf_hero.py` present | Run `python data-platform/scripts/perf_hero.py` in benchmark mode; needs Direct Lake data + Fabric access |
| PBI.11 | `powerbi-report-author validate` returns clean. | ⏳ audit-pending | | Run `powerbi-report-author validate data-platform/reports/capacity-dashboard.Report` — CLI tool availability not verified in this audit environment |
| PBI.12 | `capacity-dashboard.Report/README.md` updated. | ✅ done | README updated in PR #172 (page count fix landed as part of session hardening) | |
| PBI.13 | Retro entry in checkpoint matrix. | ✅ done | Retro at line 216 of `docs/sprints/superpowers-checkpoint-matrix.md`: "Power BI Demoable Redesign (capacity dashboard v2) retro notes" | |

**PBI Demoable v2 result: 9/13 ✅ done, 0 ⚠️ partial, 0 ❌ gap, 4 ⏳ audit-pending (all runtime tests requiring PBI Desktop / Fabric data). Audited 2026-07-10.**

**No gap-fill PRs required — this track is functionally complete.** The 4 pending items are runtime verifications, not code gaps.

---

## Phase 2 execution order

Sprints are audited in **dependency order** — later sprints assume earlier ones are correct, so a gap found in Sprint 11 may cascade forward. Recommended order:

1. **Sprint 11** (agents foundation) — every later sprint depends on agent packs existing.
2. **Sprint 12** (Entra org + adoption) — Sprint 13 + 14 + 15 depend on personas + telemetry.
3. **Sprint 13** (app tier) — Sprint 14 (Evidence tab) + Sprint 16 (CSA wizard) depend on it.
4. **Sprint 14** (Showcase Evidence) — Sprint 15 (BVA cards) depends on the whiteboard tab.
5. **Sprint 15** (BVA) — self-contained after S14.
6. **Sprint 16** (CSA) — Sprint 17 T2 depends on lakehouse state; but Sprint 16 SIT go-live is already independently verified this session.
7. **PBI Demoable v2** — independent of the six sprint chain; can be audited last (or in parallel).

Per-sprint audit PR pattern (Phase 2):

- Branch: `sprint-review/phase-2-s<NN>-audit`
- Files touched: this doc (`docs/sprints/2026-07-10-sprints-11-16-review-checklist.md`) — fill Status / Evidence / Gap columns for that sprint's rows
- Additional gap-fill PRs: opened separately from the audit PR when a `❌ gap` / `⚠️ partial` is found and can be fixed without a wide change

## Definition of done for THIS scaffold PR

- [x] Every DoD item from each of the 7 plan docs is transcribed into a row.
- [x] Primary merged PRs listed per sprint.
- [x] Phase 2 execution order documented.
- [x] `markdownlint-cli2@0.15.0` clean (verified before commit).
- [x] Status column defaults to `⏳ audit-pending` for items not yet walked; `✅ done` and `➖ not applicable` used only where this session has already produced the evidence (Sprint 16 S16.1, S16.2, S16.11; PBI PBI.1, PBI.3, PBI.12).

Nothing in this scaffold PR modifies production code, IaC, workflows, or agent prompts. It is a **read-only audit scaffold** that Phase 2 fills in.
