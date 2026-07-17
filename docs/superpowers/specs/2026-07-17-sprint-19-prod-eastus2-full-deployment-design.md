# Sprint 19 — Full PROD Deployment in eastus2 (Fresh from Scratch) — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-17 |
| **Author** | Urs Rüeegg |
| **Status** | Draft for review |
| **Previous Version** | n/a (new — Sprint 19 kickoff) |
| **Anchor triggers** | Sprint 18 completion (Foundry control plane proven in eastus2); SIT feasibility matrix confirming 22/22 resource types GA in eastus2; ADR-0013 demo-scope pivot |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution; Bicep-first IaC for all PROD resources |
| **Prerequisites** | Sprint 18 complete (Foundry agents proven E2E in eastus2); Fabric capacity stabilized; App Fluent builds green |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and rationale](#2-context-and-rationale)
3. [Scope](#3-scope)
4. [Architecture — PROD target state](#4-architecture--prod-target-state)
5. [Resource inventory (PROD eastus2)](#5-resource-inventory-prod-eastus2)
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

Deploy the **entire PROD environment from scratch in eastus2** — all resources collocated in a single region, eliminating cross-region latency, simplifying network topology, and unlocking full Foundry Agent Service capability.

**Desired end state:**

* `rg-ihzhhpf-prod-eastus2` resource group with all platform resources deployed via Bicep.
* Full stack: Container Apps (agent-host + app-fluent + sim), Cosmos DB (CSA + platform), Event Hubs, Service Bus, Key Vault, VNet + private endpoints, AI Services + Foundry project, Fabric capacity, Storage, Log Analytics, Application Insights, Logic Apps, Container Registry.
* All 8 agents registered and functional in PROD Foundry project.
* Custom domain `app.curavias.ch` (PROD) pointing to the new Container Apps.
* Fabric PROD workspace connected to eastus2 lakehouse.
* End-to-end demo flow operational: sign-in → app → agent invocation → data query → response.

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

**Decision:** PROD deploys fresh. No data migration required (synthetic data regenerated). SIT remains in westus2 until proven stable in eastus2, then decommissioned in a future sprint.

### Why eastus2 specifically

* 122 OpenAI models (88 GA), 5.8M TPM quota — richest in the tenant
* Foundry Agent Service GA supported
* All 22 resource types confirmed GA (Sprint 18 feasibility analysis)
* DataZone + ProvisionedManaged SKUs available for future scale
* Same continent as current deployment (acceptable latency for EU-based users during demo scope)

---

## 3. Scope

### In scope

| # | Item | Deliverable |
|---|------|-------------|
| T1 | Bicep template: PROD eastus2 landing zone | `infra/prod-eastus2/main.bicep` + modules |
| T2 | VNet + subnets + NSGs | Network foundation |
| T3 | Key Vault (PROD) | Secrets store |
| T4 | Storage Account (PROD) | Platform storage |
| T5 | Log Analytics + App Insights | Observability stack |
| T6 | Container Registry | Shared image registry (geo-replicated from SIT or new) |
| T7 | Container Apps Environment + apps (3) | Agent-host + App Fluent + Sim Capacity |
| T8 | Cosmos DB (2 accounts: CSA + platform) | NoSQL + vector search + private endpoints |
| T9 | Event Hubs namespace | Event ingestion |
| T10 | Service Bus namespace | Message routing |
| T11 | AI Services + Foundry project | Control plane (eastus2-native) |
| T12 | Model deployments (gpt-5, gpt-5-mini, o3) | Agent backing models |
| T13 | Agent registration (8 agents) | Full roster in PROD |
| T14 | Managed Identities (7) | Workload identities |
| T15 | Private endpoints + Private DNS zones | Cosmos DB + Key Vault PE |
| T16 | Fabric capacity (F2) | PROD Fabric in eastus2 |
| T17 | DNS: `app.curavias.ch` → PROD Container Apps | Custom domain + managed TLS |
| T18 | Logic Apps workflow | Platform orchestration |
| T19 | Entra: PROD app registration bindings | RBAC for PROD identities |
| T20 | End-to-end PROD verification | Full demo flow proven |
| T21 | Bicep `what-if` + deployment evidence | IaC proof |
| T22 | PROD evidence document | `docs/sprints/prod-evidence-eastus2.md` |

### Out of scope

* SIT decommission (future sprint after PROD proven stable)
* PHI data onboarding (per ADR-0016, demo scope only)
* Multi-region DR (not required for demo scope)
* switzerlandnorth failover (post-demo scope consideration)

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

## 5. Resource inventory (PROD eastus2)

| # | Resource Type | Name Pattern | SKU/Tier | Notes |
|---|------|------|------|-------|
| 1 | Resource Group | `rg-ihzhhpf-prod-eastus2` | — | New RG in eastus2 |
| 2 | VNet | `vnet-platform-ihzhhpf-prod` | — | 3 subnets: snet-cae, snet-data, snet-app |
| 3 | NSGs (×3) | `*-nsg-eastus2` | — | Per subnet |
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
| 17 | AI Services | `ai-ihzhhpf-prod-eastus2` | S0 | Foundry-enabled |
| 18 | Foundry Project | `ai-ihzhhpf-prod-eastus2-project` | — | 8 agents + 3 models |
| 19 | Fabric Capacity | `fabricihzhhpfprod` | F2 | eastus2 |
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
| **P1: IaC authoring** | T1 (Bicep modules) | Sprint 18 done | 4h |
| **P2: Foundation** | T2–T6 (VNet, KV, Storage, Log, ACR) | T1 reviewed | 1h |
| **P3: Compute** | T7 (CAE + 3 apps) | P2 | 2h |
| **P4: Data** | T8–T10 (Cosmos ×2, EVH, SB) + T15 (PEs) | P2 | 2h |
| **P5: AI/Foundry** | T11–T13 (AI + project + models + agents) | P2 | 2h |
| **P6: Fabric** | T16 (capacity + workspace) | P2 | 1h |
| **P7: Integration** | T17 (DNS), T18 (Logic), T19 (Entra) | P3, P4, P5 | 2h |
| **P8: Verification** | T20–T22 (E2E test, evidence) | P3–P7 | 3h |

**Total estimated effort:** ~17 hours (2–3 working days)

---

## 7. Bicep module plan

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
| `app.curavias.ch` | PROD app | Points to westus2 CA (or not yet assigned) | CNAME → eastus2 CA FQDN |
| `appsit.curavias.ch` | SIT app | Points to westus2 CA | Unchanged (SIT stays in westus2) |
| `api.curavias.ch` | PROD API | Not assigned | CNAME → eastus2 agent-host CA |

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

* New `fabricihzhhpfprod` capacity (F2 SKU) in eastus2
* Create PROD workspace `ws-ihzhhpf-prod-data` attached to eastus2 capacity
* Deploy lakehouse, notebooks, semantic model from repo via Fabric Git integration (Sprint 17 pattern)
* No data migration — run simulator to regenerate synthetic PROD data

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
| Subscription quota for eastus2 | ✅ Verified | — |
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

* [ ] `infra/prod-eastus2/main.bicep` authored and passes `az bicep build`
* [ ] `az deployment group what-if` produces clean output with expected resources
* [ ] All 25 resources deployed in `rg-ihzhhpf-prod-eastus2` with `Succeeded` state
* [ ] Cosmos DB accounts: AAD-only, local auth disabled, PE connected, vector search enabled
* [ ] AI Services + Foundry project with 3 models deployed and 8 agents registered
* [ ] Container Apps: 3 apps running, agent-host health check green
* [ ] Custom domain `app.curavias.ch` resolves to PROD CA with valid TLS
* [ ] Fabric capacity F2 active in eastus2; PROD workspace created
* [ ] E2E demo flow: sign-in → app → agent → data → response (end-to-end green)
* [ ] PROD evidence document committed: `docs/sprints/prod-evidence-eastus2.md`
* [ ] All CI checks pass (markdown lint, link check, Bicep build)
* [ ] ADR (if needed) for PROD region strategy beyond ADR-0028
* [ ] SIT remains functional (no breaking changes to westus2)

---

## 15. References

* [Sprint 18 Design Spec](../specs/2026-07-17-sprint-18-foundry-eastus2-control-plane-design.md)
* [Sprints 11–16 Roadmap Design](../specs/2026-07-09-sprints-11-16-roadmap-design.md)
* [ADR-0013: Temporary US Region Demo Scope](../../adr/0013-temporary-us-region-demo-scope.md)
* [SIT Evidence (2026-07-17)](../../sprints/sit-evidence-2026-07-17.md)
* [Sprint 17: Fabric Git Integration Design](../specs/2026-07-10-sprint-17-fabric-git-cicd-and-lakehouse-schema-design.md)
* [AGENTS.md](../../../AGENTS.md)
* [.github/copilot-instructions.md](../../../.github/copilot-instructions.md)
