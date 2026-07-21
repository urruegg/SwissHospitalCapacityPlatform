# Sprint 19 — PROD Region Pivot to Switzerland North (Greenfield) — Implementation Plan

| Field | Value |
|-------|-------|
| **Version** | 2.0.0 |
| **Date** | 2026-07-21 |
| **Author** | Urs Rüegg |
| **Status** | Accepted (region pivot) — Phase 0 decommission + Switzerland North greenfield rebuild pending `approved-to-apply`; the eastus2/westus2 execution records below are the decommission target |
| **Previous Version** | 1.6.0 (P7 execution record — `app.curavias.ch` custom domain + managed cert, PROD Entra SPA redirect URIs, Logic App skip). 2.0.0 is a **MAJOR** bump reversing the eastus2/westus2 PROD region decision per [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md); PROD is decommissioned (DR-style) and rebuilt greenfield in `switzerlandnorth` at SIT parity. |
| **Design spec** | [2026-07-17-sprint-19-prod-eastus2-full-deployment-design.md](../specs/2026-07-17-sprint-19-prod-eastus2-full-deployment-design.md) |

---

> ## ⚠️ Region pivot (2026-07-21) — read the design spec §0 pivot notice first
>
> Per [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md), PROD
> moves from split US regions (eastus2 Foundry + westus2 Fabric) to a
> **single-region `switzerlandnorth` greenfield** at SIT parity, executed
> **DR-style**: **Phase 0 decommissions the whole eastus2/westus2 PROD footprint
> first**, then the rebuild replays the proven Option-1 flow (reuse
> `infra/main.bicep`) with `location='switzerlandnorth'`. The "Execution record"
> sections below (P1–P7) document the **now-decommissioned** eastus2/westus2
> build and are kept as the audit trail. For the rebuild, substitute
> `eastus2`/`westus2` → `switzerlandnorth` and `rg-ihzhhpf-prod-eastus2` →
> `rg-ihzhhpf-prod`. **SIT (westus2 + eastus2) is untouched.**

---

## Phase 0 — DR-style decommission (runs first, `approved-to-apply`-gated)

Tear down the entire prior PROD footprint so the rebuild starts from a clean
single-region slate. **Verify each deletion; SIT resource groups
(`rg-ihzhhpf-sit`) must be excluded from every command.**

```bash
# T0a — delete the eastus2 PROD resource group (~22 resources: Foundry account
# + project, Container Apps x2 + CAEs, Cosmos x2, Event Hubs, Service Bus,
# Key Vault, ACR crihzhhpfprod, Log/AppInsights, VNet + NSGs, identities)
az group delete --name rg-ihzhhpf-prod-eastus2 --yes

# T0b — delete the westus2 PROD Fabric capacity
az resource delete --name fabricihzhhpfprod \
  --resource-type Microsoft.Fabric/capacities -g rg-ihzhhpf-prod-eastus2
#   (if the RG is already gone, target by full resourceId before T0a)

# T0c — confirm clean slate: zero PROD resources in any US region
az resource list --query "[?resourceGroup=='rg-ihzhhpf-prod-eastus2']" -o tsv
az group list --query "[?starts_with(name,'rg-ihzhhpf-prod')].name" -o tsv
```

Notes:

- The purge-protected Key Vault from the earlier westus2 teardown
  (`kv-ihzhhpf-prod-i62t`) auto-expires 2026-10-16 — non-blocking, the swn
  rebuild uses a distinct KV name.
- Foundry account soft-delete: purge `ai-ihzhhpf-prod` after RG deletion so the
  name is reusable in swn (`az cognitiveservices account purge`).
- Managed App Insights RG (auto-created) is removed with its parent; verify.

---

---

> **The four "Execution record" sections below (P1–P7) are the history of the
> now-decommissioned eastus2/westus2 PROD build (Phase 0 target).** They are kept
> verbatim as the audit trail. The swn rebuild replays the same steps with
> `location='switzerlandnorth'`.

## Execution record — P1–P3 (2026-07-19)

> Supersedes the fresh-tree command examples below. Actual execution used
> **Option 1**: the existing `infra/main.bicep` driven by
> `infra/environments/prod-eastus2.bicepparam` (no `infra/prod-eastus2/` tree).

**Approved-to-apply**: @urruegg 2026-07-19T00:53 +02:00.

**Deployment**: `az deployment group create -n sprint19-prod-eastus2-p1 -g
rg-ihzhhpf-prod-eastus2 -f infra/main.bicep -p
infra/environments/prod-eastus2.bicepparam` — Succeeded in 2m26s
(2026-07-19T05:37Z).

**First attempt failed** on two shared-module limitations, both fixed:

1. **Cross-RG ACR unsupported** — the Container App module references the
   registry *by name in the deployment RG* (`existing`, no cross-RG scope), so
   cross-region pull from the SIT ACR returned `ResourceNotFound`. Fix: created
   a **PROD-local ACR `crihzhhpfprod`** and `az acr import`ed both images
   (`hcc-agent-host:b796961`, `hcc-app-fluent:b796961`) from the SIT ACR.
2. **Cosmos private endpoint** needs the `privatelink.documents.azure.com` zone
   that only the CSA-Cosmos module creates. Fix: `enableNetworkModule=false`
   for this slice → public CAEs + public Cosmos (synthetic data, no PHI per
   ADR-0013 — parity with how SIT ran for months). VNet + private-endpoint is a
   hardening follow-up.

The two half-created CAEs + the orphaned Cosmos PE were deleted before the
clean redeploy.

**Deployed & verified (17 resources)**:

| Layer | Resources |
|-------|-----------|
| Foundation | `vnet-platform-ihzhhpf-prod` (+3 NSGs, unused while network off), `log-ihzhhpf-prod`, `appi-ihzhhpf-prod`, `kv-ihzhhpf-prod-q4nk`, `id-platform-ihzhhpf-prod` |
| AI platform | `ai-ihzhhpf-prod` (Foundry/Cognitive account) |
| Registry | `crihzhhpfprod` (PROD-local ACR, 2 images) |
| Compute | `cae-ihzhhpf-prod` + `ca-agent-host-ihzhhpf-prod` + `id-ca-agent-host-…`; `cae-app-fluent-ihzhhpf-prod` + `ca-app-fluent-ihzhhpf-prod` + `id-ca-app-fluent-…` |
| Data | `cosmos-ihzhhpf-prod` → db `agenthost` → `conversations` / `audit` / `approval-events` |

**Live-health evidence**: agent-host `/healthz` → `{"status":"ok"}`, `/agents`
→ 200; app-fluent `/` → 200; both Container Apps `runningStatus=Running` on the
PROD-ACR images. Commits `6d31559` (param) + `0913b02` (ACR + network-off fix).

**Deferred to later phases**: Redis (eastus2 Balanced SKU unverified — in-memory
per ADR-0028), P5 Foundry-hosted agents (Sprint 18 API pattern against the PROD
project), P6 Fabric F2 workspace + Data Agent, P7 DNS cutover `app.curavias.ch`,
VNet + private-endpoint hardening.

---

## Execution record — P4 data lane, deployed via CI/CD (2026-07-19)

> First PROD slice deployed through the **`cd-infra-deploy-prod` GitHub
> workflow** rather than a local `az` command — deliberately, to prove the
> CI/CD infra path works end-to-end (policy gate → OIDC → what-if → deploy).

**Prerequisite — #252 Phase A (CSA Cosmos parity):** the CSA Cosmos account was
previously an out-of-band standalone deploy (not in `main.bicep`, invisible to
CI what-if — logged as [#252](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/252)).
Phase A wired it in: `enableCsaCosmosModule` gate + a `csaCosmos` block calling
`modules/cosmos/csa.bicep`, an `agentHostMiPrincipalId` output on the agent-host
module, and a pinned `publicNetworkAccess` in `csa.bicep`. Enabled in both
`sit.bicepparam` (idempotent adoption — SIT what-if showed **0 Create / 0
Delete**) and `prod-eastus2.bicepparam` (which also flips on EVH + SB for P4).
Commit `a0eeda1`.

**CI/CD finding — stale `prod` environment variables:** the GitHub `prod`
environment still pointed at the decommissioned westus2 footprint
(`rg-ihzhhpf-prod`, `prod.bicepparam`, `westus2`). Corrected the three infra
vars to `rg-ihzhhpf-prod-eastus2` / `prod-eastus2.bicepparam` / `eastus2`.
(Broader staleness — `SOLUTION_SHORT_NAME`, `PROD_SOURCE_SQL_*`,
`PROD_FABRIC_*` still reference the frozen old tenant `mngenvmcap228255` — noted
on #252 for a follow-up sweep.)

**Approved-to-apply**: @urruegg 2026-07-19 (PROD what-if **12 Create / 0
Delete**). Workflow run `29679485559` — policy-gate PASSED, `Deploy PROD`
job approved at the `prod` required-reviewer gate, deploy green in 5m8s
(what-if + `az deployment group create`).

**Deployed & verified (12 resources)**:

| Resource | Evidence |
|----------|----------|
| `cosmos-csa-ihzhhpf-prod` | db `csa` + 4 containers: `scenarios`, `agent-memory`, `response-levers`, `simulation-runs` |
| `evh-ihzhhpf-prod-q4nk` | Event Hubs namespace + hub `events` + `$Default` + consumer groups `cg-bm-copilot-agent`, `cg-csa-agent`, `cg-fabric-eventstream` |
| `sb-ihzhhpf-prod-q4nk` | Service Bus namespace — status Active |

**Policy note (publicNetworkAccess):** the template requested `Enabled`
(network off), but both `cosmos-csa-ihzhhpf-prod` **and** the platform
`cosmos-ihzhhpf-prod` show `publicNetworkAccess=Disabled` live. The MCAPSGov
governance policy is therefore a **Modify-effect** that force-disables public
Cosmos across the subscription — the deploy still succeeds, but the accounts are
unreachable without a private endpoint. Runtime reachability of CSA Cosmos in
PROD is folded into the **VNet + private-endpoint hardening** follow-up
(consistent with ADR-0013 synthetic-only, network-off first slice). Resource
*provisioning* (the P4 goal) is complete.

**Still deferred:** P5 Foundry-hosted agents, P6 Fabric F2 workspace + Data
Agent, P7 DNS cutover, VNet/PE hardening, #252 Phase B (ACR module + CD import)
and Phase C (SIT/PROD parity assertion).

---

## Execution record — P5 Foundry agents (2026-07-19)

**Approved-to-apply**: @urruegg 2026-07-19 10:47 +02:00. Followed the proven
Sprint 18 pattern (az + Foundry data-plane API) against the PROD account
`ai-ihzhhpf-prod` — models/project/agents are **not** Bicep-managed, so this is
script/API-based rather than the infra CD workflow.

**IaC finding — `allowProjectManagement`.** Project create first failed
`BadRequest: Project can only [be] created under AIServices Kind account with
allowProjectManagement set to true`. The `modules/ai-platform/main.bicep`
module does not set this property; SIT had it set out-of-band. Fixed with a
`PATCH` on the account (`properties.allowProjectManagement=true`) and logged on
[#252](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/252) as
a Bicep parity gap (the module should set it declaratively).

**Deployed & verified:**

| Step | Evidence |
|------|----------|
| Foundry project | `ai-ihzhhpf-prod-project` — provisioningState `Succeeded`, SystemAssigned identity |
| Models (3) | `gpt-5` (2025-08-07, GS 50), `gpt-5-mini` (2025-08-07, GS 100), `o3` (2025-04-16, GS 30) — all `Succeeded`; eastus2 quota headroom confirmed (50/100/0 of 1000 used pre-deploy) |
| RBAC | `id-ca-agent-host-ihzhhpf-prod` (`af610e05…`) → **Cognitive Services User** on `ai-ihzhhpf-prod` |
| Agents (8) | Registered via the Foundry v2 persistent-agents API (`/agents`, `definition.kind=prompt`), replicated from the SIT v2 definitions. All 8 present; model assignments cross-checked **OK** vs SIT (bmca/dca/ooa=gpt-5, csa=o3, orsa/sba/data-quality/onboarding=gpt-5-mini) |

**API note:** the v2 persistent-agents `/agents` API (api-version
`2025-05-15-preview`) requires a `definition` wrapper (`kind: prompt`, `model`,
`instructions`) — distinct from the classic OpenAI Assistants (`asst_*`) shape.
Live-inference E2E runs through the agent-host `azure-ai-projects` SDK path and
is deferred to **P8/T9** (same invocation path as SIT), not the raw
`threads/runs` API.

**Still deferred:** P6.2 workspace + content, P7 DNS cutover,
VNet/PE hardening, P8 E2E agent invocation, #252 Phases B/C/D.

---

## Execution record — P6.1 Fabric capacity (2026-07-19)

**Approved-to-apply**: @urruegg 2026-07-19 11:29 +02:00.

**Blocker → decision — eastus2 Fabric quota = 0.** The eastus2 create failed
`BadRequest … RegionalQuota: 0`. The `Microsoft.Fabric` usages API confirms
**0 CU** quota in eastus2 vs **512 CU** in westus2 (2 CU used by the SIT F2).
Per user decision, PROD Fabric is placed in **westus2** (region-flexible SaaS
plane, reachable cross-region over HTTPS, ADR-0013 demo scope). All-eastus2
would need an eastus2 Fabric quota-increase request (deferred).

**Verified:** `fabricihzhhpfprod` — F2/Fabric, **westus2**, in
`rg-ihzhhpf-prod-eastus2`, admin `admin@mngenvmcap164444.onmicrosoft.com`;
created Active (`Succeeded`) then **suspended** → `state=Paused` (cost-saving,
mirrors SIT). Design §10 + §5 inventory updated to westus2.

**P6.2 (dedicated slice):** workspace `ws-ihzhhpf-prod-data` + Git-connect +
lakehouse/notebooks/semantic-model deploy + simulator run.

---

## Execution record — P7 integration (DNS + custom domain + Entra) (2026-07-19)

**Approved-to-apply**: @urruegg 2026-07-19 (P7 batch).

**7.1 Custom domain + TLS — `app.curavias.ch` → PROD app-fluent.** The apex
domain had **no `app` record** yet (only `appsit` for SIT), so the cutover was a
fresh binding with zero regression to the running SIT demo. Steps executed:

1. TXT `asuid.app` = the PROD app's `customDomainVerificationId`
   (`98440D26…48AB`) in zone `curavias.ch` (rg-ihzhhpf-sit).
2. CNAME `app` → `ca-app-fluent-ihzhhpf-prod.thankfulisland-9e831bdb.eastus2.azurecontainerapps.io`.
3. `az containerapp hostname add` + `hostname bind --validation-method CNAME` on
   `ca-app-fluent-ihzhhpf-prod` → managed cert
   `mc-cae-app-fluent-app-curavias-ch-6166` (`provisioningState=Succeeded`),
   bound `SniEnabled`.

**Verified live:** `https://app.curavias.ch/` → **HTTP 200** with valid managed
TLS.

**7.2 Entra redirect URIs.** Added the two PROD origins to the single SPA app
registration `ihzhhpf-app` (appId `52681a08-…`):
`https://app.curavias.ch` and the PROD CA fqdn. SPA redirect set now 6 URIs
(SIT + PROD). Verified via `az ad app show`.

**7.3 Logic App — skipped.** The only Logic App is `logic-ihzhhpf-sit`
(westus2) and it is **Disabled** (no active workflow), so `logic-ihzhhpf-prod`
is **not** created. Logged as a deferred SIT/PROD parity item (SIT parity =
disabled/unused).

---

## Execution phases

> **Region substitution for the Switzerland North rebuild.** The command
> examples below were authored for eastus2. For the swn rebuild, run **Phase 0
> (decommission) first**, then apply these with: `location`/region →
> `switzerlandnorth`; `rg-ihzhhpf-prod-eastus2` → `rg-ihzhhpf-prod`;
> param file → `infra/environments/prod-swn.bicepparam`; the Foundry project
> endpoint host → `ai-ihzhhpf-prod.services.ai.azure.com`; **Fabric capacity
> creates in `switzerlandnorth`** (quota 0/512 — drop the westus2 special-case
> from §6.1). Everything else (Option-1 reuse of `infra/main.bicep`, PROD-local
> ACR `az acr import`, network-off first slice, Foundry v2 `/agents` API,
> DNS/Entra binding) is identical.

### Phase 1 — IaC Authoring (T1)

#### 1.1 Scaffold Bicep modules

Create `infra/prod-eastus2/` with the module structure defined in Design §7:

```bash
mkdir -p infra/prod-eastus2/modules infra/prod-eastus2/parameters
```

Each module follows:
- Input: environment name (`prod`), location (`eastus2`), resource name pattern
- Output: resource IDs for cross-module references
- Tags: `env=prod`, `owner=urruegg`, `costCenter=demo`, `workload=ihzhhpf`
- Diagnostic settings where applicable

#### 1.2 Author main.bicep orchestrator

```bicep
targetScope = 'resourceGroup'

param environment string = 'prod'
param location string = 'eastus2'
param solutionShortName string = 'ihzhhpf'

// Module invocations in dependency order:
// 1. identities → 2. network → 3. keyvault → 4. storage → 5. monitoring
// 6. container-registry → 7. cosmos-csa → 8. cosmos-platform
// 9. eventhubs → 10. servicebus → 11. container-apps
// 12. ai-services → 13. fabric → 14. logic-apps → 15. private-dns
```

#### 1.3 Author parameters file

```json
{
  "environment": { "value": "prod" },
  "location": { "value": "eastus2" },
  "solutionShortName": { "value": "ihzhhpf" },
  "fabricSkuName": { "value": "F2" },
  "cosmosDbConsistency": { "value": "Session" },
  "containerRegistrySku": { "value": "Basic" }
}
```

### Phase 2 — Foundation Deployment (T2–T6)

#### 2.1 Create resource group

```bash
az group create --name rg-ihzhhpf-prod-eastus2 --location eastus2 \
  --tags env=prod owner=urruegg costCenter=demo workload=ihzhhpf
```

#### 2.2 Deploy foundation modules

```bash
az deployment group what-if \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --template-file infra/prod-eastus2/main.bicep \
  --parameters infra/prod-eastus2/parameters/prod.parameters.json \
  --mode Incremental
```

Wait for `approved-to-apply`, then:

```bash
az deployment group create \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --template-file infra/prod-eastus2/main.bicep \
  --parameters infra/prod-eastus2/parameters/prod.parameters.json \
  --mode Incremental
```

### Phase 3 — Compute Layer (T7)

#### 3.1 Push container images to PROD ACR

```bash
# Option A: geo-replicate existing ACR
az acr replication create --registry cri75lbu5sj4hza --location eastus2

# Option B: create new PROD ACR and push
az acr create --name crihzhhpfprod --resource-group rg-ihzhhpf-prod-eastus2 \
  --location eastus2 --sku Basic --admin-enabled false

# Push images
az acr import --name crihzhhpfprod \
  --source cri75lbu5sj4hza.azurecr.io/agent-host:latest \
  --image agent-host:latest
az acr import --name crihzhhpfprod \
  --source cri75lbu5sj4hza.azurecr.io/app-fluent:latest \
  --image app-fluent:latest
az acr import --name crihzhhpfprod \
  --source cri75lbu5sj4hza.azurecr.io/sim-capacity:latest \
  --image sim-capacity:latest
```

#### 3.2 Verify Container Apps health

```bash
# Agent-host health
curl -s https://ca-agent-host-ihzhhpf-prod.<region>.azurecontainerapps.io/health

# App Fluent (after DNS)
curl -s https://ca-app-fluent-ihzhhpf-prod.<region>.azurecontainerapps.io/
```

### Phase 4 — Data Layer (T8–T10, T15)

#### 4.1 Verify Cosmos DB configuration

```bash
# Cosmos CSA: AAD-only, vector search, PE
az cosmosdb show --name cosmos-csa-ihzhhpf-prod \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --query "{localAuth:disableLocalAuth, vectorSearch:capabilities}"

# Verify private endpoint connectivity
az network private-endpoint show --name pe-cosmos-csa-ihzhhpf-prod \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --query "privateLinkServiceConnections[0].privateLinkServiceConnectionState.status"
```

#### 4.2 Seed CSA containers

Run the CSA seed notebook to create the 4 containers with vector embedding policies:
- `scenarios` (partition: `/scenarioId`)
- `simulation-runs` (partition: `/runId`)
- `agent-memory` (partition: `/threadId`)
- `response-levers` (partition: `/leverId`)

### Phase 5 — AI/Foundry Layer (T11–T13)

#### 5.1 Deploy models

Follow Sprint 18 pattern (already proven):
- gpt-5: GlobalStandard, 50 TPM
- gpt-5-mini: GlobalStandard, 100 TPM
- o3: GlobalStandard, 30 TPM

#### 5.2 Register 8 agents

Same registration flow as Sprint 18 but targeting PROD project endpoint:

```text
https://ai-ihzhhpf-prod-eastus2.services.ai.azure.com/api/projects/ai-ihzhhpf-prod-eastus2-project/assistants
```

### Phase 6 — Fabric (T16)

#### 6.1 Create PROD Fabric capacity

```bash
az rest --method PUT \
  --url "https://management.azure.com/subscriptions/.../resourceGroups/rg-ihzhhpf-prod-eastus2/providers/Microsoft.Fabric/capacities/fabricihzhhpfprod?api-version=2023-11-01" \
  --body '{"location":"eastus2","sku":{"name":"F2","tier":"Fabric"},"properties":{"administration":{"members":["admin@mngenvmcap164444.onmicrosoft.com"]}}}'
```

#### 6.2 Create PROD workspace and connect

- Create `ws-ihzhhpf-prod-data` workspace
- Assign to `fabricihzhhpfprod` capacity
- Connect via Fabric Git integration (Sprint 17 pattern) or REST publish

### Phase 7 — Integration (T17–T19)

#### 7.1 DNS cutover for PROD

```bash
# Add custom domain binding
az containerapp hostname add --name ca-app-fluent-ihzhhpf-prod \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --hostname app.curavias.ch

# Bind managed certificate
az containerapp hostname bind --name ca-app-fluent-ihzhhpf-prod \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --hostname app.curavias.ch \
  --environment cae-ihzhhpf-prod

# Update DNS
az network dns record-set cname set-record \
  --resource-group rg-ihzhhpf-sit \
  --zone-name curavias.ch \
  --record-set-name app \
  --cname ca-app-fluent-ihzhhpf-prod.<region>.azurecontainerapps.io
```

#### 7.2 Entra PROD bindings

- Add PROD redirect URIs to existing app registration
- Verify MSAL authentication flow against PROD endpoints

### Phase 8 — End-to-End Verification (T20–T22)

#### 8.1 Full demo flow test

1. Navigate to `app.curavias.ch` → verify TLS + login page
2. Sign in as demo persona → verify role-based view
3. Invoke `bmca-agent` via Copilot drawer → verify response
4. Query Fabric Gold table via semantic model → verify data
5. Open CSA wizard → verify scenario creation in Cosmos
6. Check agent-host `/agents` endpoint → verify 7 agents loaded

#### 8.2 Produce PROD evidence document

```text
docs/sprints/prod-evidence-eastus2.md
```

Contents:
- Resource inventory (all 25 resources with provisioningState)
- Model deployment confirmations
- Agent registration proof
- E2E test results
- Security posture verification (PE, AAD-only, TLS)
- Bicep deployment output

---

## Validation checklist (pre-merge)

```bash
# Bicep build
az bicep build --file infra/prod-eastus2/main.bicep

# Markdown lint
npx --yes markdownlint-cli2 "docs/**/*.md" "infra/**/*.md" "#node_modules"

# Link check
npx --yes markdown-link-check docs/sprints/prod-evidence-eastus2.md

# Resource verification
az resource list --resource-group rg-ihzhhpf-prod-eastus2 \
  --query "length(@)" -o tsv
# Expected: ≥ 25
```

---

## Sprint close criteria

All items from [Design Spec §14 (Definition of Done)](../specs/2026-07-17-sprint-19-prod-eastus2-full-deployment-design.md#14-definition-of-done) verified green.
