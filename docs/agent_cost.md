# Agent Cost - Copilot Telemetry + Azure Subscription Spend

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | n/a |

## Purpose

This document captures two weekly cost inputs to the
[Business Value Assessment](BVA.md) and its Total Cost of Ownership (TCO)
model, and is the evidence annex a future **BVA Agent**
([proposal](superpowers/ideas/Curavias-BVA-Agent-Proposal.md)) will consume
and keep current:

1. **Azure subscription spend** for the SIT + PROD deployment
   (subscription 1, `ihzhhpf` / MCAP164444) - authoritative billed cost from
   Azure Cost Management, with a full [BOM annex](agent-cost-bom.md).
2. **GitHub Copilot CLI usage telemetry** (tokens and AI Units) - best-effort
   consumption signal for the agent-development effort spent driving the
   Curavias platform via the Copilot coding agent.

## Azure subscription spend (SIT + PROD) - weekly

* **Scope:** subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`
  (`ME-MngEnvMCAP164444-urruegg-1`, tenant
  `1337187a-4c41-4da9-8fca-731bba7a4329`). Hosts both SIT and PROD `ihzhhpf`
  resources across resource groups `rg-ihzhhpf-sit`, `rg-ihzhhpf-prod`,
  `rg-ihzhhpf-prod-eastus2`, and their managed Container Apps environments.
* **Source:** Azure Cost Management **ActualCost** query, Daily granularity
  aggregated to ISO weeks (Monday start). Authoritative billed cost, not
  telemetry. **Currency:** USD. **Period:** 2026-04-01 to 2026-07-27.
* **Snapshot:** 2026-07-28, grand total **USD 491.11**. Recent
  weeks are still settling in ActualCost, so the latest week can rise on a
  later pull (the 2026-07-27 week moved 26.66 -> 58.10 between two same-day
  pulls). Treat the newest 1-2 weeks as provisional.
* **No spend before 2026-06-29.** The window opens 2026-04-01, but the first
  billed week is **2026-06-29** - SIT/PROD were only stood up in the
  MCAP164444 tenant after the Sprint 00 tenant migration (completed
  2026-07-02). April to late-June weeks are genuinely **zero-cost**.
* **Demo/PoT scope.** Per [ADR-0013](adr/0013-temporary-us-region-demo-scope.md)
  the workload runs in `westus2` on synthetic data; a proof-of-technology
  footprint, not a production Swiss-region run rate.

### Weekly cost by Azure service (USD)

| Service (USD) | 2026-06-29 | 2026-07-06 | 2026-07-13 | 2026-07-20 | 2026-07-27 | **Total** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Microsoft Fabric | 5.83 | 53.01 | 42.59 | 100.87 | 16.55 | **218.85** |
| Log Analytics | 0.00 | 8.19 | 15.62 | 36.73 | 9.39 | **69.92** |
| Azure Container Apps | 0.00 | 2.10 | 11.75 | 26.89 | 6.33 | **47.08** |
| Azure Cosmos DB | 0.00 | 3.94 | 8.83 | 18.06 | 4.22 | **35.05** |
| Event Hubs | 1.83 | 9.15 | 9.81 | 10.09 | 1.44 | **32.32** |
| Container Registry | 4.58 | 9.35 | 8.75 | 5.83 | 0.85 | **29.36** |
| Azure Cognitive Search | 0.00 | 0.00 | 0.00 | 12.43 | 16.13 | **28.56** |
| Virtual Network | 0.00 | 0.73 | 3.76 | 7.02 | 1.44 | **12.95** |
| Load Balancer | 0.00 | 0.00 | 3.42 | 6.23 | 1.20 | **10.85** |
| Azure App Service | 0.58 | 2.04 | 1.06 | 1.65 | 0.52 | **5.85** |
| Foundry Models | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | **0.14** |
| Azure DNS | 0.00 | 0.01 | 0.04 | 0.07 | 0.01 | **0.13** |
| Storage | 0.00 | 0.00 | 0.01 | 0.02 | 0.00 | **0.04** |
| **Weekly total** | **12.82** | **88.52** | **105.79** | **225.88** | **58.10** | **491.11** |

`Microsoft Fabric` is the dominant driver (~45% of
spend), followed by Log Analytics and Azure Container Apps.

### Weekly cost by resource group (USD)

| Resource group (USD) | 2026-06-29 | 2026-07-06 | 2026-07-13 | 2026-07-20 | 2026-07-27 | **Total** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| rg-ihzhhpf-sit | 10.37 | 78.73 | 87.20 | 126.59 | 26.73 | **329.61** |
| rg-ihzhhpf-prod | 2.46 | 9.79 | 8.28 | 69.40 | 29.93 | **119.85** |
| rg-ihzhhpf-prod-eastus2 | 0.00 | 0.00 | 6.20 | 22.40 | 0.00 | **28.60** |
| me_cae-ihzhhpf-sit_rg-ihzhhpf-sit_westus2 | 0.00 | 0.00 | 3.90 | 5.04 | 0.72 | **9.66** |
| me_cae-ihzhhpf-prod_rg-ihzhhpf-prod_switzerlandnorth | 0.00 | 0.00 | 0.00 | 2.43 | 0.72 | **3.15** |
| me_cae-ihzhhpf-prod_rg-ihzhhpf-prod-eastus2_eastus2 | 0.00 | 0.00 | 0.21 | 0.00 | 0.00 | **0.21** |
| mcapsgovernance | 0.00 | 0.00 | 0.01 | 0.02 | 0.00 | **0.03** |
| **Weekly total** | **12.82** | **88.52** | **105.79** | **225.88** | **58.10** | **491.11** |

### Weekly cost by resource (USD, resources >= 0.05 total)

Full per-resource detail for every billed resource; the full deployed
inventory (including zero-cost resources) is in the
[BOM annex](agent-cost-bom.md).

| Resource | Resource group | 2026-06-29 | 2026-07-06 | 2026-07-13 | 2026-07-20 | 2026-07-27 | **Total** |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fabricihzhhpfsit | rg-ihzhhpf-sit | 5.83 | 53.01 | 37.80 | 55.37 | 7.70 | **159.72** |
| log-ihzhhpf-sit | rg-ihzhhpf-sit | 0.00 | 8.19 | 15.62 | 22.73 | 3.26 | **49.79** |
| fabricihzhhpfprod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 31.79 | 8.85 | **40.64** |
| cosmos-csa-ihzhhpf-sit | rg-ihzhhpf-sit | 0.00 | 3.94 | 8.06 | 8.06 | 1.15 | **21.22** |
| log-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 14.00 | 6.13 | **20.13** |
| fabricihzhhpfprod | rg-ihzhhpf-prod-eastus2 | 0.00 | 0.00 | 4.78 | 13.70 | 0.00 | **18.49** |
| evh-ihzhhpf-sit-y26y | rg-ihzhhpf-sit | 1.83 | 5.04 | 5.04 | 5.04 | 0.72 | **17.67** |
| cri75lbu5sj4hza | rg-ihzhhpf-sit | 2.29 | 4.68 | 4.67 | 4.67 | 0.68 | **16.99** |
| srch-ihzhhpf-sit | rg-ihzhhpf-sit | 0.00 | 0.00 | 0.00 | 6.38 | 8.06 | **14.45** |
| srch-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 6.05 | 8.06 | **14.11** |
| evh-ihzhhpf-prod-i62t | rg-ihzhhpf-prod | 0.00 | 4.11 | 4.32 | 2.62 | 0.72 | **11.77** |
| crxw5ddbxs36tbm | rg-ihzhhpf-prod | 2.29 | 4.67 | 3.95 | 0.00 | 0.00 | **10.91** |
| ca-app-fluent-ihzhhpf-sit | rg-ihzhhpf-sit | 0.00 | 1.32 | 4.48 | 4.42 | 0.64 | **10.86** |
| ca-sim-capacity-ihzhhpf-sit | rg-ihzhhpf-sit | 0.00 | 0.79 | 3.73 | 4.30 | 0.62 | **9.44** |
| ca-signal-runner-ihzhhpf-sit | rg-ihzhhpf-sit | 0.00 | 0.00 | 0.00 | 6.45 | 1.81 | **8.26** |
| ca-agent-host-ihzhhpf-sit | rg-ihzhhpf-sit | 0.00 | 0.00 | 3.54 | 3.95 | 0.59 | **8.08** |
| capp-svc-lb | me_cae-ihzhhpf-sit_rg-ihzhhpf-sit_westus2 | 0.00 | 0.00 | 3.25 | 4.20 | 0.60 | **8.05** |
| cosmos-csa-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 5.08 | 1.38 | **6.47** |
| cosmos-csa-ihzhhpf-prod | rg-ihzhhpf-prod-eastus2 | 0.00 | 0.00 | 0.77 | 3.84 | 0.00 | **4.61** |
| pe-cosmos-csa-ihzhhpf-sit | rg-ihzhhpf-sit | 0.00 | 0.73 | 1.68 | 1.68 | 0.24 | **4.33** |
| ca-signal-runner-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 2.88 | 1.30 | **4.17** |
| asp-platform-ihzhhpf-sit | rg-ihzhhpf-sit | 0.41 | 1.02 | 1.06 | 1.41 | 0.23 | **4.14** |
| pe-cosmos-ihzhhpf-sit | rg-ihzhhpf-sit | 0.00 | 0.00 | 1.32 | 1.68 | 0.24 | **3.24** |
| evh-ihzhhpf-prod-q4nk | rg-ihzhhpf-prod-eastus2 | 0.00 | 0.00 | 0.45 | 2.43 | 0.00 | **2.88** |
| capp-svc-lb | me_cae-ihzhhpf-prod_rg-ihzhhpf-prod_switzerlandnorth | 0.00 | 0.00 | 0.00 | 2.03 | 0.60 | **2.63** |
| cosmos-po-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 0.69 | 0.92 | **1.61** |
| capp-svc-lb-ip | me_cae-ihzhhpf-sit_rg-ihzhhpf-sit_westus2 | 0.00 | 0.00 | 0.65 | 0.84 | 0.12 | **1.61** |
| ca-sim-capacity-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 1.09 | 0.50 | **1.58** |
| ca-app-fluent-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 1.06 | 0.48 | **1.53** |
| ca-agent-host-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 0.87 | 0.39 | **1.26** |
| asp-platform-ihzhhpf-prod | rg-ihzhhpf-prod | 0.17 | 1.02 | 0.00 | 0.00 | 0.00 | **1.19** |
| cosmos-po-ihzhhpf-sit | rg-ihzhhpf-sit | 0.00 | 0.00 | 0.00 | 0.38 | 0.77 | **1.15** |
| pe-kv-ihzhhpf-prod-swn1 | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 0.81 | 0.24 | **1.05** |
| pe-cosmos-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 0.81 | 0.24 | **1.05** |
| pe-cosmos-csa-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 0.79 | 0.24 | **1.03** |
| ca-agent-host-ihzhhpf-prod | rg-ihzhhpf-prod-eastus2 | 0.00 | 0.00 | 0.00 | 0.94 | 0.00 | **0.94** |
| ca-app-fluent-ihzhhpf-prod | rg-ihzhhpf-prod-eastus2 | 0.00 | 0.00 | 0.00 | 0.93 | 0.00 | **0.93** |
| crihzhhpfprod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 0.61 | 0.17 | **0.78** |
| crihzhhpfprod | rg-ihzhhpf-prod-eastus2 | 0.00 | 0.00 | 0.13 | 0.55 | 0.00 | **0.68** |
| stapp-ihzhhpf-prod | rg-ihzhhpf-prod | 0.00 | 0.00 | 0.00 | 0.23 | 0.30 | **0.53** |
| capp-svc-lb-ip | me_cae-ihzhhpf-prod_rg-ihzhhpf-prod_switzerlandnorth | 0.00 | 0.00 | 0.00 | 0.41 | 0.12 | **0.53** |
| capp-svc-lb | me_cae-ihzhhpf-prod_rg-ihzhhpf-prod-eastus2_eastus2 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | **0.18** |
| ai-ihzhhpf-sit-eastus2 | rg-ihzhhpf-sit | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | **0.14** |
| pe-cosmos-ihzhhpf-prod | rg-ihzhhpf-prod-eastus2 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | **0.07** |
| privatelink.documents.azure.com | rg-ihzhhpf-sit | 0.00 | 0.01 | 0.02 | 0.02 | 0.00 | **0.06** |

### Bill of Materials summary

Full deployed inventory: **144 resources**. Counts by type and the
complete list are in the [BOM annex](agent-cost-bom.md).

| Resource type | Count |
| --- | ---: |
| Microsoft.ManagedIdentity/userAssignedIdentities | 18 |
| Microsoft.App/jobs | 11 |
| Microsoft.App/managedEnvironments | 10 |
| Microsoft.App/containerApps | 10 |
| Microsoft.Storage/storageAccounts | 8 |
| Microsoft.EventGrid/systemTopics | 8 |
| Microsoft.CognitiveServices/accounts | 6 |
| Microsoft.Network/networkSecurityGroups | 6 |
| Microsoft.DocumentDB/databaseAccounts | 6 |
| Microsoft.Network/privateEndpoints | 5 |
| Microsoft.Network/networkInterfaces | 5 |
| Microsoft.CognitiveServices/accounts/projects | 4 |
| Microsoft.KeyVault/vaults | 4 |
| Microsoft.Network/networkWatchers | 3 |
| Microsoft.Network/privateDnsZones | 3 |
| Microsoft.Network/privateDnsZones/virtualNetworkLinks | 3 |
| Microsoft.ContainerRegistry/registries | 2 |
| Microsoft.OperationalInsights/workspaces | 2 |
| Microsoft.Insights/components | 2 |
| Microsoft.Logic/workflows | 2 |
| Microsoft.MachineLearningServices/workspaces | 2 |
| Microsoft.Network/virtualNetworks | 2 |
| microsoft.operationalinsights/workspaces | 2 |
| Microsoft.EventHub/namespaces | 2 |
| Microsoft.ServiceBus/namespaces | 2 |
| Microsoft.Fabric/capacities | 2 |
| Microsoft.Network/publicIPAddresses | 2 |
| Microsoft.Network/loadBalancers | 2 |
| Microsoft.App/managedEnvironments/managedCertificates | 2 |
| Microsoft.Search/searchServices | 2 |
| Microsoft.Insights/actiongroups | 1 |
| Microsoft.Web/serverFarms | 1 |
| microsoft.insights/actiongroups | 1 |
| Microsoft.Web/sites | 1 |
| Microsoft.Network/dnszones | 1 |
| Microsoft.Web/staticSites | 1 |
| **Total** | **144** |

## Copilot CLI usage telemetry

This section captures **GitHub Copilot CLI usage telemetry** (tokens and
AI Units) on a weekly basis. It quantifies the agent-development effort spent
driving the Curavias platform via the Copilot coding agent.

### Data source and limitations (read before using in TCO)

* **This is telemetry, not billing.** Figures come from the Copilot CLI
  **session store** (per-turn usage events), not GitHub's billing ledger.
* **No authoritative currency conversion.** The store records **AI Units
  (AIU)** but not a `$`/AIU rate. A monetary line needs the billed AIU rate
  from the GitHub billing dashboard.
* **Incomplete history.** The stores retain only recent sessions; continuous
  data since April does not exist (earliest captured session 2026-05-04, then
  a gap until July 2026).
* **AIU only from 2026-07-17.** `total_nano_aiu` is recorded only in the local
  store, so the AIU series starts 2026-07-17; the token series reaches
  slightly further back via the cloud store.
* **Cache-dominated input.** ~90%+ of input tokens are cache reads, typically
  priced far below fresh input tokens.

### Weekly AI Units and tokens (local store - cost unit)

| Week (Mon) | Sessions | Input tok | Output tok | Cache-read tok | Reasoning tok | AIU consumed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-07-17 (W28) | 3 | 468,390,537 | 2,616,277 | 442,175,660 | 906,779 | 44,191.973 |
| 2026-07-20 (W29) | 30 | 1,798,630,898 | 13,247,695 | 1,665,029,257 | 4,664,105 | 190,943.247 |
| 2026-07-27 (W30) | 9 | 98,635,372 | 591,353 | 90,699,896 | 186,987 | 10,966.464 |
| **Total** | - | **2,365,656,807** | **16,455,325** | **2,197,904,813** | **5,757,871** | **246,101.684** |

### Weekly tokens (cloud store - longer history)

| Week (Mon) | Sessions | Input tok | Output tok |
| --- | ---: | ---: | ---: |
| 2026-05-04 | 1 | 476,875 | 3,320 |
| 2026-07-06 | 1 | 1,216,228 | 7,941 |
| 2026-07-13 | 5 | 282,990,208 | 1,884,932 |
| 2026-07-20 | 29 | 1,415,812,356 | 9,556,700 |
| 2026-07-27 | 7 | 86,340,559 | 489,025 |

## How to get authoritative cost

* **Azure (already authoritative):** re-run the Cost Management ActualCost
  query to refresh settling weeks. A FOCUS export feeds the Sprint 15 BVA data
  product.
* **Copilot billing:** create a fine-grained PAT with **`Plan` (read)**, then
  `gh api /users/urruegg/settings/billing/usage?year=2026` and aggregate by
  week (the default CLI token returns HTTP 404). Once the billed AIU rate is
  known, add a `$` column to the local-store table above and carry the weekly
  total into the [BVA](BVA.md) TCO model.
