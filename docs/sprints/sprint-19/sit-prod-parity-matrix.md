# Sprint 19 — SIT↔PROD parity matrix (all levels)

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-24 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | — |

## 1. Summary

Live read-only `az` evidence gathered on 2026-07-24 shows that SIT and PROD are
aligned for the core production path (agent host, signal runner execution,
Cosmos, Event Hubs, Key Vault posture, app ingress, and observability), while the
known region/topology differences are deliberate. Three unintended divergences
remain visible in the evidence: SIT has no Key Vault private endpoint/DNS zone,
SIT signal runner still uses a system-assigned identity while PROD uses a UAMI,
and PROD has no storage/ADLS landing-zone account corresponding to SIT storage.

**Verdict tally:** ✅ **Parity** 9 · ⚠️ **Deliberate asymmetry** 3 · 🟥 **Gap** 3 ·
**N-A** 1.

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

## 3. Parity matrix

| Level | Dimension | SIT (westus2/eastus2) | PROD (switzerlandnorth) | Verdict | Evidence ref. |
|---|---|---|---|---|---|
| 1 | Region and primary topology | `rg-ihzhhpf-sit` is `westus2`; main SIT resources are in `westus2`. | `rg-ihzhhpf-prod` is `switzerlandnorth`; PROD is single-region GA target. | ⚠️ **Deliberate asymmetry (F1/F3 / ADR-0013)** | [E1](#e1-region--topology) |
| 1 | SIT eastus2 Foundry split | SIT also has `ai-ihzhhpf-sit-eastus2` in `eastus2` for the Foundry control plane. | No corresponding PROD eastus2 split is required. | ⚠️ **Deliberate asymmetry (F4 / ADR-0032)** | [E1](#e1-region--topology) |
| 2 | VNet, subnets, and CAE VNet integration | `vnet-platform-ihzhhpf-sit` `10.60.0.0/16`; `cae-ihzhhpf-sit` integrated with `snet-cae`. | `vnet-platform-ihzhhpf-prod` `10.70.0.0/16`; `cae-ihzhhpf-prod` integrated with `snet-cae`. | ✅ **Parity** | [E2](#e2-network) |
| 2 | Private endpoints and private DNS | Cosmos platform + CSA private endpoints are Approved; only `privatelink.documents.azure.com` exists. No Key Vault private endpoint or `privatelink.vaultcore.azure.net` zone was returned. | Cosmos platform + CSA and Key Vault private endpoints are Approved; documents and vaultcore private DNS zones exist. | 🟥 **Gap** | [E2](#e2-network) |
| 3 | Agent-host managed identity and platform roles | `ca-agent-host-ihzhhpf-sit` uses UAMI `id-ca-agent-host-ihzhhpf-sit`; has `AcrPull`, `Cognitive Services User`, and Cosmos SQL data-plane role `...0002` on platform + CSA accounts. | `ca-agent-host-ihzhhpf-prod` uses UAMI `id-ca-agent-host-ihzhhpf-prod`; has `AcrPull`, `Cognitive Services User`, and Cosmos SQL data-plane role `...0002` on platform + CSA accounts. | ✅ **Parity** | [E3](#e3-identity--rbac) |
| 3 | Signal-runner identity and Event Hubs sender | `ca-signal-runner-ihzhhpf-sit` uses a **SystemAssigned** identity; that principal has `Azure Event Hubs Data Sender` on `evh-ihzhhpf-sit-y26y`. | `ca-signal-runner-ihzhhpf-prod` uses UAMI `id-signal-runner-ihzhhpf-prod`; that principal has `Azure Event Hubs Data Sender` on `evh-ihzhhpf-prod-i62t`. | 🟥 **Gap** | [E3](#e3-identity--rbac) |
| 4 | Cosmos DB and Event Hubs data platform | Platform + CSA Cosmos accounts exist, AAD-only (`disableLocalAuth=true`), public access disabled, single `West US 2`; Event Hubs namespace `Standard`, public access enabled. | Platform + CSA Cosmos accounts exist, AAD-only (`disableLocalAuth=true`), public access disabled, single `Switzerland North`; Event Hubs namespace `Standard`, public access enabled. | ✅ **Parity** | [E4](#e4-data-platform) |
| 4 | Storage / ADLS landing zone | Two StorageV2 accounts exist with public access disabled. | `az storage account list -g rg-ihzhhpf-prod` returned an empty array. | 🟥 **Gap** | [E4](#e4-data-platform) |
| 5 | Core Container Apps runtime | Core apps `ca-app-fluent-ihzhhpf-sit`, `ca-agent-host-ihzhhpf-sit`, and `ca-signal-runner-ihzhhpf-sit` are `Succeeded` / `Running`. | Core apps `ca-app-fluent-ihzhhpf-prod`, `ca-agent-host-ihzhhpf-prod`, and `ca-signal-runner-ihzhhpf-prod` are `Succeeded` / `Running`. | ✅ **Parity** | [E5](#e5-compute--runtime) |
| 5 | SIT-only simulation runtime | SIT additionally has simulation CAEs/apps (`cae-sim-*`, `cae-skills-sim-*`, `ca-sim-capacity-*`) for synthetic testing. | PROD does not carry those SIT simulation-only runtime resources. | ⚠️ **Deliberate asymmetry (F3 / ADR-0013)** | [E5](#e5-compute--runtime) |
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

## 5. Open items

### 🟥 Gaps

* **SIT Key Vault private networking:** SIT has Cosmos private endpoints and the
  documents private DNS zone, but no Key Vault private endpoint or
  `privatelink.vaultcore.azure.net` zone matching PROD.
* **SIT signal-runner identity hardening:** SIT signal runner has the correct
  Event Hubs sender permission but uses a system-assigned identity rather than a
  dedicated UAMI like PROD.
* **PROD storage/ADLS landing zone:** SIT has two locked-down StorageV2 accounts;
  PROD returned no storage accounts in `rg-ihzhhpf-prod`.

### Accepted asymmetries

* **Region:** SIT is westus2 synthetic-only while PROD is Switzerland North GA
  target (F1/F3, ADR-0013).
* **SIT cross-region Foundry:** SIT uses the eastus2 Foundry account
  `ai-ihzhhpf-sit-eastus2`; PROD does not need the split (F4, ADR-0032).
* **SIT simulation runtime:** SIT carries simulation-only Container Apps and
  environments for synthetic testing; PROD does not.

### N/A-per-ADR

* **Fabric IQ ontology:** excluded from GA parity by ADR-0034 and the #270
  Switzerland North preview gate.
