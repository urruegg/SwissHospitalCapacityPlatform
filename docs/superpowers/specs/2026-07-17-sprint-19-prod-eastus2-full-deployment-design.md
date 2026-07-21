# Sprint 19 — PROD Region Pivot to Switzerland North (Greenfield Decommission-and-Rebuild) — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 2.0.0 |
| **Date** | 2026-07-21 |
| **Author** | Urs Rüegg |
| **Status** | Accepted (region pivot) — supersedes the eastus2/westus2 PROD build recorded in §7 (now the **Phase 0 decommission target**); Switzerland North greenfield rebuild pending `approved-to-apply` |
| **Previous Version** | 1.6.0 (P7 integration outcome — `app.curavias.ch` custom domain + managed cert bound to the PROD app, PROD Entra SPA redirect URIs, Logic App skip). 2.0.0 is a **MAJOR** bump: it reverses the "PROD in eastus2/westus2" region decision, backed by [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md). The whole prior eastus2/westus2 PROD footprint becomes the DR-style decommission target; PROD is rebuilt greenfield in `switzerlandnorth` at SIT parity. |
| **Anchor triggers** | [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md) (Switzerland North PROD pivot, live-`az`-verified 2026-07-21); [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md) sunset-to-`switzerlandnorth` intent now executed; Switzerland North Fabric quota (0/512) + OpenAI GA catalog confirming SIT-parity feasibility |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution; Bicep-first IaC for all PROD resources |
| **Prerequisites** | Sprint 18 complete (Foundry agents proven E2E in eastus2); Fabric capacity stabilized; App Fluent builds green |

---

> ## ⚠️ Region pivot notice (2026-07-21) — this sprint changed direction
>
> This sprint originally deployed PROD **split across two US regions** — Foundry
> in `eastus2` ([ADR-0032](../../adr/0032-foundry-control-plane-eastus2.md)) and
> Fabric in `westus2` ([ADR-0035](../../adr/0035-fabric-iq-layer-region-westus2.md))
> — because each service had zero quota in the other US region. That footprint is
> **built and verified** (see §7, kept as the execution record).
>
> Live `az` verification on 2026-07-21 (sub `66a9953a-df37-4c51-856c-9971b9bf3e03`)
> confirmed Switzerland North now has **Fabric quota 0/512**, an **OpenAI GA
> catalog** covering all three agent models (gpt-5, gpt-5-mini, o3), and
> **Foundry Agent Service GA** — enough for **single-region SIT parity**. Per
> [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md), PROD now
> pivots to a **greenfield Switzerland North** deployment, executed **DR-style**:
> **Phase 0 decommissions the entire eastus2/westus2 PROD footprint first**, then
> PROD is rebuilt clean in `switzerlandnorth` at SIT parity in a single resource
> group `rg-ihzhhpf-prod`. **SIT (westus2 + eastus2) is untouched.** Sections 1–6,
> 10 and 14 below describe the **new** target; §7 is retained as the history of
> the now-decommissioned footprint.

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and rationale](#2-context-and-rationale)
3. [Scope](#3-scope)
4. [Architecture — PROD target state](#4-architecture--prod-target-state)
5. [Resource inventory (PROD Switzerland North)](#5-resource-inventory-prod-switzerland-north)
6. [Task breakdown](#6-task-breakdown)
7. [Bicep module plan](#7-bicep-module-plan)
8. [DNS and custom domain strategy](#8-dns-and-custom-domain-strategy)
9. [Security and identity](#9-security-and-identity)
10. [Fabric capacity and workspace](#10-fabric-capacity-and-workspace)
11. [Side-effect posture and approval gates](#11-side-effect-posture-and-approval-gates)
12. [Dependencies](#12-dependencies)
13. [Risk register](#13-risk-register)
14. [Definition of done](#14-definition-of-done)
15. [References](#15-references)

---

## 1. Goal and desired end state

**Decommission the entire eastus2/westus2 PROD footprint, then deploy the whole
PROD environment greenfield in `switzerlandnorth`** — DR-style, single-region,
at SIT service parity. This executes the [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md)
sunset-to-Switzerland intent now that Switzerland North has verified quota and GA
services (per [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md)),
and collapses the two-US-region split into one Swiss region.

**Desired end state:**

* Prior PROD footprint (`rg-ihzhhpf-prod-eastus2` + `fabricihzhhpfprod` in
  westus2 + the managed App Insights RG) **deleted** — no PROD resources remain
  in any US region.
* Single `rg-ihzhhpf-prod` resource group in **`switzerlandnorth`** with all
  platform resources deployed via Bicep.
* Full stack (SIT parity): Container Apps (agent-host + app-fluent + sim),
  Cosmos DB (CSA + platform), Event Hubs, Service Bus, Key Vault, VNet + private
  endpoints, AI Services + Foundry project, Fabric capacity (F2), Storage, Log
  Analytics, Application Insights, Logic Apps, Container Registry — **all in
  `switzerlandnorth`**.
* All 8 agents registered and functional in the PROD Foundry project on the
  Switzerland North account (gpt-5 / gpt-5-mini / o3, GA in swn).
* Custom domain `app.curavias.ch` (PROD) re-pointed to the new Switzerland North
  Container App.
* Fabric PROD workspace connected to the Switzerland North lakehouse (F2, quota
  0/512 available — **no cross-region hop**, unlike the westus2 interim).
* End-to-end demo flow operational: sign-in → app → agent invocation → data
  query → response.
* **SIT remains untouched** throughout (westus2 + eastus2).

> **Residency posture (not a blocker now).** Under [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md)
> / [ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md) the data is synthetic
> and PHI-free, so the region choice is about topology and sovereignty
> readiness, not data residency. The three agent models are `GlobalStandard`
> SKU (cross-geo inference); true in-Switzerland residency (regional `Standard`
> SKU: gpt-4.1 / gpt-4o + embeddings) becomes decisive only at a future PHI PROD
> and is recorded in ADR-0037 as a revisit criterion.

---

## 2. Context and rationale

### Why fresh deployment (not migration)

| Factor | Migrate existing | Fresh deploy |
|--------|-----------------|--------------|
| Cosmos DB data | Requires export/import + PE rewire + vector re-index | Fresh schema + synthetic seed — cleaner |
| Container Apps | Can't move — must redeploy | Same outcome, simpler |
| Event Hubs / Service Bus | Message state not portable | Fresh — no persistent messages needed |
| Key Vault | Secrets can be recreated | Fresh — all secrets are synthetic/generated |
| Network topology | Complex PE migration | Clean VNet design from scratch |
| Blast radius | Risk breaking SIT during migration | Zero impact on existing SIT |
| Time | Higher — debugging migration issues | Lower — known Bicep patterns |

**Decision:** PROD is torn down and rebuilt **greenfield in `switzerlandnorth`**.
No data migration required (synthetic data regenerated by the simulator). The
existing eastus2/westus2 PROD footprint is **decommissioned first (Phase 0,
DR-style)** so the rebuild starts from a clean single-region slate. **SIT stays
in westus2 + eastus2, untouched.**

### Why Switzerland North now (2026-07-21 pivot)

Live `az` verification (sub `66a9953a-df37-4c51-856c-9971b9bf3e03`, 2026-07-21)
confirmed Switzerland North is ready for **single-region SIT parity**:

* **Fabric quota 0/512** available in swn (vs eastus2 = 0/0 — the original
  blocker that forced Fabric into westus2). PROD Fabric F2 can now be
  **co-located** with the rest of PROD — no cross-region HTTPS hop.
* **OpenAI GA catalog** in swn covers all three agent models (**gpt-5**,
  **gpt-5-mini**, **o3**) plus the gpt-5.4/5.5/5.6 families and gpt-4.1/gpt-4o.
* **Foundry Agent Service GA** in swn (Responses + Agents; the only gap is
  Class-A private-IP networking, not needed under the network-off demo slice).
* **Fabric IQ Ontology + Data Agent** are region-listed for CH North (Preview),
  subject to the same per-capacity preview toggle tracked in
  [#270](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/270) —
  region-independent, so no worse than the westus2 PROD status quo.
* **Swiss sovereignty readiness**: collapsing the two-US-region split into one
  Swiss region is the intended [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md)
  sunset and de-risks the eventual PHI PROD (residency-tier models available in
  swn when needed — see ADR-0037).

See [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md) for
the full evidence table and the residency/SKU nuance.

### Why eastus2 was chosen originally (superseded 2026-07-21)

> Retained for history. This rationale drove versions 1.0.0–1.6.0 and is
> **superseded** by "Why Switzerland North now" above per ADR-0037.

* 122 OpenAI models (88 GA), 5.8M TPM quota — richest in the tenant
* Foundry Agent Service GA supported
* All 22 resource types confirmed GA (Sprint 18 feasibility analysis)
* DataZone + ProvisionedManaged SKUs available for future scale
* Same continent as current deployment (acceptable latency for EU-based users during demo scope)
* **Why it was split**: westus2 had 0 OpenAI quota, so Foundry went to eastus2;
  eastus2 had 0 Fabric quota, so Fabric stayed in westus2. Switzerland North
  resolves both at once, removing the split.

---

## 3. Scope

### In scope

> **All region references below retarget from eastus2/westus2 to
> `switzerlandnorth`, and from `rg-ihzhhpf-prod-eastus2` to the single
> `rg-ihzhhpf-prod`.** Resource names drop the `-eastus2` infix and follow the
> naming convention (`<type>-ihzhhpf-prod`, shared/PROD suffix `-prod`).

**Phase 0 — DR-style decommission (runs first, `approved-to-apply`-gated):**

| # | Item | Deliverable |
|---|------|-------------|
| T0a | Delete `rg-ihzhhpf-prod-eastus2` (all ~22 resources: Foundry account+project, Container Apps ×2 + CAEs, Cosmos ×2, Event Hubs, Service Bus, Key Vault, ACR, Log/AppInsights, VNet+NSGs, identities) | US PROD RG removed |
| T0b | Delete `fabricihzhhpfprod` (F2, westus2) + purge if soft-deleted | US PROD Fabric removed |
| T0c | Remove the managed App Insights RG + verify no PROD resources remain in any US region; note purge-protected KV auto-expiry (non-blocking, new swn KV name differs) | Clean slate confirmed |

**Phase 1+ — Switzerland North greenfield rebuild (SIT parity):**

| # | Item | Deliverable |
|---|------|-------------|
| T1 | Bicep: PROD Switzerland North landing zone via `infra/main.bicep` + new `infra/environments/prod-swn.bicepparam` (`location='switzerlandnorth'`) | Reuse SIT-proven orchestrator |
| T2 | VNet + subnets + NSGs | Network foundation |
| T3 | Key Vault (PROD) | Secrets store |
| T4 | Storage Account (PROD) | Platform storage |
| T5 | Log Analytics + App Insights | Observability stack |
| T6 | Container Registry | Shared image registry (geo-replicated from SIT or new) |
| T7 | Container Apps Environment + apps (3) | Agent-host + App Fluent + Sim Capacity |
| T8 | Cosmos DB (2 accounts: CSA + platform) | NoSQL + vector search + private endpoints |
| T9 | Event Hubs namespace | Event ingestion |
| T10 | Service Bus namespace | Message routing |
| T11 | AI Services + Foundry project | Control plane (switzerlandnorth-native, GA) |
| T12 | Model deployments (gpt-5, gpt-5-mini, o3) | Agent backing models |
| T13 | Agent registration (8 agents) | Full roster in PROD |
| T14 | Managed Identities (7) | Workload identities |
| T15 | Private endpoints + Private DNS zones | Cosmos DB + Key Vault PE |
| T16 | Fabric capacity (F2) | PROD Fabric in switzerlandnorth (quota 0/512, co-located) |
| T17 | DNS: `app.curavias.ch` → PROD Container Apps | Custom domain + managed TLS |
| T18 | Logic Apps workflow | Platform orchestration |
| T19 | Entra: PROD app registration bindings | RBAC for PROD identities |
| T20 | End-to-end PROD verification | Full demo flow proven |
| T21 | Bicep `what-if` + deployment evidence | IaC proof |
| T22 | PROD evidence document | `docs/sprints/prod-evidence-eastus2.md` |

### Out of scope

* **SIT decommission** (SIT stays in westus2 + eastus2, untouched by this sprint)
* PHI data onboarding (per ADR-0016, demo scope only) — and therefore regional
  residency-tier model deployment (deferred to a future PHI PROD, see ADR-0037)
* Multi-region DR / failover (single-region swn is sufficient for demo scope;
  the Phase 0 teardown is DR-*style* process, not standing DR capability)
* Fabric IQ Ontology + Data Agent in PROD swn (Preview per-capacity gate #270 —
  SIT remains the live Fabric IQ seam; unblocking is tracked separately)

---

## 4. Architecture — PROD target state

```mermaid
flowchart TB
  subgraph eastus2["eastus2 — PROD (all resources collocated)"]
    subgraph vnet["vnet-platform-ihzhhpf-prod"]
      subgraph snet_cae["snet-cae"]
        CAE["Container Apps Environment"]
        CA_HOST["ca-agent-host-ihzhhpf-prod"]
        CA_APP["ca-app-fluent-ihzhhpf-prod"]
        CA_SIM["ca-sim-capacity-ihzhhpf-prod"]
      end
      subgraph snet_data["snet-data"]
        PE_COSMOS["PE: Cosmos CSA"]
        PE_COSMOS2["PE: Cosmos Platform"]
        PE_KV["PE: Key Vault"]
      end
    end

    AI["ai-ihzhhpf-prod-eastus2<br/>+ Foundry project<br/>+ 3 model deployments<br/>+ 8 registered agents"]
    COSMOS_CSA["cosmos-csa-ihzhhpf-prod<br/>NoSQL + vector search"]
    COSMOS_PLAT["cosmos-ihzhhpf-prod<br/>Platform state"]
    EVH["evh-ihzhhpf-prod<br/>Event Hubs"]
    SB["sb-ihzhhpf-prod<br/>Service Bus"]
    KV["kv-ihzhhpf-prod<br/>Key Vault"]
    LOG["log-ihzhhpf-prod<br/>Log Analytics"]
    APPI["appi-ihzhhpf-prod<br/>App Insights"]
    STG["st-ihzhhpf-prod<br/>Storage"]
    FABRIC["fabricihzhhpfprod<br/>F2 capacity"]
    ACR["crihzhhpfprod<br/>Container Registry"]

    CA_HOST --> AI
    CA_HOST --> COSMOS_CSA
    CA_HOST --> EVH
    CA_APP --> SB
    CA_SIM --> EVH
    PE_COSMOS --> COSMOS_CSA
    PE_COSMOS2 --> COSMOS_PLAT
    PE_KV --> KV
  end

  DNS["app.curavias.ch"] -->|CNAME| CA_APP
  FABRIC --> GOLD["Gold lakehouse<br/>semantic model"]
```

---

## 5. Resource inventory (PROD Switzerland North)

> All PROD resources land in the **single `rg-ihzhhpf-prod` resource group in
> `switzerlandnorth`**. Names drop the `-eastus2` infix (the split-region
> artefact) and follow the naming convention `<type>-ihzhhpf-prod`. The table
> below is the **target** — the eastus2/westus2 names in §7 are the
> now-decommissioned prior footprint.

| # | Resource Type | Name Pattern | SKU/Tier | Notes |
|---|------|------|------|-------|
| 1 | Resource Group | `rg-ihzhhpf-prod` | — | New single-region RG in **switzerlandnorth** |
| 2 | VNet | `vnet-platform-ihzhhpf-prod` | — | 3 subnets: snet-cae, snet-data, snet-app |
| 3 | NSGs (×3) | `*-nsg-ihzhhpf-prod` | — | Per subnet (switzerlandnorth) |
| 4 | Key Vault | `kv-ihzhhpf-prod` | Standard | RBAC mode, purge protection |
| 5 | Storage | `stihzhhpfprod` | Standard_LRS | Platform storage |
| 6 | Log Analytics | `log-ihzhhpf-prod` | PerGB2018 | 30-day retention |
| 7 | App Insights | `appi-ihzhhpf-prod` | — | Connected to Log Analytics |
| 8 | Container Registry | `crihzhhpfprod` | Basic | Or geo-replicate SIT ACR |
| 9 | CAE | `cae-ihzhhpf-prod` | Consumption | VNet-integrated (snet-cae) |
| 10 | CA: agent-host | `ca-agent-host-ihzhhpf-prod` | — | 7 agents loaded |
| 11 | CA: app-fluent | `ca-app-fluent-ihzhhpf-prod` | — | Custom domain + TLS |
| 12 | CA: sim-capacity | `ca-sim-capacity-ihzhhpf-prod` | — | Simulator |
| 13 | Cosmos CSA | `cosmos-csa-ihzhhpf-prod` | Serverless | NoSQL + vector, PE, AAD-only |
| 14 | Cosmos Platform | `cosmos-ihzhhpf-prod` | Serverless | Platform state, PE, AAD-only |
| 15 | Event Hubs | `evh-ihzhhpf-prod` | Standard | 1 TU |
| 16 | Service Bus | `sb-ihzhhpf-prod` | Standard | — |
| 17 | AI Services | `ai-ihzhhpf-prod` | S0 | Foundry-enabled, **switzerlandnorth** (GA) |
| 18 | Foundry Project | `ai-ihzhhpf-prod-project` | — | 8 agents + 3 models (gpt-5/gpt-5-mini/o3, GA in swn) |
| 19 | Fabric Capacity | `fabricihzhhpfprod` | F2 | **switzerlandnorth** (quota 0/512 — co-located, no cross-region hop) |
| 20 | Logic App | `logic-ihzhhpf-prod` | Consumption | Orchestration flows |
| 21 | Managed Identities (×7) | `id-*-ihzhhpf-prod` | — | Per workload |
| 22 | Private Endpoints (×3) | `pe-*-ihzhhpf-prod` | — | Cosmos CSA, Cosmos Platform, KV |
| 23 | Private DNS Zones | `privatelink.documents.azure.com` | Global | VNet link |
| 24 | DNS Zone | `curavias.ch` | Global | Already exists (shared) |
| 25 | Managed Certificate | `cert-app-curavias-ch` | — | On CAE |

---

## 6. Task breakdown

| Phase | Tasks | Depends on | Effort |
|-------|-------|------------|--------|
| **P0: Decommission (DR-style, first)** | T0a–T0c (delete `rg-ihzhhpf-prod-eastus2`, `fabricihzhhpfprod` westus2, managed AppInsights RG; confirm clean slate) | `approved-to-apply` | 1h |
| **P1: IaC authoring** | T1 (`prod-swn.bicepparam`, `location='switzerlandnorth'`) | P0 done | 1h |
| **P2: Foundation** | T2–T6 (VNet, KV, Storage, Log, ACR) | T1 reviewed | 1h |
| **P3: Compute** | T7 (CAE + 3 apps) | P2 | 2h |
| **P4: Data** | T8–T10 (Cosmos ×2, EVH, SB) + T15 (PEs) | P2 | 2h |
| **P5: AI/Foundry** | T11–T13 (AI + project + models + agents, swn GA) | P2 | 2h |
| **P6: Fabric** | T16 (F2 capacity + workspace, swn — no cross-region) | P2 | 1h |
| **P7: Integration** | T17 (DNS re-point), T18 (Logic), T19 (Entra) | P3, P4, P5 | 2h |
| **P8: Verification** | T20–T22 (E2E test, evidence) | P3–P7 | 3h |

**Total estimated effort:** ~15 hours (2–3 working days). Because PROD reuses the
SIT-proven `infra/main.bicep` (Option 1, see §7) and the Foundry/Fabric API
patterns are already scripted, the rebuild is mostly re-parameterise-and-replay;
the new work is **P0 (decommission)** and swapping `location` to
`switzerlandnorth`.

---

## 7. Bicep module plan

> ## 🗄️ §7 is the execution history of the now-decommissioned eastus2/westus2 PROD footprint
>
> Everything in §7 (7a–7f) records the **prior** PROD build that Phase 0 (§6)
> **tears down**. It is kept verbatim as the audit trail of what was deployed and
> why. For the **Switzerland North rebuild**, the same Option-1 approach applies
> unchanged — reuse `infra/main.bicep` via a **new
> `infra/environments/prod-swn.bicepparam`** (`environmentName='prod'`,
> `location='switzerlandnorth'`), leaner module selection identical to the
> eastus2 param — with two simplifications the swn region enables:
> **(a) Fabric co-locates in swn** (quota 0/512, no westus2 cross-region hop, so
> §7e no longer applies); **(b) the ACR is a fresh PROD-local `crihzhhpfprod` in
> swn** (`az acr import` from SIT ACR, same as §7b). Read §7 as "how PROD was
> built in the US" — replace every `eastus2`/`westus2` with `switzerlandnorth`
> and `rg-ihzhhpf-prod-eastus2` with `rg-ihzhhpf-prod` for the rebuild.
>
> ---
>
> **Revised 2026-07-19 (v1.1.0) — Option 1 (reuse) adopted.** The fresh
> `infra/prod-eastus2/modules/*` tree below is **superseded**. Rather than
> re-author 15 modules, PROD reuses the existing, SIT-proven orchestrator
> `infra/main.bicep` (550 lines, 20+ `enable<X>Module` gates, parameterised
> `location`) via a **new environment param file
> `infra/environments/prod-eastus2.bicepparam`** (`environmentName='prod'`,
> `location='eastus2'`). This is DRY, avoids module drift, and lets every
> PROD deploy benefit from SIT hardening. Module *selection* for PROD is
> leaner than SIT: the legacy App Service / ML-workspace topology
> (`experience-hosting`, `api-runtime`, `ai-ml-foundation`) is **excluded** —
> the PROD demo target is Container Apps + Foundry + Fabric + Cosmos only (see
> §5 inventory).
>
> **Prerequisite done 2026-07-19:** the abandoned westus2 `rg-ihzhhpf-prod`
> (19 resources: App Service, ML workspace, Cognitive Services, EventHub,
> ServiceBus, KV, ACR, VNet, …) was **decommissioned** (`approved-to-apply`
> by @urruegg) so PROD is region-isolated to eastus2. Cognitive Services was
> purged; the Key Vault `kv-ihzhhpf-prod-i62t` is purge-protected and
> auto-expires 2026-10-16 (non-blocking — the new deploy uses a distinct KV
> name).

### 7b. Verified deploy outcome — P1–P3 (2026-07-19)

Approved-to-apply @urruegg 2026-07-19T00:53 +02:00. Deployment
`sprint19-prod-eastus2-p1` Succeeded in 2m26s (2026-07-19T05:37Z) into
`rg-ihzhhpf-prod-eastus2`. **17 resources**, both Container Apps live on
PROD-local images.

The first attempt surfaced two limitations in the reused shared modules; both
are now documented constraints for future PROD/region work:

1. **Cross-RG ACR is unsupported.** `modules/agent-host/container-app.bicep`
   references the registry with `existing = { name: last(split(resourceId,'/')) }`
   — resolved **in the deployment resource group**, with no cross-RG scope. A
   cross-region pull from the SIT ACR therefore fails `ResourceNotFound`.
   **Decision:** stand up a **PROD-local ACR `crihzhhpfprod`** in the PROD RG and
   `az acr import` the images from the SIT ACR. This is also the more
   region-isolated end-state (reverses the interim "reuse SIT ACR" idea).
2. **Cosmos private endpoint depends on the CSA-Cosmos DNS zone.**
   `modules/agent-host/cosmos-pe.bicep` references
   `privatelink.documents.azure.com` as `existing`; that zone is created only by
   `modules/cosmos/csa.bicep`. With the CSA module out of scope, the PE fails
   `InvalidPrivateDnsZoneIds`. **Decision:** `enableNetworkModule=false` for the
   first slice → public CAEs + public Cosmos (synthetic data, no PHI per
   ADR-0013). VNet + private endpoint becomes a **hardening follow-up** (must
   also provision/own the privatelink zone independently of CSA-Cosmos).

**Verified live:** agent-host `/healthz` → `{"status":"ok"}`, `/agents` → 200;
app-fluent `/` → 200; Cosmos db `agenthost` has `conversations` / `audit` /
`approval-events`; KV `kv-ihzhhpf-prod-q4nk` (distinct name dodged the
purge-protected `-i62t`). Commits `6d31559` + `0913b02`.

**Still deferred:** Redis (eastus2 Balanced SKU unverified), P4 Event Hubs /
Service Bus, P5 Foundry-hosted agents, P6 Fabric F2 workspace + Data Agent, P7
DNS cutover `app.curavias.ch`, VNet/PE hardening.

### 7c. P4 data lane — deployed via the CI/CD workflow (2026-07-19)

The P4 data lane was deployed through the **`cd-infra-deploy-prod` GitHub
workflow** (not a local `az` command) to prove the CI/CD infra path
end-to-end: `policy-gate` → `environment: prod` OIDC → what-if → deploy.

**#252 Phase A — CSA Cosmos parity (prerequisite).** The CSA Cosmos account was
an out-of-band standalone deploy, invisible to `main.bicep` and CI what-if
([#252](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/252)).
Phase A wired it into the orchestrator behind an `enableCsaCosmosModule` gate (a
`csaCosmos` block calling `modules/cosmos/csa.bicep`), added an
`agentHostMiPrincipalId` output on the agent-host module for the data-contributor
role assignment, and pinned `publicNetworkAccess` in `csa.bicep`. Enabled in
`sit.bicepparam` (idempotent — SIT what-if **0 Create / 0 Delete**) and
`prod-eastus2.bicepparam` (which also enables EVH + SB). Commit `a0eeda1`.

**CI/CD finding — stale `prod` environment.** The GitHub `prod` environment
variables still targeted the decommissioned westus2 footprint
(`rg-ihzhhpf-prod` / `prod.bicepparam` / `westus2`); corrected to
`rg-ihzhhpf-prod-eastus2` / `prod-eastus2.bicepparam` / `eastus2`. Broader
stale vars (`SOLUTION_SHORT_NAME`, `PROD_SOURCE_SQL_*`, `PROD_FABRIC_*` →
frozen tenant `mngenvmcap228255`) are noted on #252 for a follow-up sweep.

**Outcome.** Workflow run `29679485559` — policy-gate PASSED, `Deploy PROD`
approved at the required-reviewer gate, green in 5m8s. PROD what-if **12 Create
/ 0 Delete**; verified live: `cosmos-csa-ihzhhpf-prod` (db `csa` + 4 containers
`scenarios` / `agent-memory` / `response-levers` / `simulation-runs`),
`evh-ihzhhpf-prod-q4nk` (hub `events` + consumer groups `cg-bm-copilot-agent` /
`cg-csa-agent` / `cg-fabric-eventstream`), `sb-ihzhhpf-prod-q4nk` (Active).

**MCAPSGov policy note.** Both `cosmos-csa-ihzhhpf-prod` and the platform
`cosmos-ihzhhpf-prod` show `publicNetworkAccess=Disabled` live despite the
template requesting `Enabled`. The subscription policy is a **Modify-effect**
that force-disables public Cosmos: deploys succeed, but the accounts are
unreachable without a private endpoint. Runtime reachability folds into the
**VNet + private-endpoint hardening** follow-up; P4 *provisioning* is complete.

### 7d. P5 Foundry agents — provisioned via the Sprint 18 API pattern (2026-07-19)

Approved-to-apply @urruegg 2026-07-19 10:47 +02:00. The Foundry control plane
(project + models + agents) is **not** Bicep-managed, so P5 followed the proven
Sprint 18 pattern (az CLI + Foundry data-plane API) against `ai-ihzhhpf-prod`.

**IaC parity gap — `allowProjectManagement`.** Project create failed until the
account had `properties.allowProjectManagement=true`;
`modules/ai-platform/main.bicep` does not set it (SIT had it out-of-band). Fixed
via a `PATCH` and logged on #252 — the module should set it declaratively so
future accounts are project-ready from Bicep.

**Verified end state:** project `ai-ihzhhpf-prod-project` (`Succeeded`); 3 model
deployments `gpt-5` / `gpt-5-mini` / `o3` (all `Succeeded`, GlobalStandard
50/100/30 TPM); `id-ca-agent-host-ihzhhpf-prod` granted **Cognitive Services
User**; **8 agents** registered via the v2 persistent-agents API
(`/agents`, api-version `2025-05-15-preview`, `definition.kind=prompt`),
replicated from the SIT v2 definitions with model assignments cross-checked OK.

**Invocation note:** the v2 `/agents` API needs a `definition` wrapper — not the
classic OpenAI Assistants (`asst_*`) `threads/runs` shape. Live-inference E2E
runs through the agent-host `azure-ai-projects` SDK and is verified in **P8/T9**,
not via the raw REST runs API.

### 7e. P6.1 Fabric capacity — westus2 (eastus2 quota = 0) (2026-07-19)

Approved-to-apply @urruegg 2026-07-19 11:29 +02:00. The eastus2 create failed:

> `BadRequest: The sum total of CapacityUnits of all Fabric capacities … must
> not exceed the regional quota … TotalCapacityUnits: 0, RegionalQuota: 0`

The `Microsoft.Fabric` usages API confirms the subscription has **0 CU** quota
in eastus2 and **512 CU** in westus2 (2 CU used by the SIT F2). Per the user
decision, PROD Fabric is placed in **westus2** — Fabric is a region-flexible
SaaS plane reachable cross-region over HTTPS from the eastus2 app/agents (same
cross-region tolerance as the Sprint 18 topology), acceptable under the
ADR-0013 synthetic demo scope. A clean all-eastus2 end-state would require an
eastus2 Fabric quota-increase request (deferred).

**Verified:** `fabricihzhhpfprod` — F2/Fabric, **westus2**, in
`rg-ihzhhpf-prod-eastus2`, admin `admin@mngenvmcap164444.onmicrosoft.com`,
created Active (`provisioningState=Succeeded`) then **suspended** → `state=Paused`
to save cost. §10 and the §5 resource inventory updated to westus2.

**P6.2 (deferred to a dedicated slice):** create workspace `ws-ihzhhpf-prod-data`,
attach to the capacity, Git-connect, deploy lakehouse + notebooks + semantic
model, and run the simulator for synthetic PROD data (Sprint 17 pattern).

### 7f. P7 integration — DNS custom domain + Entra redirect URIs (2026-07-19)

Approved-to-apply @urruegg 2026-07-19 (P7 batch). Delivers §8's DNS strategy row
for `app.curavias.ch` and the Entra binding.

**7.1 Custom domain + managed TLS.** `app.curavias.ch` had no DNS record yet
(only `appsit` was live for SIT), so pointing it at the PROD app was a fresh,
zero-regression binding. Created TXT `asuid.app` = the PROD app's
`customDomainVerificationId` and CNAME `app` → the eastus2 PROD CA fqdn in zone
`curavias.ch` (rg-ihzhhpf-sit), then `az containerapp hostname add` +
`hostname bind --validation-method CNAME` on `ca-app-fluent-ihzhhpf-prod`. The
managed certificate `mc-cae-app-fluent-app-curavias-ch-6166` reached
`provisioningState=Succeeded` and is bound `SniEnabled`.

**Verified:** `https://app.curavias.ch/` returns **HTTP 200** over the managed
certificate.

**7.2 Entra redirect URIs.** The platform uses a single SPA app registration
`ihzhhpf-app` (appId `52681a08-…`) across both environments. Added the two PROD
SPA redirect URIs — `https://app.curavias.ch` and the PROD CA fqdn — via Graph
PATCH; the SPA redirect set is now 6 URIs (SIT + PROD), verified read-back.

**7.3 Logic App — skipped.** The inventory row 20 (`logic-ihzhhpf-prod`) is not
provisioned: the only Logic App is `logic-ihzhhpf-sit` (westus2) and it is
**Disabled**, so there is no active workflow to mirror. Logged as a deferred
SIT/PROD parity item (SIT parity = disabled/unused), not a demo blocker.

### 7a. Original fresh-tree plan (superseded — kept for history)

```text
infra/prod-eastus2/
├── main.bicep                  # Orchestrator
├── main.bicepparam             # PROD parameters
├── modules/
│   ├── network.bicep           # VNet + subnets + NSGs
│   ├── keyvault.bicep          # Key Vault + RBAC
│   ├── storage.bicep           # Storage account
│   ├── monitoring.bicep        # Log Analytics + App Insights
│   ├── container-registry.bicep
│   ├── container-apps.bicep    # CAE + 3 apps
│   ├── cosmos-csa.bicep        # Cosmos CSA + vector + PE
│   ├── cosmos-platform.bicep   # Cosmos Platform + PE
│   ├── eventhubs.bicep         # Event Hubs namespace
│   ├── servicebus.bicep        # Service Bus namespace
│   ├── ai-services.bicep       # AI account + project
│   ├── fabric.bicep            # Fabric capacity
│   ├── logic-apps.bicep        # Logic Apps
│   ├── identities.bicep        # 7 managed identities
│   └── private-dns.bicep       # Private DNS zones + links
└── parameters/
    └── prod.parameters.json
```

All modules follow the conventions in `.github/copilot-instructions.md` §3 (Bicep):
* Parameterised environment suffix (`-prod`)
* Tags: `env=prod`, `owner=urruegg`, `costCenter=demo`, `workload=ihzhhpf`
* Diagnostic settings → Log Analytics for every resource

---

## 8. DNS and custom domain strategy

| Domain | Target | Current | After Sprint 19 |
|--------|--------|---------|-----------------|
| `app.curavias.ch` | PROD app | Points to the eastus2 PROD CA (from prior §7f) | **Re-point** CNAME → switzerlandnorth CA FQDN |
| `appsit.curavias.ch` | SIT app | Points to westus2 CA | Unchanged (SIT stays in westus2) |
| `api.curavias.ch` | PROD API | Not assigned | CNAME → switzerlandnorth agent-host CA |

Steps:
1. Deploy Container Apps in eastus2 → get FQDN
2. Add custom domain binding on CAE
3. Request managed certificate (Let's Encrypt via Azure)
4. Update DNS zone CNAME record
5. Verify TLS handshake

---

## 9. Security and identity

| Control | Implementation |
|---------|---------------|
| Network isolation | VNet + subnets + NSGs; Cosmos/KV via PE only |
| Identity | Managed Identities for all workloads; no connection strings |
| Auth | Entra ID (AAD-only on Cosmos; RBAC on Key Vault) |
| Secrets | Key Vault RBAC mode; no local auth on any resource |
| TLS | Managed certificates on Container Apps; TLS 1.2+ enforced |
| RBAC | Least privilege per identity per resource |
| Audit | Diagnostic settings → Log Analytics; GitHub audit log for agent actions |

---

## 10. Fabric capacity and workspace

* New `fabricihzhhpfprod` capacity (F2 SKU) in **`switzerlandnorth`** — live `az`
  confirmed swn Fabric quota is **0/512 CU** (available), so PROD Fabric is now
  **co-located** with the rest of PROD in one region. This removes the westus2
  cross-region hop that §7e was forced into (eastus2 had 0 CU). Placed in the
  single PROD RG `rg-ihzhhpf-prod`; create Active then **Paused** to save cost
  (mirrors the SIT capacity posture).
* Create PROD workspace `ws-ihzhhpf-prod-data` attached to the swn capacity
* Deploy lakehouse, notebooks, semantic model from repo via the fabric-cicd
  release train (Sprint 17 / ADR-0035 pattern; re-point `environments.yml`
  region to `switzerlandnorth`)
* No data migration — run the simulator to regenerate synthetic PROD data
* **Fabric IQ Ontology + Data Agent**: Preview, per-capacity-gated (#270). SIT
  stays the live Fabric IQ seam; PROD ontology/data-agent remain deferred to
  #270, unchanged by the region pivot.

---

## 11. Side-effect posture and approval gates

| Phase | Ceiling | Gate |
|-------|---------|------|
| P1 (IaC authoring) | `write` (repo) | Normal PR review |
| P2–P6 (Azure deployment) | `deploy` | `approved-to-apply` per resource group |
| P7 (DNS cutover) | `deploy` | `approved-to-apply` + DNS propagation check |
| P8 (Verification) | `read` | No gate |

**Single approval gate for full PROD deployment:** Run `az deployment group what-if` → post output on PR → wait for `approved-to-apply` → execute `az deployment group create`.

---

## 12. Dependencies

| Dependency | Status | Impact if not met |
|------------|--------|-------------------|
| Sprint 18 complete (Foundry proven in eastus2) | ⏳ Sprint 18 in progress | Blocker — cannot proceed |
| Fabric capacity stable | ⚠️ Was paused, now resumed | May delay P6 |
| App Fluent builds green | ✅ Verified (Playwright 6/6) | — |
| Container images in ACR | ✅ Exist in SIT ACR | Push to PROD ACR or geo-replicate |
| DNS zone `curavias.ch` writable | ✅ In rg-ihzhhpf-sit (shared) | — |
| Subscription quota for switzerlandnorth | ✅ Verified 2026-07-21 (Fabric 0/512, OpenAI GA, Foundry Agent Service GA) | Blocker if not met |
| Entra app registration (PROD bindings) | ⚠️ May need PROD redirect URIs | Low effort |

---

## 13. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| R1 | Bicep deployment fails on a module | Medium | Medium | Deploy module-by-module with `what-if` first |
| R2 | DNS propagation delay for custom domain | Low | Low | Pre-validate with dig; 24h buffer |
| R3 | Fabric Git integration not available in eastus2 | Low | Medium | Fall back to REST-based publish (existing pattern) |
| R4 | Container image incompatibility | Low | Low | Same images as SIT; already tested |
| R5 | PROD Cosmos private endpoint fails | Low | High | Follow exact SIT PE pattern (proven working) |
| R6 | Cost overrun from collocated PROD | Medium | Low | All Serverless/Consumption tier; monitor weekly |

---

## 14. Definition of done

* [ ] **P0 decommission complete**: `rg-ihzhhpf-prod-eastus2` deleted,
  `fabricihzhhpfprod` (westus2) deleted, managed AppInsights RG removed; `az
  resource list` confirms **zero PROD resources in any US region**
* [ ] `infra/environments/prod-swn.bicepparam` authored (`location='switzerlandnorth'`)
  and `az bicep build-params` passes
* [ ] `az deployment group what-if` produces clean output with expected resources
* [ ] All PROD resources deployed in `rg-ihzhhpf-prod` (**switzerlandnorth**) with `Succeeded` state
* [ ] Cosmos DB accounts: AAD-only, local auth disabled, PE connected (or network-off per ADR-0013 first slice), vector search enabled
* [ ] AI Services + Foundry project (swn, GA) with 3 models deployed and 8 agents registered
* [ ] Container Apps: apps running, agent-host health check green (on swn-local ACR images)
* [ ] Custom domain `app.curavias.ch` re-pointed to the swn PROD CA with valid TLS
* [ ] Fabric capacity F2 active in **switzerlandnorth**; PROD workspace created (co-located)
* [ ] E2E demo flow: sign-in → app → agent → data → response (end-to-end green)
* [ ] PROD evidence document committed: `docs/sprints/prod-evidence-swn.md`
* [ ] All CI checks pass (markdown lint, link check, Bicep build)
* [ ] [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md) status advanced (Proposed → Accepted) once the rebuild is verified
* [ ] SIT remains functional (no breaking changes to westus2 + eastus2)

---

## 15. References

* [ADR-0037: PROD Region Pivot to Switzerland North (Greenfield)](../../adr/0037-prod-region-switzerland-north-greenfield.md)
* [ADR-0032: Foundry Control Plane in eastus2](../../adr/0032-foundry-control-plane-eastus2.md) (scoped-superseded for PROD by ADR-0037)
* [ADR-0035: Fabric IQ Layer Region westus2](../../adr/0035-fabric-iq-layer-region-westus2.md) (scoped-superseded for PROD by ADR-0037)
* [ADR-0013: Temporary US Region Demo Scope](../../adr/0013-temporary-us-region-demo-scope.md)
* [ADR-0016: No PHI in MVP Demo Scope](../../adr/0016-no-phi-in-mvp-demo-scope.md)
* [Sprint 18 Design Spec](../specs/2026-07-17-sprint-18-foundry-eastus2-control-plane-design.md)
* [Sprints 11–16 Roadmap Design](../specs/2026-07-09-sprints-11-16-roadmap-design.md)
* [SIT Evidence (2026-07-17)](../../sprints/sit-evidence-2026-07-17.md)
* [Sprint 17: Fabric Git Integration Design](../specs/2026-07-10-sprint-17-fabric-git-cicd-and-lakehouse-schema-design.md)
* [AGENTS.md](../../../AGENTS.md)
* [.github/copilot-instructions.md](../../../.github/copilot-instructions.md)
