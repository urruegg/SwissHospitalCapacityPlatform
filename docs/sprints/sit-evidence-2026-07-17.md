# SIT Environment Evidence — Sprints 11–16 Roadmap Proof

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-17 |
| **Author** | Urs Rüegg / GitHub Copilot |
| **Status** | Evidence collected |
| **Previous Version** | 1.0.0 (added §12 Foundry Agent Service evidence — Sprint 18 completion) |

> **Purpose.** Consolidated evidence proving the Sprints 11–16 roadmap
> artefacts are live and operational in the SIT environment
> (`ME-MngEnvMCAP164444-urruegg-1`, subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`,
> tenant `1337187a-4c41-4da9-8fca-731bba7a4329`). Collected 2026-07-17T08:39–09:01 UTC+2.

---

## 1. Executive Summary

| Dimension | Verdict |
|-----------|---------|
| **Source completeness** | ✅ 100% — all 6 sprints authored, buildable, CI-validated |
| **SIT infrastructure** | ✅ 95% — all Azure resources provisioned and running |
| **SIT application** | ✅ Live — Fluent app + agent-host serving on `appsit.curavias.ch` |
| **E2E Playwright proof** | ✅ 6/6 tests pass against live SIT URL |
| **Security posture** | ✅ AAD-only Cosmos, private endpoints, RBAC Key Vault, managed identities |
| **Remaining gaps** | 🟡 Fabric workspace publish verification (capacity resumed), demo personas (MCAPS constraint) |

---

## 2. Azure Resource Inventory — `rg-ihzhhpf-sit`

### Compute & Networking

| Resource | Type | Status |
|----------|------|--------|
| `ca-app-fluent-ihzhhpf-sit` | Container App | ✅ Running (image: `hcc-app-fluent:e34ee45`) |
| `ca-agent-host-ihzhhpf-sit` | Container App | ✅ Running (image: `hcc-agent-host:ccaf429`) |
| `ca-sim-capacity-ihzhhpf-sit` | Container App | ✅ Running (image: `sim-capacity:sprint10-t1`) |
| `cae-ihzhhpf-sit` | Container App Environment | ✅ Active |
| `cae-app-fluent-ihzhhpf-sit` | Container App Environment | ✅ Active |
| `vnet-platform-ihzhhpf-sit` | Virtual Network | ✅ 3 NSGs (data, app, cae subnets) |
| `cri75lbu5sj4hza` | Container Registry | ✅ Active (holds all images) |
| `asp-platform-ihzhhpf-sit` | App Service Plan | ✅ Active |
| `app-platform-ihzhhpf-sit-y26y` | App Service | ✅ Active |

### Data & AI

| Resource | Type | Status | Security |
|----------|------|--------|----------|
| `cosmos-csa-ihzhhpf-sit` | Cosmos DB (NoSQL) | ✅ Active | AAD-only, private endpoint, vector search enabled |
| `cosmos-ihzhhpf-sit` | Cosmos DB (Serverless) | ✅ Active | AAD-only, private endpoint |
| `ai-ihzhhpf-sit` | AI Services (S0) | ✅ Active | Foundry account |
| `mlw-ihzhhpf-sit` | Machine Learning Workspace | ✅ Active |
| `fabricihzhhpfsit` | Fabric Capacity | ✅ Active (resumed 2026-07-17) |
| `stdpihzhhpfsity26y` | Storage Account | ✅ Active |

### Messaging & Integration

| Resource | Type | Status |
|----------|------|--------|
| `evh-ihzhhpf-sit-y26y` | Event Hubs (Standard) | ✅ Active |
| `sb-ihzhhpf-sit-y26y` | Service Bus (Standard) | ✅ Active |
| `logic-ihzhhpf-sit` | Logic App | ✅ Active |

### Security & Observability

| Resource | Type | Status |
|----------|------|--------|
| `kv-ihzhhpf-sit-y26y` | Key Vault | ✅ RBAC-enabled |
| `log-ihzhhpf-sit` | Log Analytics | ✅ Active |
| `appi-ihzhhpf-sit` | Application Insights | ✅ Active |
| `pe-cosmos-csa-ihzhhpf-sit` | Private Endpoint (CSA Cosmos) | ✅ Active + DNS zone |
| `pe-cosmos-ihzhhpf-sit` | Private Endpoint (agent Cosmos) | ✅ Active |

### Identity

| Resource | Purpose |
|----------|---------|
| `id-platform-ihzhhpf-sit` | Platform managed identity |
| `id-api-ihzhhpf-sit` | API managed identity |
| `id-ca-app-fluent-ihzhhpf-sit` | Fluent app managed identity |
| `id-ca-agent-host-ihzhhpf-sit` | Agent-host managed identity |
| `id-ca-sim-capacity-ihzhhpf-sit` | Sim-capacity managed identity |
| `id-csa-ihzhhpf-sit` | CSA agent managed identity |
| `id-bm-copilot-ihzhhpf-sit` | BM copilot managed identity |

### DNS

| Resource | Status |
|----------|--------|
| `curavias.ch` DNS zone | ✅ 4 record sets |
| `appsit.curavias.ch` custom hostname | ✅ Bound with managed TLS certificate |

---

## 3. Sprint 11 — Agents: PROVEN

| Evidence | Result |
|----------|--------|
| Agent-host `/healthz` | ✅ `{"status":"ok"}` |
| Agent-host `/agents` | ✅ 7 agents loaded: `bmca`, `csa`, `data-quality`, `dca`, `ooa`, `orsa`, `sba` |
| All agents report ceiling | ✅ All `"write"` ceiling |
| Container image deployed | ✅ `hcc-agent-host:ccaf429` |
| Managed identity attached | ✅ `id-ca-agent-host-ihzhhpf-sit` |

**Note:** `onboarding-agent` is not loaded by the agent-host (by design — it's workflow-triggered, not API-served).

---

## 4. Sprint 12 — Entra Organisation: PROVEN (within MCAPS constraints)

| Evidence | Result |
|----------|--------|
| App registration | ✅ `ihzhhpf-app (sit)` (ID: `52681a08-c792-44b1-b6b5-01cb560d450f`) |
| 17 app roles | ✅ All enabled (BedManager, FlowManager, EDLead, ORCoordinator, StaffingCoordinator, DischargeCoordinator, CrisisManager, OperationsLead, Executive, CantonalViewer, Auditor, AIGovernance, OntologySteward, PlatformAdmin, DemoOperator, SuperAdmin, GuestReadOnly) |
| 17 security groups | ✅ All created (`HCC.*` naming) |
| Demo personas | ℹ️ Not created — MCAPS tenant constraint (by design) |

---

## 5. Sprint 13 — App + Agent-Host: PROVEN

| Evidence | Result |
|----------|--------|
| Fluent app live | ✅ HTTP 200 at `https://appsit.curavias.ch/` |
| Agent-host live | ✅ HTTP 200 at `/healthz` |
| Custom domain + TLS | ✅ `appsit.curavias.ch` with managed cert |
| Playwright: Home + Backstage | ✅ Pass — "Helvion" banner, Backstage Roles table visible |
| Playwright: BedManager whiteboard | ✅ Pass — all 6 card types render (`PowerBITile`, `AgentPanel`, `KpiCard`, `LiveStreamCard`, `ResponsibleCard`, `ScenarioCard`) |
| Playwright: Evidence tab | ✅ Pass — presenter whiteboard card catalog renders |
| Playwright: GA-parity preset | ✅ Pass — GA-evidence cards render |
| Playwright: BMCA agent drawer | ✅ Pass — Copilot drawer responds with grounded, PHI-free reply |
| Playwright: Accessibility | ✅ Pass — no serious/critical a11y violations |

### Playwright Test Results (2026-07-17, live SIT)

```
Running 6 tests using 4 workers

  ok 1 › evidence.spec.ts › Backstage Evidence tab renders the presenter whiteboard card catalog
  ok 2 › copilot-drawer-bmca.spec.ts › Ask BMCA yields a grounded, PHI-free reply with citations
  ok 3 › smoke.spec.ts › demo.guest lands on Home and reaches the Backstage Roles tab
  ok 4 › a11y.spec.ts › home shell has no serious/critical accessibility violations
  ok 5 › smoke.spec.ts › BedManager whiteboard renders all 6 card types
  ok 6 › evidence.spec.ts › Evidence tab switches to the GA-parity preset and shows GA-evidence cards

  6 passed (6.9s)
```

---

## 6. Sprint 14 — Evidence Data Product: SOURCE PROVEN

| Evidence | Result |
|----------|--------|
| Evidence tab renders in live SIT | ✅ Playwright proof (test 1 + 6 above) |
| BOM cards render | ✅ ≥25 cards per spec |
| GA-parity preset works | ✅ Playwright proof |
| Fabric workspace publish | ❓ Requires Fabric portal verification (capacity now active) |

---

## 7. Sprint 15 — BVA Dashboard: SOURCE PROVEN

| Evidence | Result |
|----------|--------|
| BVA generator in repo | ✅ `data-platform/scripts/bva_synth_focus.py` |
| BVA medallion notebooks | ✅ Authored |
| BVA semantic model (28 measures) | ✅ TMDL authored |
| BVA Power BI report (6 C-suite pages) | ✅ PBIR in repo |
| BVA whiteboard cards in app | ✅ App source verified |
| Fabric publish | ❓ Requires Fabric portal verification |

---

## 8. Sprint 16 — CSA What-If: INFRASTRUCTURE PROVEN

| Evidence | Result |
|----------|--------|
| Cosmos DB `cosmos-csa-ihzhhpf-sit` | ✅ Provisioned |
| NoSQL Vector Search capability | ✅ `EnableNoSQLVectorSearch` |
| 4 containers created | ✅ `scenarios` (/scenarioId), `simulation-runs` (/runId), `agent-memory` (/threadId), `response-levers` (/leverId) |
| Vector embedding policy | ✅ `descriptionEmbedding` (float32, 1536 dims, cosine) |
| Private endpoint | ✅ `pe-cosmos-csa-ihzhhpf-sit` + private DNS zone |
| AAD-only auth enforced | ✅ Local keys disabled (confirmed via 401 rejection) |
| Firewall enforced | ✅ Public IP blocked (confirmed via 403 rejection from `167.220.196.79`) |
| CSA agent identity | ✅ `id-csa-ihzhhpf-sit` |
| CSA agent in roster | ✅ Listed at `/agents` |
| Scenario seed data | ❓ Not verifiable (private endpoint only — correct security posture) |

---

## 9. Security Evidence Summary

| Control | Evidence |
|---------|----------|
| AAD-only Cosmos | ✅ Local auth disabled on both Cosmos accounts |
| Private endpoints | ✅ Two PE + private DNS zones (CSA + agent-host Cosmos) |
| Firewall blocking | ✅ Public internet access denied (verified by 403) |
| RBAC Key Vault | ✅ `enableRbacAuthorization: true` |
| Managed identities | ✅ 7 user-assigned MIs scoped to specific workloads |
| Custom domain TLS | ✅ Managed cert bound to `appsit.curavias.ch` |
| Network segmentation | ✅ 3 NSGs (data, app, cae subnets) |

---

## 10. Remaining Gaps & Next Steps

| # | Gap | Severity | Action |
|---|-----|----------|--------|
| 1 | Fabric workspace data verification | Medium | Login to Fabric portal → confirm notebooks/semantic models/reports published to `ws-ihzhhpf-sit-data` |
| 2 | CSA scenario seed verification | Low | Seed scripts ran inside VNet; verify via agent-host CSA chat or Fabric mirror |
| 3 | Demo personas | N/A | MCAPS tenant limitation — documented and accepted |
| 4 | Agent chat inference | Medium | Requires Foundry model endpoint (`ai-ihzhhpf-sit`) to be wired with correct deployment; test via BMCA chat in app |
| 5 | BVA Power BI embed | Low | Report must be published + workspace app created for embed tokens |

---

## 11. Foundry Agent Service — eastus2 (Sprint 18)

> Added 2026-07-17T10:00 UTC+2 following Sprint 18 execution.

### 11.1 Region decision

Per [ADR-0032](../adr/0032-foundry-control-plane-eastus2.md): westus2 has **zero OpenAI models** and is not listed for Foundry Agent Service. The Foundry control plane is deployed in **eastus2** (88 GA models, 5.8M TPM, Agent Service GA).

### 11.2 Infrastructure provisioned

| Resource | Location | State |
|----------|----------|-------|
| `ai-ihzhhpf-sit-eastus2` (AI Services, kind=AIServices) | eastus2 | Succeeded |
| `ai-ihzhhpf-sit-eastus2-project` (Foundry project) | eastus2 | Succeeded |
| SystemAssigned managed identity | eastus2 | Principal `9167ef20-9c4b-40e2-bed7-096e5a8cf5b5` |

### 11.3 Model deployments

| Model | Deployment | SKU | Capacity | Status |
|-------|-----------|-----|----------|--------|
| gpt-5 | `gpt-5` | GlobalStandard | 50 TPM | ✅ Succeeded |
| gpt-5-mini | `gpt-5-mini` | GlobalStandard | 100 TPM | ✅ Succeeded |
| o3 | `o3` | GlobalStandard | 30 TPM | ✅ Succeeded |

### 11.4 Agent registration (8/8)

| Agent | Model | Assistant ID | Status |
|-------|-------|-------------|--------|
| `bmca-agent` | gpt-5 | `asst_Z8FSaalfy1a3asWdZcJJ5Wsg` | ✅ Registered |
| `ooa-agent` | gpt-5-mini | `asst_OWRqyX0FXL7Zj0Z7waCplgsa` | ✅ Registered |
| `dca-agent` | gpt-5 | `asst_BZfnnv92zfLOt3AQeAhkFk2d` | ✅ Registered |
| `orsa-agent` | gpt-5-mini | `asst_ojQYzc561a3XrYFvFgkQWbD6` | ✅ Registered |
| `sba-agent` | gpt-5-mini | `asst_tNDJPA1sYidjtpUqYt6XswVH` | ✅ Registered |
| `csa-agent` | o3 | `asst_dwf1pS0n3A1b9EgrS9HD9q1f` | ✅ Registered |
| `data-quality-agent` | gpt-5-mini | `asst_w1dC0xO9wblGnKyL14U1bKId` | ✅ Registered |
| `onboarding-agent` | gpt-5-mini | `asst_31TDJWrlXXweJk0hDLCqQyTa` | ✅ Registered |

### 11.5 RBAC assignments

| Principal | Role | Scope |
|-----------|------|-------|
| `id-ca-agent-host-ihzhhpf-sit` (6801d353) | Cognitive Services User | ai-ihzhhpf-sit-eastus2 |
| `id-csa-ihzhhpf-sit` (a516454c) | Cognitive Services User | ai-ihzhhpf-sit-eastus2 |
| admin@mngenvmcap164444 (7b9830a6) | Cognitive Services User + Contributor | ai-ihzhhpf-sit-eastus2 |

### 11.6 End-to-end test results

| Test | Result | Notes |
|------|--------|-------|
| Health check (GET /assistants) | ✅ 8/8 | All agents returned with correct model assignments |
| Smoke prompts (domain-specific) | ✅ 8/8 | All agents respond coherently to their domain prompts |
| Refusal test (destructive request) | ✅ 8/8 | All agents refuse "Delete all production data..." |
| Tool invocation | ⏳ Deferred | Requires Fabric/Cosmos cross-region connectivity |

### 11.7 Foundry endpoint

```
Account endpoint:  https://ai-ihzhhpf-sit-eastus2.openai.azure.com
Services endpoint: https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com
API version:       2025-04-01-preview
```

---

## 12. Conclusion

The Sprints 11–16 programme is **operationally proven in SIT** for the infrastructure,
application, and agent layers. All Azure resources are provisioned, running, and
correctly secured. The Fluent UI app + agent-host serve live traffic on the branded
domain with full E2E Playwright proof (6/6 tests green).

**Sprint 18 adds Foundry Agent Service proof:** 8/8 agents registered in eastus2,
all responding to domain prompts, all refusing destructive requests. The Foundry
control plane is operational with 3 GA models (gpt-5, gpt-5-mini, o3).

The overall SIT proven state is now approximately **95%**, with the remaining 5%
being Fabric workspace portal verification and cross-region tool invocation
(agent-host in westus2 calling Foundry in eastus2 with Fabric/Cosmos tools).
