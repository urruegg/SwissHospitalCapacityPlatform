# Sprint 19 — SIT↔PROD parity matrix (all levels)

| Field | Value |
|-------|-------|
| **Version** | 1.5.0 |
| **Date** | 2026-07-29 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.4.0 (live 2026-07-28 re-verification; surfaced the gold-medallion divergence) |

## 1. Summary

> **2026-07-29 gap remediation (v1.5.0).** The external-signals + forecast
> gold-medallion gap surfaced in v1.4.0 is now **CLOSED**. A gated
> (`approved-to-apply` by **@urruegg**, 2026-07-29T09:08 +02:00) PROD medallion
> rebuild materialised the two approved lanes live in PROD gold, verified by a
> fresh OneLake DFS re-read (evidence [E15](#e15-prod-gap-remediation-2026-07-29)):
>
> * **external-signals lane** — `bronze.ext_signals_raw`,
>   `silver.ext_signals` + `silver.ext_signals_quarantine`, and all 5
>   `gold.ext_*` tables (`ext_dim_hazard_type`, `ext_dim_region`,
>   `ext_dim_source`, `ext_fact_signal`, `ext_fact_trigger_event`) now present in
>   PROD — the `external-signals` semantic model finally has backing gold data.
> * **forecast lane** — `gold.fact_forecast_driver`,
>   `gold.fact_occupancy_forecast`, and `gold.fact_signal` now present in PROD
>   (deployed from the committed self-contained
>   `data-platform/notebooks/foresight/run_foresight_evidence.ipynb`, byte-identical
>   to the proven SIT notebook).
>
> PROD gold went **28 → 36**. The only SIT-only gold tables now remaining are the
> 11 `bva_*` (⏳ gated forward-parity, unchanged) and the legacy nested
> `patient-flow` namespace (disposition pending — see §5). Both medallion applies
> were additive (0 deletes), synthetic-only, no PHI.

The v1.4.0 baseline finding that this remediation closes is retained below for
traceability.

> **2026-07-28 full re-verification (v1.4.0, Sprint 33 close-out).** A fresh
> end-to-end live re-read (control plane via `az`, plus the OneLake DFS +
> Fabric REST data plane) both **confirmed new parity gained since 2026-07-24**
> and **surfaced one new data-product divergence** the earlier control-plane-only
> matrix could not see:
>
> * **PROD storage is now genuinely present** — `stcorpusihzhhpfprod`,
>   `stdpihzhhpfprodi62t`, `stmasterdataihzhhpfprod`, `stmediaihzhhpfprod`
>   (the former 2026-07-24 "PROD has no storage accounts" open item is
>   **closed**, superseding the stale §5 gap note).
> * **Product-Owner stack (Sprint 28) is live in BOTH** environments — `ca-po-*`
>   Container App, `kvpo*` Key Vault, and `stcorpus*` corpus storage in each RG.
> * **PROD now carries `ca-sim-capacity-ihzhhpf-prod`** (running), so the
>   simulation-capacity runtime is no longer SIT-only.
> * **New finding — gold data-product medallion divergence.** SIT gold has **48**
>   tables; PROD gold has **28**. PROD is missing 20 SIT tables across three
>   product families, consistently absent bronze→silver→gold: the **BVA cost
>   product** (`bva_consumption` + 11 `bva_*` gold), the **external-signals
>   product** (`ext_signals*` + 5 `ext_*` gold), and newer **forecast facts**
>   (`fact_forecast_driver`, `fact_occupancy_forecast`, `fact_signal`) plus the
>   legacy `patient-flow` table. Cosmos containers and the two semantic models
>   (`capacity-dashboard`, `external-signals`) remain at parity; no `bva`
>   database / `opportunities` container and no `sm_bva` semantic model exist in
>   **either** environment (WS-A/WS-D live publish is `approved-to-apply`-gated →
>   absent-in-both, not a divergence).

Live read-only `az` evidence first gathered on 2026-07-24 and re-verified on
2026-07-28 shows that SIT and PROD are aligned for the core production path
(agent host, signal runner execution, Cosmos, Event Hubs, Key Vault posture, app
ingress, observability, and the Product-Owner stack), while the known
region/topology differences are deliberate. Re-verification corrected two former
red findings: PROD is more hardened than SIT for Key Vault private networking and
signal-runner identity. The former data/AI/integration-lane gap was **closed on
2026-07-24 by the D8 full-parity deploy slices** (additive, 0 deletes,
`Succeeded`): PROD substrate includes the ML workspace, ADLS masterdata,
`sim-capacity` CA, skills-sim jobs + managed environments, Fabric F2
workspace/lakehouse + 2 semantic models, and the Foundry project (3 models + 8
agents). The remaining non-parity items are the deliberate region/topology
asymmetries, the Fabric IQ ontology (excluded from GA parity per ADR,
availability-blocked, #270), and the **new 2026-07-28 gold-medallion divergence**
availability-blocked, #270), and the 2026-07-28 gold-medallion divergence
— of which the BVA family remains a **managed, gated forward-parity item**
(Sprint 33 SIT-first) while the external-signals + forecast families were
**remediated on 2026-07-29** (gated PROD medallion rebuild, §5, E15), leaving
only the legacy `patient-flow` namespace pending disposition.

**Verdict tally (post-2026-07-29 remediation):** ✅ **Parity** 11 ·
⚠️ **Deliberate asymmetry** 5 · ⏳ **Gated forward-parity** 1 ·
🟥 **Gap** 1 (legacy `patient-flow` namespace only) · **N-A** 1.

> **Static parity harness (2026-07-26, #255):** module-selection parity between
> `infra/environments/sit.bicepparam` and `infra/environments/prod-swn.bicepparam`
> is now machine-checked offline by
> [`infra/tests/test_sit_prod_parity.py`](../../../infra/tests/test_sit_prod_parity.py)
> (wired into the `bicep-build` job of `ci-infra-validate.yml`). It asserts
> effective `enable*Module` parity — resolving undeclared flags to the
> `infra/main.bicep` default — against an ADR-sourced deliberate-asymmetry
> allow-list, so any new SIT↔PROD module drift fails CI until it is fixed or
> documented. The four current allow-listed asymmetries are: lean-PROD
> `enableExperienceHostingModule` + `enableApiRuntimeModule` off (ADR-0037,
> Level 5); PROD-only `enableSignalRunnerModule` on (ADR-0039 hardening,
> Level 3); and SIT-only `enableDecisionApplyJobModule` on (Sprint 26 WS-C
> #335). The deliberate `skillsEventstreamSourceMode` transport split
> (SIT `CustomEndpoint` / PROD `EventHub`, ADR-0043) is asserted separately.
> This complements the live `deployed-parity-check` job (resource-types,
> `workflow_dispatch`).

## 2. Facts (F1–F4)

* **F1:** PROD is Azure **Switzerland North**, single-region, resource group
  `rg-ihzhhpf-prod`, and is the GA target.
* **F2:** No customer/patient PID/PHI is present; the platform is
  metadata/episode-driven per ADR-0016.
* **F3:** SIT in **westus2** is acceptable because SIT uses only synthetic data,
  per ADR-0013.
* **F4:** SIT deliberately permits cross-region access and is split across
  westus2 plus the eastus2 Foundry control-plane account
  `ai-ihzhhpf-sit-eastus2` per ADR-0032. PROD does not need that eastus2 split.
* **F5:** The Sprint 33 BVA data product (`bva_consumption` bronze/silver, 11
  `bva_*` gold tables, the `sm_bva` semantic model, and the `bva`/`opportunities`
  Cosmos SoR) is authored **SIT-first**; its live PROD publish is
  `approved-to-apply`-gated per the WS-A/WS-D gated-load plans. SIT-only presence
  of the BVA family is therefore a **managed, gated forward-parity item**, not an
  unmanaged gap.

## 3. Parity matrix

| Level | Dimension | SIT (westus2/eastus2) | PROD (switzerlandnorth) | Verdict | Evidence ref. |
|---|---|---|---|---|---|
| 1 | Region and primary topology | `rg-ihzhhpf-sit` is `westus2`; main SIT resources are in `westus2`. | `rg-ihzhhpf-prod` is `switzerlandnorth`; PROD is single-region GA target. | ⚠️ **Deliberate asymmetry (F1/F3 / ADR-0013)** | [E1](#e1-region--topology) |
| 1 | SIT eastus2 Foundry split | SIT also has `ai-ihzhhpf-sit-eastus2` in `eastus2` for the Foundry control plane. | No corresponding PROD eastus2 split is required. | ⚠️ **Deliberate asymmetry (F4 / ADR-0032)** | [E1](#e1-region--topology) |
| 2 | VNet, subnets, and CAE VNet integration | `vnet-platform-ihzhhpf-sit` `10.60.0.0/16`; `cae-ihzhhpf-sit` integrated with `snet-cae`. | `vnet-platform-ihzhhpf-prod` `10.70.0.0/16`; `cae-ihzhhpf-prod` integrated with `snet-cae`. | ✅ **Parity** | [E2](#e2-network) |
| 2 | Private endpoints and private DNS | Cosmos platform + CSA private endpoints are Approved; only `privatelink.documents.azure.com` exists. No Key Vault private endpoint or `privatelink.vaultcore.azure.net` zone was returned; SIT KV `kv-ihzhhpf-sit-y26y` has `publicNetworkAccess=Disabled` but no PE. | Cosmos platform + CSA and Key Vault private endpoints are Approved; documents and vaultcore private DNS zones exist. PROD has Approved `pe-kv-ihzhhpf-prod-swn1` and KV `publicNetworkAccess=Disabled`. | ⚠️ **Deliberate asymmetry — PROD exceeds SIT (F4)**. SIT permits broader/cross-region access, so SIT KV needs no PE; SIT could adopt the PROD KV-PE pattern as future hardening, not required for GA parity. | [E2](#e2-network) |
| 3 | Agent-host managed identity and platform roles | `ca-agent-host-ihzhhpf-sit` uses UAMI `id-ca-agent-host-ihzhhpf-sit`; has `AcrPull`, `Cognitive Services User`, and Cosmos SQL data-plane role `...0002` on platform + CSA accounts. | `ca-agent-host-ihzhhpf-prod` uses UAMI `id-ca-agent-host-ihzhhpf-prod`; has `AcrPull`, `Cognitive Services User`, and Cosmos SQL data-plane role `...0002` on platform + CSA accounts. | ✅ **Parity** | [E3](#e3-identity--rbac) |
| 3 | Signal-runner identity and Event Hubs sender | `ca-signal-runner-ihzhhpf-sit` uses a **SystemAssigned** identity; that principal has `Azure Event Hubs Data Sender` on `evh-ihzhhpf-sit-y26y`. | `ca-signal-runner-ihzhhpf-prod` uses UAMI `id-signal-runner-ihzhhpf-prod`; that principal has `Azure Event Hubs Data Sender` on `evh-ihzhhpf-prod-i62t`. PROD was deliberately hardened to stable UAMI so role assignment survives CAE recreates. | ⚠️ **Deliberate asymmetry — PROD exceeds SIT**. SIT could adopt the stable-UAMI pattern as future hardening, not a GA-parity gap. | [E3](#e3-identity--rbac) |
| 4 | Cosmos DB and Event Hubs data platform | Platform + CSA Cosmos accounts exist, AAD-only (`disableLocalAuth=true`), public access disabled, single `West US 2`; Event Hubs namespace `Standard`, public access enabled. | Platform + CSA Cosmos accounts exist, AAD-only (`disableLocalAuth=true`), public access disabled, single `Switzerland North`; Event Hubs namespace `Standard`, public access enabled. | ✅ **Parity** | [E4](#e4-data-platform) |
| 4 | Storage / ADLS landing zone and data/AI/integration lane | Three StorageV2 accounts with public access disabled: `stcorpusihzhhpfsit` (PO corpus), `stdpihzhhpfsity26y` (data-platform), and `stmasterdataihzhhpfsit` (ADLS Gen2, masterdata landing). | **PROD storage now present (re-verified 2026-07-28):** `stcorpusihzhhpfprod`, `stdpihzhhpfprodi62t`, `stmasterdataihzhhpfprod`, and `stmediaihzhhpfprod` — the former "PROD has no storage accounts" open item is closed. Data/AI/integration lane deployed via the D8 full-parity slices: ML workspace, ADLS masterdata, `sim-capacity` CA + skills-sim jobs/environments, Fabric F2 workspace/lakehouse + 2 semantic models, Foundry project (3 models + 8 agents). Only Fabric IQ Ontology/Data Agent remain Preview-gated (#270). | ✅ **Parity — closed 2026-07-24** by decision D8 (@urruegg, `approved-to-apply`) and re-confirmed live 2026-07-28. PROD storage is present; required BOM items are GA in Switzerland North per ADR-0037. | [E4](#e4-data-platform), [E11](#e11-storage-refresh-2026-07-28) |
| 4 | Gold data-product medallion — BVA cost product (Sprint 33) | `bva_consumption` (bronze/silver) + 11 `bva_*` gold tables (`bva_dim_*` ×8, `bva_fact_azure_consumption`, `bva_fact_budget`, `bva_fact_value_realization`) present in SIT gold. | Absent from PROD gold. WS-A/WS-D live publish is `approved-to-apply`-gated per the gated-load plans; no `bva`/`opportunities` Cosmos container or `sm_bva` semantic model exists in either environment. | ⏳ **Gated forward-parity (F5)** — Sprint 33 is SIT-first; PROD publish is a tracked, human-gated deploy slice, not an unmanaged gap. | [E12](#e12-medallion-table-diff-2026-07-28) |
| 4 | Gold data-product medallion — external-signals + forecast facts | `ext_signals_raw` (bronze), `ext_signals`/`ext_signals_quarantine` (silver), 5 `ext_*` gold tables, and forecast facts `fact_forecast_driver`/`fact_occupancy_forecast`/`fact_signal` present in SIT gold. | **Remediated 2026-07-29** — all 5 `gold.ext_*`, the `ext_signals*` bronze/silver sources, and the 3 forecast facts now present in PROD (gold 28→36); `external-signals` semantic model now has backing gold data. | ✅ **Parity** — gated (`approved-to-apply` @urruegg) PROD medallion rebuild closed the v1.4.0 gap; legacy `patient-flow` namespace tracked separately (§5). | [E15](#e15-prod-gap-remediation-2026-07-29) |
| 4 | Cosmos containers and Fabric semantic models | Platform Cosmos `agenthost` (`agent_interactions`, `approval-events`, `conversations`, `audit`); CSA `csa` (`simulation-runs`, `plans`, `proposed_actions`, `agent-memory`, `response-levers`, `scenarios`); semantic models `capacity-dashboard` + `external-signals`. | Identical Cosmos container set in both platform and CSA accounts; identical semantic models `capacity-dashboard` + `external-signals`. | ✅ **Parity** | [E13](#e13-cosmos-containers--semantic-models-2026-07-28) |
| 5 | Core Container Apps runtime | Core apps `ca-app-fluent-ihzhhpf-sit`, `ca-agent-host-ihzhhpf-sit`, `ca-signal-runner-ihzhhpf-sit`, and `ca-po-ihzhhpf-sit` are `Succeeded` / `Running`. | Core apps `ca-app-fluent-ihzhhpf-prod`, `ca-agent-host-ihzhhpf-prod`, `ca-signal-runner-ihzhhpf-prod`, and `ca-po-ihzhhpf-prod` are `Succeeded` / `Running` (Product-Owner stack, Sprint 28, now live in both). | ✅ **Parity** | [E5](#e5-compute--runtime), [E14](#e14-container-apps--key-vault-refresh-2026-07-28) |
| 5 | Simulation-capacity runtime | SIT has `ca-sim-capacity-ihzhhpf-sit` plus the simulation-only CAEs (`cae-sim-*`, `cae-skills-sim-*`). | PROD now carries `ca-sim-capacity-ihzhhpf-prod` (running); the simulation-only CAEs remain SIT-only. | ⚠️ **Deliberate asymmetry (F3 / ADR-0013)** — narrowed: `ca-sim-capacity` reached PROD; only the synthetic-testing CAEs stay SIT-only. | [E5](#e5-compute--runtime), [E14](#e14-container-apps--key-vault-refresh-2026-07-28) |
| 6 | Key Vault / secrets control plane | `kv-ihzhhpf-sit-y26y`: RBAC authorization enabled; public network access disabled. | `kv-ihzhhpf-prod-swn1`: RBAC authorization enabled; public network access disabled. | ✅ **Parity** | [E6](#e6-key-vault--secrets) |
| 7 | App / experience ingress and custom domain | `ca-app-fluent-ihzhhpf-sit` has external ingress, `appsit.curavias.ch`, and a westus2 Container Apps FQDN. | `ca-app-fluent-ihzhhpf-prod` has external ingress, `app.curavias.ch`, and a Switzerland North Container Apps FQDN. | ✅ **Parity** | [E7](#e7-app--experience) |
| 8 | Observability | App Insights component `appi-ihzhhpf-sit` exists in westus2. | App Insights component `appi-ihzhhpf-prod` exists in switzerlandnorth. | ✅ **Parity** | [E8](#e8-observability) |
| 9 | Fabric IQ ontology | Excluded from GA parity; SIT Fabric IQ remains demo/preview scope. | Excluded from GA parity pending Switzerland North preview gate (#270). | N/A-per-ADR | [E9](#e9-fabric-iq-ontology) |
| 10 | Compliance posture / data classification | Synthetic-only, metadata/episode-driven, no PID/PHI. | Metadata/episode-driven, no customer/patient PID/PHI. | ✅ **Parity** | [E10](#e10-compliance-posture) |

## 4. Evidence appendix

All commands were read-only and executed against subscription
`66a9953a-df37-4c51-856c-9971b9bf3e03` and tenant
`1337187a-4c41-4da9-8fca-731bba7a4329` on 2026-07-24.

### E1 Region & topology

```text
// az group show -n rg-ihzhhpf-sit --query '{name:name,location:location,provisioningState:properties.provisioningState}' -o json
{
  "location": "westus2",
  "name": "rg-ihzhhpf-sit",
  "provisioningState": "Succeeded"
}

// az group show -n rg-ihzhhpf-prod --query '{name:name,location:location,provisioningState:properties.provisioningState}' -o json
{
  "location": "switzerlandnorth",
  "name": "rg-ihzhhpf-prod",
  "provisioningState": "Succeeded"
}

// az resource list --name ai-ihzhhpf-sit-eastus2 --query '[].{name:name,resourceGroup:resourceGroup,location:location,type:type,provisioningState:properties.provisioningState}' -o json
[
  {
    "location": "eastus2",
    "name": "ai-ihzhhpf-sit-eastus2",
    "provisioningState": null,
    "resourceGroup": "rg-ihzhhpf-sit",
    "type": "Microsoft.CognitiveServices/accounts"
  }
]
```

### E2 Network

```text
// az network vnet list -g rg-ihzhhpf-sit --query '[].{name:name,location:location,addressSpace:addressSpace.addressPrefixes,subnets:subnets[].{name:name,addressPrefix:addressPrefix,delegations:delegations[].serviceName}}' -o json
[
  {
    "addressSpace": ["10.60.0.0/16"],
    "location": "westus2",
    "name": "vnet-platform-ihzhhpf-sit",
    "subnets": [
      {"addressPrefix": "10.60.1.0/24", "delegations": [], "name": "snet-app"},
      {"addressPrefix": "10.60.2.0/24", "delegations": [], "name": "snet-data"},
      {"addressPrefix": "10.60.4.0/23", "delegations": ["Microsoft.App/environments"], "name": "snet-cae"}
    ]
  }
]

// az network vnet list -g rg-ihzhhpf-prod --query '[].{name:name,location:location,addressSpace:addressSpace.addressPrefixes,subnets:subnets[].{name:name,addressPrefix:addressPrefix,delegations:delegations[].serviceName}}' -o json
[
  {
    "addressSpace": ["10.70.0.0/16"],
    "location": "switzerlandnorth",
    "name": "vnet-platform-ihzhhpf-prod",
    "subnets": [
      {"addressPrefix": "10.70.1.0/24", "delegations": [], "name": "snet-app"},
      {"addressPrefix": "10.70.2.0/24", "delegations": [], "name": "snet-data"},
      {"addressPrefix": "10.70.4.0/23", "delegations": ["Microsoft.App/environments"], "name": "snet-cae"}
    ]
  }
]

// az network private-endpoint list -g rg-ihzhhpf-sit --query '[].{name:name,location:location,provisioningState:provisioningState,connections:privateLinkServiceConnections[].{target:privateLinkServiceId,groupIds:groupIds,status:privateLinkServiceConnectionState.status}}' -o json
[
  {
    "connections": [{"groupIds": ["Sql"], "status": "Approved", "target": ".../databaseAccounts/cosmos-csa-ihzhhpf-sit"}],
    "location": "westus2",
    "name": "pe-cosmos-csa-ihzhhpf-sit",
    "provisioningState": "Succeeded"
  },
  {
    "connections": [{"groupIds": ["Sql"], "status": "Approved", "target": ".../databaseAccounts/cosmos-ihzhhpf-sit"}],
    "location": "westus2",
    "name": "pe-cosmos-ihzhhpf-sit",
    "provisioningState": "Succeeded"
  }
]

// az network private-endpoint list -g rg-ihzhhpf-prod --query '[].{name:name,location:location,provisioningState:provisioningState,connections:privateLinkServiceConnections[].{target:privateLinkServiceId,groupIds:groupIds,status:privateLinkServiceConnectionState.status}}' -o json
[
  {"name": "pe-cosmos-csa-ihzhhpf-prod", "location": "switzerlandnorth", "provisioningState": "Succeeded", "connections": [{"target": ".../databaseAccounts/cosmos-csa-ihzhhpf-prod", "groupIds": ["Sql"], "status": "Approved"}]},
  {"name": "pe-cosmos-ihzhhpf-prod", "location": "switzerlandnorth", "provisioningState": "Succeeded", "connections": [{"target": ".../databaseAccounts/cosmos-ihzhhpf-prod", "groupIds": ["Sql"], "status": "Approved"}]},
  {"name": "pe-kv-ihzhhpf-prod-swn1", "location": "switzerlandnorth", "provisioningState": "Succeeded", "connections": [{"target": ".../vaults/kv-ihzhhpf-prod-swn1", "groupIds": ["vault"], "status": "Approved"}]}
]

// az network private-dns zone list -g rg-ihzhhpf-sit --query '[].{name:name,recordSets:numberOfRecordSets}' -o json
[
  {"name": "privatelink.documents.azure.com", "recordSets": 5}
]

// az network private-dns zone list -g rg-ihzhhpf-prod --query '[].{name:name,recordSets:numberOfRecordSets}' -o json
[
  {"name": "privatelink.documents.azure.com", "recordSets": 5},
  {"name": "privatelink.vaultcore.azure.net", "recordSets": 2}
]

// az containerapp env list -g rg-ihzhhpf-sit --query '[].{name:name,location:location,provisioningState:properties.provisioningState,vnetConfiguration:properties.vnetConfiguration}' -o json
[
  {"name": "cae-app-fluent-ihzhhpf-sit", "location": "West US 2", "provisioningState": "Succeeded", "vnetConfiguration": null},
  {"name": "cae-ihzhhpf-sit", "location": "West US 2", "provisioningState": "Succeeded", "vnetConfiguration": {"infrastructureSubnetId": ".../vnet-platform-ihzhhpf-sit/subnets/snet-cae", "internal": false}},
  {"name": "cae-sim-ihzhhpf-sit", "location": "West US 2", "provisioningState": "Succeeded", "vnetConfiguration": null},
  {"name": "cae-skills-sim-ihzhhpf-sit", "location": "West US 2", "provisioningState": "Succeeded", "vnetConfiguration": null}
]

// az containerapp env list -g rg-ihzhhpf-prod --query '[].{name:name,location:location,provisioningState:properties.provisioningState,vnetConfiguration:properties.vnetConfiguration}' -o json
[
  {"name": "cae-app-fluent-ihzhhpf-prod", "location": "Switzerland North", "provisioningState": "Succeeded", "vnetConfiguration": null},
  {"name": "cae-ihzhhpf-prod", "location": "Switzerland North", "provisioningState": "Succeeded", "vnetConfiguration": {"infrastructureSubnetId": ".../vnet-platform-ihzhhpf-prod/subnets/snet-cae", "internal": false}}
]
```

### E3 Identity & RBAC

```text
// az identity list -g rg-ihzhhpf-sit --query '[].{name:name,location:location,principalId:principalId,clientId:clientId}' -o json
[
  {"name": "id-platform-ihzhhpf-sit", "location": "westus2", "principalId": "378e389d-651e-4ab4-b956-9d7b407d883c", "clientId": "d0e0fd13-c65a-41e9-891d-a77d6be61c53"},
  {"name": "id-api-ihzhhpf-sit", "location": "westus2", "principalId": "6d051bee-82c9-42af-bc03-0b417282459d", "clientId": "b619b401-cd38-4631-92fd-57f233e57ba2"},
  {"name": "id-ca-agent-host-ihzhhpf-sit", "location": "westus2", "principalId": "6801d353-ae42-49d2-a9b3-8db23f571348", "clientId": "5f579f8e-1b70-4506-8a55-67f59e791aa7"}
]

// az identity list -g rg-ihzhhpf-prod --query '[].{name:name,location:location,principalId:principalId,clientId:clientId}' -o json
[
  {"name": "id-platform-ihzhhpf-prod", "location": "switzerlandnorth", "principalId": "ffe2de7b-25ae-4924-877f-2c08ec44958d", "clientId": "3b719987-507a-473b-ae1f-8bf49ebdecd8"},
  {"name": "id-ca-agent-host-ihzhhpf-prod", "location": "switzerlandnorth", "principalId": "d6ff2ed3-febc-4779-b05f-7f7e17243be2", "clientId": "0bac8b9f-f7a0-479a-abee-9057686c858e"},
  {"name": "id-signal-runner-ihzhhpf-prod", "location": "switzerlandnorth", "principalId": "7d639be1-e6ad-4ef5-b2b0-004eb0a1e107", "clientId": "5800b7e0-ad87-4f32-b414-56ce139d2213"}
]

// az containerapp show -g rg-ihzhhpf-sit -n ca-signal-runner-ihzhhpf-sit --query '{name:name,resourceGroup:resourceGroup,identity:identity}' -o json
{
  "name": "ca-signal-runner-ihzhhpf-sit",
  "resourceGroup": "rg-ihzhhpf-sit",
  "identity": {"type": "SystemAssigned", "principalId": "7f707bae-0861-47e8-b518-f5b4fe94e5ac", "tenantId": "1337187a-4c41-4da9-8fca-731bba7a4329"}
}

// az containerapp show -g rg-ihzhhpf-prod -n ca-signal-runner-ihzhhpf-prod --query '{name:name,resourceGroup:resourceGroup,identity:identity}' -o json
{
  "name": "ca-signal-runner-ihzhhpf-prod",
  "resourceGroup": "rg-ihzhhpf-prod",
  "identity": {"type": "UserAssigned", "userAssignedIdentities": {".../id-signal-runner-ihzhhpf-prod": {"clientId": "5800b7e0-ad87-4f32-b414-56ce139d2213", "principalId": "7d639be1-e6ad-4ef5-b2b0-004eb0a1e107"}}}
}

// az role assignment list --assignee 7f707bae-0861-47e8-b518-f5b4fe94e5ac --all --query '[].{role:roleDefinitionName,scope:scope,principalType:principalType}' -o json
[
  {"principalType": "ServicePrincipal", "role": "Azure Event Hubs Data Sender", "scope": ".../Microsoft.EventHub/namespaces/evh-ihzhhpf-sit-y26y"}
]

// az role assignment list --assignee 7d639be1-e6ad-4ef5-b2b0-004eb0a1e107 --all --query '[].{role:roleDefinitionName,scope:scope,principalType:principalType}' -o json
[
  {"principalType": "ServicePrincipal", "role": "Azure Event Hubs Data Sender", "scope": ".../Microsoft.EventHub/namespaces/evh-ihzhhpf-prod-i62t"}
]

// az role assignment list --assignee <agent-host-principalId> --all --query '[].{role:roleDefinitionName,scope:scope,principalType:principalType}' -o json
// SIT: 6801d353-ae42-49d2-a9b3-8db23f571348; PROD: d6ff2ed3-febc-4779-b05f-7f7e17243be2
{
  "SIT": [
    {"principalType": "ServicePrincipal", "role": "AcrPull", "scope": ".../registries/cri75lbu5sj4hza"},
    {"principalType": "ServicePrincipal", "role": "Cognitive Services User", "scope": ".../accounts/ai-ihzhhpf-sit-eastus2"}
  ],
  "PROD": [
    {"principalType": "ServicePrincipal", "role": "AcrPull", "scope": ".../registries/crihzhhpfprod"},
    {"principalType": "ServicePrincipal", "role": "Cognitive Services User", "scope": ".../accounts/ai-ihzhhpf-prod"}
  ]
}

// az cosmosdb sql role assignment list -g <rg> -a <account> --query '[].{principalId:principalId,roleDefinitionId:roleDefinitionId,scope:scope}' -o json
{
  "cosmos-ihzhhpf-sit": [{"principalId": "6801d353-ae42-49d2-a9b3-8db23f571348", "roleDefinitionId": ".../sqlRoleDefinitions/00000000-0000-0000-0000-000000000002", "scope": ".../databaseAccounts/cosmos-ihzhhpf-sit"}],
  "cosmos-csa-ihzhhpf-sit": [{"principalId": "6801d353-ae42-49d2-a9b3-8db23f571348", "roleDefinitionId": ".../sqlRoleDefinitions/00000000-0000-0000-0000-000000000002", "scope": ".../databaseAccounts/cosmos-csa-ihzhhpf-sit"}],
  "cosmos-ihzhhpf-prod": [{"principalId": "d6ff2ed3-febc-4779-b05f-7f7e17243be2", "roleDefinitionId": ".../sqlRoleDefinitions/00000000-0000-0000-0000-000000000002", "scope": ".../databaseAccounts/cosmos-ihzhhpf-prod"}],
  "cosmos-csa-ihzhhpf-prod": [{"principalId": "d6ff2ed3-febc-4779-b05f-7f7e17243be2", "roleDefinitionId": ".../sqlRoleDefinitions/00000000-0000-0000-0000-000000000002", "scope": ".../databaseAccounts/cosmos-csa-ihzhhpf-prod"}]
}
```

### E4 Data platform

```text
// az cosmosdb list -g rg-ihzhhpf-sit --query '[].{name:name,location:location,locations:locations[].locationName,publicNetworkAccess:publicNetworkAccess,disableLocalAuth:disableLocalAuth,capabilities:capabilities[].name}' -o json
[
  {"name": "cosmos-csa-ihzhhpf-sit", "location": "West US 2", "locations": ["West US 2"], "publicNetworkAccess": "Disabled", "disableLocalAuth": true, "capabilities": ["EnableNoSQLVectorSearch"]},
  {"name": "cosmos-ihzhhpf-sit", "location": "West US 2", "locations": ["West US 2"], "publicNetworkAccess": "Disabled", "disableLocalAuth": true, "capabilities": ["EnableServerless"]}
]

// az cosmosdb list -g rg-ihzhhpf-prod --query '[].{name:name,location:location,locations:locations[].locationName,publicNetworkAccess:publicNetworkAccess,disableLocalAuth:disableLocalAuth,capabilities:capabilities[].name}' -o json
[
  {"name": "cosmos-ihzhhpf-prod", "location": "Switzerland North", "locations": ["Switzerland North"], "publicNetworkAccess": "Disabled", "disableLocalAuth": true, "capabilities": ["EnableServerless"]},
  {"name": "cosmos-csa-ihzhhpf-prod", "location": "Switzerland North", "locations": ["Switzerland North"], "publicNetworkAccess": "Disabled", "disableLocalAuth": true, "capabilities": ["EnableNoSQLVectorSearch"]}
]

// az eventhubs namespace list -g <rg> --query '[].{name:name,location:location,sku:sku.name,publicNetworkAccess:publicNetworkAccess,privateEndpointConnections:privateEndpointConnections[].privateLinkServiceConnectionState.status}' -o json
{
  "SIT": [{"name": "evh-ihzhhpf-sit-y26y", "location": "westus2", "sku": "Standard", "publicNetworkAccess": "Enabled", "privateEndpointConnections": null}],
  "PROD": [{"name": "evh-ihzhhpf-prod-i62t", "location": "switzerlandnorth", "sku": "Standard", "publicNetworkAccess": "Enabled", "privateEndpointConnections": null}]
}

// az storage account list -g rg-ihzhhpf-sit --query '[].{name:name,location:location,kind:kind,sku:sku.name,publicNetworkAccess:publicNetworkAccess,allowBlobPublicAccess:allowBlobPublicAccess}' -o json
[
  {"name": "stdpihzhhpfsity26y", "location": "westus2", "kind": "StorageV2", "sku": "Standard_LRS", "publicNetworkAccess": "Disabled", "allowBlobPublicAccess": false},
  {"name": "stmasterdataihzhhpfsit", "location": "westus2", "kind": "StorageV2", "sku": "Standard_LRS", "publicNetworkAccess": "Disabled", "allowBlobPublicAccess": false}
]

// az storage account list -g rg-ihzhhpf-prod --query '[].{name:name,location:location,kind:kind,sku:sku.name,publicNetworkAccess:publicNetworkAccess,allowBlobPublicAccess:allowBlobPublicAccess}' -o json
[]
```

### E5 Compute & runtime

```text
// az containerapp list -g rg-ihzhhpf-sit --query '[].{name:name,location:location,provisioningState:properties.provisioningState,runningStatus:properties.runningStatus,environmentId:properties.environmentId,ingress:properties.configuration.ingress.{external:external,targetPort:targetPort,fqdn:fqdn,customDomains:customDomains[].name}}' -o json
[
  {"name": "ca-sim-capacity-ihzhhpf-sit", "location": "West US 2", "provisioningState": "Succeeded", "runningStatus": "Running", "environmentId": ".../cae-sim-ihzhhpf-sit", "ingress": null},
  {"name": "ca-app-fluent-ihzhhpf-sit", "location": "West US 2", "provisioningState": "Succeeded", "runningStatus": "Running", "environmentId": ".../cae-app-fluent-ihzhhpf-sit", "ingress": {"external": true, "targetPort": 8080, "fqdn": "ca-app-fluent-ihzhhpf-sit.ashysky-8f51a689.westus2.azurecontainerapps.io", "customDomains": ["appsit.curavias.ch"]}},
  {"name": "ca-agent-host-ihzhhpf-sit", "location": "West US 2", "provisioningState": "Succeeded", "runningStatus": "Running", "environmentId": ".../cae-ihzhhpf-sit", "ingress": {"external": true, "targetPort": 8080, "fqdn": "ca-agent-host-ihzhhpf-sit.salmonsand-fb86922a.westus2.azurecontainerapps.io", "customDomains": null}},
  {"name": "ca-signal-runner-ihzhhpf-sit", "location": "West US 2", "provisioningState": "Succeeded", "runningStatus": "Running", "environmentId": ".../cae-sim-ihzhhpf-sit", "ingress": null}
]

// az containerapp list -g rg-ihzhhpf-prod --query '[].{name:name,location:location,provisioningState:properties.provisioningState,runningStatus:properties.runningStatus,environmentId:properties.environmentId,ingress:properties.configuration.ingress.{external:external,targetPort:targetPort,fqdn:fqdn,customDomains:customDomains[].name}}' -o json
[
  {"name": "ca-app-fluent-ihzhhpf-prod", "location": "Switzerland North", "provisioningState": "Succeeded", "runningStatus": "Running", "environmentId": ".../cae-app-fluent-ihzhhpf-prod", "ingress": {"external": true, "targetPort": 8080, "fqdn": "ca-app-fluent-ihzhhpf-prod.politesky-3ad3f6a5.switzerlandnorth.azurecontainerapps.io", "customDomains": ["app.curavias.ch"]}},
  {"name": "ca-agent-host-ihzhhpf-prod", "location": "Switzerland North", "provisioningState": "Succeeded", "runningStatus": "Running", "environmentId": ".../cae-ihzhhpf-prod", "ingress": {"external": true, "targetPort": 8080, "fqdn": "ca-agent-host-ihzhhpf-prod.whiteriver-d854b3bc.switzerlandnorth.azurecontainerapps.io", "customDomains": null}},
  {"name": "ca-signal-runner-ihzhhpf-prod", "location": "Switzerland North", "provisioningState": "Succeeded", "runningStatus": "Running", "environmentId": ".../cae-ihzhhpf-prod", "ingress": null}
]
```

### E6 Key Vault & secrets

```text
// az keyvault list -g rg-ihzhhpf-sit --query '[].{name:name,location:location,publicNetworkAccess:properties.publicNetworkAccess,enableRbacAuthorization:properties.enableRbacAuthorization,networkAcls:properties.networkAcls.defaultAction}' -o json
[
  {"name": "kv-ihzhhpf-sit-y26y", "location": "westus2", "publicNetworkAccess": "Disabled", "enableRbacAuthorization": true, "networkAcls": null}
]

// az keyvault list -g rg-ihzhhpf-prod --query '[].{name:name,location:location,publicNetworkAccess:properties.publicNetworkAccess,enableRbacAuthorization:properties.enableRbacAuthorization,networkAcls:properties.networkAcls.defaultAction}' -o json
[
  {"name": "kv-ihzhhpf-prod-swn1", "location": "switzerlandnorth", "publicNetworkAccess": "Disabled", "enableRbacAuthorization": true, "networkAcls": null}
]
```

### E7 App & experience

```text
// Extracted from az containerapp list -g rg-ihzhhpf-sit / rg-ihzhhpf-prod, properties.configuration.ingress
{
  "SIT": {
    "name": "ca-app-fluent-ihzhhpf-sit",
    "external": true,
    "targetPort": 8080,
    "fqdn": "ca-app-fluent-ihzhhpf-sit.ashysky-8f51a689.westus2.azurecontainerapps.io",
    "customDomains": ["appsit.curavias.ch"]
  },
  "PROD": {
    "name": "ca-app-fluent-ihzhhpf-prod",
    "external": true,
    "targetPort": 8080,
    "fqdn": "ca-app-fluent-ihzhhpf-prod.politesky-3ad3f6a5.switzerlandnorth.azurecontainerapps.io",
    "customDomains": ["app.curavias.ch"]
  }
}
```

### E8 Observability

```text
// az resource list -g rg-ihzhhpf-sit --resource-type microsoft.insights/components --query '[].{name:name,location:location,kind:kind}' -o json
[
  {"kind": "web", "location": "westus2", "name": "appi-ihzhhpf-sit"}
]

// az resource list -g rg-ihzhhpf-prod --resource-type microsoft.insights/components --query '[].{name:name,location:location,kind:kind}' -o json
[
  {"kind": "web", "location": "switzerlandnorth", "name": "appi-ihzhhpf-prod"}
]
```

### E9 Fabric IQ ontology

No Fabric REST call was attempted. Fabric IQ ontology is recorded as
**N/A-per-ADR** for GA parity because ADR-0034 scopes the Fabric IQ artefact to
demo/preview evidence and issue #270 tracks the Switzerland North preview gate.

### E10 Compliance posture

No `az` command can prove absence of PHI by itself. The parity finding is based
on the accepted repository facts and ADRs: SIT uses synthetic-only data per
ADR-0013, and both SIT and PROD remain metadata/episode-driven with no
customer/patient PID/PHI per ADR-0016.

### E11 Storage refresh (2026-07-28)

```text
// az storage account list -g rg-ihzhhpf-sit --query '[].name' -o tsv
stcorpusihzhhpfsit
stdpihzhhpfsity26y
stmasterdataihzhhpfsit

// az storage account list -g rg-ihzhhpf-prod --query '[].name' -o tsv
stcorpusihzhhpfprod
stdpihzhhpfprodi62t
stmasterdataihzhhpfprod
stmediaihzhhpfprod
```

PROD storage is present, superseding the 2026-07-24 empty result recorded in E4.

### E12 Medallion table diff (2026-07-28)

Data-plane reads via the OneLake DFS filesystem API
(`https://onelake.dfs.fabric.microsoft.com/<workspace>?resource=filesystem&directory=<lakehouse>/Tables/<schema>`),
storage-token auth, executed by
[`data-platform/scripts/fabric/list_gold_tables.py`](../../../data-platform/scripts/fabric/list_gold_tables.py)
(`--environment SIT|PROD`) and equivalent bronze/silver listings.

```text
// gold schema — SIT=48, PROD=28; tables present in SIT gold but absent in PROD gold (20):
bva_dim_capability, bva_dim_date, bva_dim_environment, bva_dim_exec_role,
bva_dim_hospital, bva_dim_meter, bva_dim_resource, bva_dim_service,
bva_fact_azure_consumption, bva_fact_budget, bva_fact_value_realization,   # BVA (F5, gated)
ext_dim_hazard_type, ext_dim_region, ext_dim_source, ext_fact_signal,
ext_fact_trigger_event,                                                    # external-signals (gap)
fact_forecast_driver, fact_occupancy_forecast, fact_signal,                # forecast facts (gap)
patient-flow                                                               # legacy SIT table (gap)

// silver schema — SIT=13, PROD=11; SIT-only: bva_consumption, ext_signals, ext_signals_quarantine
// bronze schema — SIT=12, PROD=11; SIT-only: bva_consumption, ext_signals_raw
// (PROD-only 'schema.json.gz' entries are lakehouse metadata blobs, not Delta tables)
```

The divergence is consistent bronze→silver→gold for both the BVA and
external-signals families, confirming PROD medallion has not been rebuilt for
them (rather than a partial/gold-only projection failure).

### E13 Cosmos containers & semantic models (2026-07-28)

```text
// az cosmosdb sql container list -g <rg> -a <account> -d <db> --query '[].name' -o tsv
cosmos-ihzhhpf-sit/agenthost   : agent_interactions, approval-events, conversations, audit
cosmos-csa-ihzhhpf-sit/csa     : simulation-runs, plans, proposed_actions, agent-memory, response-levers, scenarios
cosmos-ihzhhpf-prod/agenthost  : agent_interactions, conversations, audit, approval-events   # same set
cosmos-csa-ihzhhpf-prod/csa    : agent-memory, scenarios, proposed_actions, response-levers, plans, simulation-runs   # same set
// No 'bva' database / 'opportunities' container in either environment (WS-D publish gated).

// GET https://api.fabric.microsoft.com/v1/workspaces/<id>/semanticModels  (displayName)
SIT  ws-ihzhhpf-sit-data  : capacity-dashboard, external-signals
PROD ws-ihzhhpf-prod-data : capacity-dashboard, external-signals
// No 'sm_bva' semantic model in either environment (WS-A publish gated).
```

### E14 Container Apps & Key Vault refresh (2026-07-28)

```text
// az containerapp list -g <rg> --query '[].{n:name,s:properties.runningStatus}' -o tsv
SIT  : ca-sim-capacity-ihzhhpf-sit(Running), ca-app-fluent-ihzhhpf-sit(Running),
       ca-agent-host-ihzhhpf-sit(Running), ca-signal-runner-ihzhhpf-sit(Running),
       ca-po-ihzhhpf-sit(Running)
PROD : ca-app-fluent-ihzhhpf-prod(Running), ca-agent-host-ihzhhpf-prod(Running),
       ca-signal-runner-ihzhhpf-prod(Running), ca-sim-capacity-ihzhhpf-prod(Running),
       ca-po-ihzhhpf-prod(Running)

// az keyvault list -g <rg> --query '[].name' -o tsv
SIT  : kv-ihzhhpf-sit-y26y, kvpoihzhhpfsit
PROD : kv-ihzhhpf-prod-swn1, kvpoihzhhpfprod
```

Both environments now run the 5-app core set (Product-Owner `ca-po` + `kvpo`
Key Vault added in both since 2026-07-24), and `ca-sim-capacity` is present in
PROD as well as SIT.

### E15 PROD gap remediation (2026-07-29)

Gated (`approved-to-apply` @urruegg, 2026-07-29T09:08 +02:00) PROD medallion
rebuild for the external-signals + forecast lanes, applied via
[`run_single_notebook.py --environment PROD --apply`](../../../data-platform/scripts/fabric/run_single_notebook.py)
and verified by a fresh OneLake DFS re-read.

```text
// external-signals apply — notebook item 13b660fa-50bf-4838-a0a0-548440986719 -> [ok]
PROD bronze : ext_signals_raw
PROD silver : ext_signals, ext_signals_quarantine
PROD gold   : ext_dim_hazard_type, ext_dim_region, ext_dim_source,
              ext_fact_signal, ext_fact_trigger_event

// forecast apply — notebook run 52931adb-ddd1-445b-a0b4-4496a9081b0f -> [ok]
PROD gold   : fact_forecast_driver, fact_occupancy_forecast, fact_signal

// post-remediation gold diff (list_gold_tables.py + DFS listing):
SIT gold = 48, PROD gold = 36 (was 28)
SIT-only remaining: 11 bva_* (F5, gated forward-parity) + patient-flow (legacy, §5)
```

Both applies were additive (0 deletes), synthetic-only, no PHI (ADR-0013 /
ADR-0016). The forecast notebook was confirmed byte-identical (cell-source) to
the proven SIT `run_foresight_evidence` notebook before apply.

## 5. Open items

### 🟥 Gaps

* **Legacy `patient-flow` gold namespace is SIT-only (disposition pending).**
  SIT gold carries a nested `patient-flow/` namespace (Delta sub-tables
  `bed_assignment`, `discharge_recommendation`, `discharge_score`, `encounter`,
  `forecast_output`) from an earlier medallion generation; PROD has none. This is
  unrelated to the Sprint 33 BVA work and was not in the 2026-07-29 remediation
  scope. **Action:** confirm whether `patient-flow` is an intended GA data
  product to forward-port to PROD or a stale SIT artefact to drop; do not rebuild
  in PROD without an explicit decision.

### ✅ Remediated (2026-07-29)

* **PROD gold medallion — external-signals + forecast lanes (was the v1.4.0
  gap).** A gated (`approved-to-apply` by **@urruegg**, 2026-07-29T09:08 +02:00)
  PROD medallion rebuild materialised both lanes live in PROD gold, additive
  (0 deletes), synthetic-only, no PHI:
  * external-signals — `data-platform/notebooks/external-signals/run_ext_medallion.ipynb`
    wrote `bronze.ext_signals_raw`, `silver.ext_signals` +
    `silver.ext_signals_quarantine`, and 5 `gold.ext_*` tables.
  * forecast — `data-platform/notebooks/foresight/run_foresight_evidence.ipynb`
    (byte-identical to the proven SIT notebook) wrote `gold.fact_forecast_driver`,
    `gold.fact_occupancy_forecast`, `gold.fact_signal`.

  Both applied via the gated
  [`run_single_notebook.py --environment PROD --apply`](../../../data-platform/scripts/fabric/run_single_notebook.py)
  runner and verified by a fresh OneLake DFS re-read (PROD gold 28→36, E15). The
  `external-signals` semantic model is Direct Lake over these gold tables and now
  resolves against real data.

### ⏳ Gated forward-parity

* **BVA cost product (Sprint 33, F5).** `bva_consumption` + 11 `bva_*` gold
  tables, the `sm_bva` semantic model, and the `bva`/`opportunities` Cosmos SoR
  are SIT-first by design; the live PROD publish is `approved-to-apply`-gated per
  the WS-A/WS-D gated-load plans. Not an unmanaged gap — it becomes a gap only if
  PROD BVA publish is required for GA and remains unactioned.

### Accepted asymmetries

* **Region:** SIT is westus2 synthetic-only while PROD is Switzerland North GA
  target (F1/F3, ADR-0013).
* **SIT cross-region Foundry:** SIT uses the eastus2 Foundry account
  `ai-ihzhhpf-sit-eastus2`; PROD does not need the split (F4, ADR-0032).
* **SIT-only simulation CAEs:** SIT carries simulation-only Container Apps
  environments (`cae-sim-*`, `cae-skills-sim-*`) for synthetic testing; PROD does
  not (though `ca-sim-capacity` itself is now present in PROD).
* **Key Vault private endpoint:** PROD exceeds SIT with an Approved Key Vault PE
  and vaultcore private DNS zone; SIT intentionally relies on disabled public
  access without a KV PE under F4 and may adopt the pattern later.
* **Signal-runner UAMI:** PROD exceeds SIT with stable
  `id-signal-runner-ihzhhpf-prod`; SIT may adopt the UAMI pattern later.

### N/A-per-ADR

* **Fabric IQ ontology:** excluded from GA parity by ADR-0034 and the #270
  Switzerland North preview gate.
