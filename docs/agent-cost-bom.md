# Agent Cost - Full Azure BOM (subscription 1)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | n/a |

## Purpose

Full Bill of Materials (BOM) for subscription 1
(`66a9953a-df37-4c51-856c-9971b9bf3e03`, `ME-MngEnvMCAP164444-urruegg-1`),
the subscription that hosts the SIT and PROD `ihzhhpf` resources. This annex
supports the Total Cost of Ownership (TCO) view in
[agent_cost.md](agent_cost.md) and the [BVA](BVA.md) ROI/TCO model. Snapshot
date: 2026-07-28.

## Resource count by type

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

## Resource count by resource group

| Resource group | Count |
| --- | ---: |
| rg-ihzhhpf-sit | 65 |
| rg-ihzhhpf-prod | 65 |
| Default-ActivityLogAlerts | 3 |
| NetworkWatcherRG | 3 |
| ME_cae-ihzhhpf-sit_rg-ihzhhpf-sit_westus2 | 2 |
| ME_cae-ihzhhpf-prod_rg-ihzhhpf-prod_switzerlandnorth | 2 |
| McapsGovernance | 1 |
| mcapsgovernance | 1 |
| ai_appi-ihzhhpf-sit_6d4c4097-c035-4807-af20-28aedbc5ee70_managed | 1 |
| ai_appi-ihzhhpf-prod_57eff6c4-1492-41a7-96eb-b78f37cfb36b_managed | 1 |
| **Total** | **144** |

## Full resource inventory (144 resources)

Type is shown without the `Microsoft.`/`microsoft.` provider prefix. `-` means
the property is not set on the resource.

| Resource group | Resource | Type | Location | SKU |
| --- | --- | --- | --- | --- |
| Default-ActivityLogAlerts | admin-4376-resource | CognitiveServices/accounts | swedencentral | S0 |
| Default-ActivityLogAlerts | admin-4376-resource/admin-4376 | CognitiveServices/accounts/projects | swedencentral | - |
| Default-ActivityLogAlerts | AGOwner | Insights/actiongroups | global | - |
| ME_cae-ihzhhpf-prod_rg-ihzhhpf-prod_switzerlandnorth | capp-svc-lb | Network/loadBalancers | switzerlandnorth | Standard |
| ME_cae-ihzhhpf-prod_rg-ihzhhpf-prod_switzerlandnorth | capp-svc-lb-ip | Network/publicIPAddresses | switzerlandnorth | Standard |
| ME_cae-ihzhhpf-sit_rg-ihzhhpf-sit_westus2 | capp-svc-lb | Network/loadBalancers | westus2 | Standard |
| ME_cae-ihzhhpf-sit_rg-ihzhhpf-sit_westus2 | capp-svc-lb-ip | Network/publicIPAddresses | westus2 | Standard |
| McapsGovernance | mcaps856c9971b9bf3e03 | Storage/storageAccounts | westus2 | Standard_LRS |
| NetworkWatcherRG | NetworkWatcher_eastus2 | Network/networkWatchers | eastus2 | - |
| NetworkWatcherRG | NetworkWatcher_switzerlandnorth | Network/networkWatchers | switzerlandnorth | - |
| NetworkWatcherRG | NetworkWatcher_westus2 | Network/networkWatchers | westus2 | - |
| ai_appi-ihzhhpf-prod_57eff6c4-1492-41a7-96eb-b78f37cfb36b_managed | managed-appi-ihzhhpf-prod-ws | operationalinsights/workspaces | switzerlandnorth | - |
| ai_appi-ihzhhpf-sit_6d4c4097-c035-4807-af20-28aedbc5ee70_managed | managed-appi-ihzhhpf-sit-ws | operationalinsights/workspaces | westus2 | - |
| mcapsgovernance | mcaps856c9971b9bf3e03-4ad4e3d1-34cb-4bb8-a9eb-49c748410779 | EventGrid/systemTopics | westus2 | - |
| rg-ihzhhpf-prod | ca-agent-host-ihzhhpf-prod | App/containerApps | switzerlandnorth | - |
| rg-ihzhhpf-prod | ca-app-fluent-ihzhhpf-prod | App/containerApps | switzerlandnorth | - |
| rg-ihzhhpf-prod | ca-po-ihzhhpf-prod | App/containerApps | switzerlandnorth | - |
| rg-ihzhhpf-prod | ca-signal-runner-ihzhhpf-prod | App/containerApps | switzerlandnorth | - |
| rg-ihzhhpf-prod | ca-sim-capacity-ihzhhpf-prod | App/containerApps | switzerlandnorth | - |
| rg-ihzhhpf-prod | caj-po-refresh-ihzhhpf-prod | App/jobs | switzerlandnorth | - |
| rg-ihzhhpf-prod | caj-sk-lms-ihzhhpf-prod | App/jobs | switzerlandnorth | - |
| rg-ihzhhpf-prod | caj-sk-sf-ihzhhpf-prod | App/jobs | switzerlandnorth | - |
| rg-ihzhhpf-prod | caj-sk-skm-ihzhhpf-prod | App/jobs | switzerlandnorth | - |
| rg-ihzhhpf-prod | caj-sk-wid-ihzhhpf-prod | App/jobs | switzerlandnorth | - |
| rg-ihzhhpf-prod | cae-app-fluent-ihzhhpf-prod | App/managedEnvironments | switzerlandnorth | - |
| rg-ihzhhpf-prod | cae-ihzhhpf-prod | App/managedEnvironments | switzerlandnorth | - |
| rg-ihzhhpf-prod | cae-po-ihzhhpf-prod | App/managedEnvironments | switzerlandnorth | - |
| rg-ihzhhpf-prod | cae-sim-ihzhhpf-prod | App/managedEnvironments | switzerlandnorth | - |
| rg-ihzhhpf-prod | cae-skills-sim-ihzhhpf-prod | App/managedEnvironments | switzerlandnorth | - |
| rg-ihzhhpf-prod | cae-app-fluent-ihzhhpf-prod/cert-app-curavias-ch | App/managedEnvironments/managedCertificates | switzerlandnorth | - |
| rg-ihzhhpf-prod | ai-ihzhhpf-prod | CognitiveServices/accounts | switzerlandnorth | S0 |
| rg-ihzhhpf-prod | oai-poihzhhpfprod | CognitiveServices/accounts | switzerlandnorth | S0 |
| rg-ihzhhpf-prod | ai-ihzhhpf-prod/ai-ihzhhpf-prod-project | CognitiveServices/accounts/projects | switzerlandnorth | - |
| rg-ihzhhpf-prod | crihzhhpfprod | ContainerRegistry/registries | switzerlandnorth | Basic |
| rg-ihzhhpf-prod | cosmos-csa-ihzhhpf-prod | DocumentDB/databaseAccounts | switzerlandnorth | - |
| rg-ihzhhpf-prod | cosmos-ihzhhpf-prod | DocumentDB/databaseAccounts | switzerlandnorth | - |
| rg-ihzhhpf-prod | cosmos-po-ihzhhpf-prod | DocumentDB/databaseAccounts | switzerlandnorth | - |
| rg-ihzhhpf-prod | stcorpusihzhhpfprod-07688abd-1c9f-46f0-992a-42243a0d3560 | EventGrid/systemTopics | switzerlandnorth | - |
| rg-ihzhhpf-prod | stdpihzhhpfprodi62t-7d1b2605-f365-40c0-aebd-009e2a850a00 | EventGrid/systemTopics | switzerlandnorth | - |
| rg-ihzhhpf-prod | stmasterdataihzhhpfprod-c354b180-f48c-460f-9f36-baf92a7b46e6 | EventGrid/systemTopics | switzerlandnorth | - |
| rg-ihzhhpf-prod | stmediaihzhhpfprod-e117714a-388f-4194-83b0-c0bafc3dc0be | EventGrid/systemTopics | switzerlandnorth | - |
| rg-ihzhhpf-prod | evh-ihzhhpf-prod-i62t | EventHub/namespaces | switzerlandnorth | Standard |
| rg-ihzhhpf-prod | fabricihzhhpfprod | Fabric/capacities | switzerlandnorth | F2 |
| rg-ihzhhpf-prod | appi-ihzhhpf-prod | Insights/components | switzerlandnorth | - |
| rg-ihzhhpf-prod | kv-ihzhhpf-prod-swn1 | KeyVault/vaults | switzerlandnorth | - |
| rg-ihzhhpf-prod | kvpoihzhhpfprod | KeyVault/vaults | switzerlandnorth | - |
| rg-ihzhhpf-prod | logic-ihzhhpf-prod | Logic/workflows | switzerlandnorth | - |
| rg-ihzhhpf-prod | mlw-ihzhhpf-prod | MachineLearningServices/workspaces | switzerlandnorth | Basic |
| rg-ihzhhpf-prod | id-bm-copilot-ihzhhpf-prod | ManagedIdentity/userAssignedIdentities | switzerlandnorth | - |
| rg-ihzhhpf-prod | id-ca-agent-host-ihzhhpf-prod | ManagedIdentity/userAssignedIdentities | switzerlandnorth | - |
| rg-ihzhhpf-prod | id-ca-app-fluent-ihzhhpf-prod | ManagedIdentity/userAssignedIdentities | switzerlandnorth | - |
| rg-ihzhhpf-prod | id-ca-sim-capacity-ihzhhpf-prod | ManagedIdentity/userAssignedIdentities | switzerlandnorth | - |
| rg-ihzhhpf-prod | id-csa-ihzhhpf-prod | ManagedIdentity/userAssignedIdentities | switzerlandnorth | - |
| rg-ihzhhpf-prod | id-platform-ihzhhpf-prod | ManagedIdentity/userAssignedIdentities | switzerlandnorth | - |
| rg-ihzhhpf-prod | id-po-ihzhhpf-prod | ManagedIdentity/userAssignedIdentities | switzerlandnorth | - |
| rg-ihzhhpf-prod | id-signal-runner-ihzhhpf-prod | ManagedIdentity/userAssignedIdentities | switzerlandnorth | - |
| rg-ihzhhpf-prod | id-skills-sim-ihzhhpf-prod | ManagedIdentity/userAssignedIdentities | switzerlandnorth | - |
| rg-ihzhhpf-prod | pe-cosmos-csa-ihzhhpf-prod.nic.78eb94da-cdfc-43b4-99fb-930ecf410ad1 | Network/networkInterfaces | switzerlandnorth | - |
| rg-ihzhhpf-prod | pe-cosmos-ihzhhpf-prod.nic.44601a91-a48e-4fbb-b031-67ab721709cd | Network/networkInterfaces | switzerlandnorth | - |
| rg-ihzhhpf-prod | pe-kv-ihzhhpf-prod-swn1.nic.17841e2a-760d-4212-bc54-3439b77b0dcf | Network/networkInterfaces | switzerlandnorth | - |
| rg-ihzhhpf-prod | vnet-platform-ihzhhpf-prod-snet-app-nsg-switzerlandnorth | Network/networkSecurityGroups | switzerlandnorth | - |
| rg-ihzhhpf-prod | vnet-platform-ihzhhpf-prod-snet-cae-nsg-switzerlandnorth | Network/networkSecurityGroups | switzerlandnorth | - |
| rg-ihzhhpf-prod | vnet-platform-ihzhhpf-prod-snet-data-nsg-switzerlandnorth | Network/networkSecurityGroups | switzerlandnorth | - |
| rg-ihzhhpf-prod | privatelink.documents.azure.com | Network/privateDnsZones | global | - |
| rg-ihzhhpf-prod | privatelink.vaultcore.azure.net | Network/privateDnsZones | global | - |
| rg-ihzhhpf-prod | privatelink.documents.azure.com/vnet-platform-ihzhhpf-prod-link | Network/privateDnsZones/virtualNetworkLinks | global | - |
| rg-ihzhhpf-prod | privatelink.vaultcore.azure.net/vnet-platform-ihzhhpf-prod-link | Network/privateDnsZones/virtualNetworkLinks | global | - |
| rg-ihzhhpf-prod | pe-cosmos-csa-ihzhhpf-prod | Network/privateEndpoints | switzerlandnorth | - |
| rg-ihzhhpf-prod | pe-cosmos-ihzhhpf-prod | Network/privateEndpoints | switzerlandnorth | - |
| rg-ihzhhpf-prod | pe-kv-ihzhhpf-prod-swn1 | Network/privateEndpoints | switzerlandnorth | - |
| rg-ihzhhpf-prod | vnet-platform-ihzhhpf-prod | Network/virtualNetworks | switzerlandnorth | - |
| rg-ihzhhpf-prod | log-ihzhhpf-prod | OperationalInsights/workspaces | switzerlandnorth | - |
| rg-ihzhhpf-prod | srch-ihzhhpf-prod | Search/searchServices | switzerlandnorth | standard |
| rg-ihzhhpf-prod | sb-ihzhhpf-prod-i62t | ServiceBus/namespaces | switzerlandnorth | Standard |
| rg-ihzhhpf-prod | stcorpusihzhhpfprod | Storage/storageAccounts | switzerlandnorth | Standard_LRS |
| rg-ihzhhpf-prod | stdpihzhhpfprodi62t | Storage/storageAccounts | switzerlandnorth | Standard_LRS |
| rg-ihzhhpf-prod | stmasterdataihzhhpfprod | Storage/storageAccounts | switzerlandnorth | Standard_LRS |
| rg-ihzhhpf-prod | stmediaihzhhpfprod | Storage/storageAccounts | switzerlandnorth | Standard_LRS |
| rg-ihzhhpf-prod | stapp-ihzhhpf-prod | Web/staticSites | westeurope | Standard |
| rg-ihzhhpf-sit | ca-agent-host-ihzhhpf-sit | App/containerApps | westus2 | - |
| rg-ihzhhpf-sit | ca-app-fluent-ihzhhpf-sit | App/containerApps | westus2 | - |
| rg-ihzhhpf-sit | ca-po-ihzhhpf-sit | App/containerApps | westus2 | - |
| rg-ihzhhpf-sit | ca-signal-runner-ihzhhpf-sit | App/containerApps | westus2 | - |
| rg-ihzhhpf-sit | ca-sim-capacity-ihzhhpf-sit | App/containerApps | westus2 | - |
| rg-ihzhhpf-sit | caj-decision-apply-ihzhhpf-sit | App/jobs | westus2 | - |
| rg-ihzhhpf-sit | caj-po-refresh-ihzhhpf-sit | App/jobs | westus2 | - |
| rg-ihzhhpf-sit | caj-sk-lms-ihzhhpf-sit | App/jobs | westus2 | - |
| rg-ihzhhpf-sit | caj-sk-sf-ihzhhpf-sit | App/jobs | westus2 | - |
| rg-ihzhhpf-sit | caj-sk-skm-ihzhhpf-sit | App/jobs | westus2 | - |
| rg-ihzhhpf-sit | caj-sk-wid-ihzhhpf-sit | App/jobs | westus2 | - |
| rg-ihzhhpf-sit | cae-app-fluent-ihzhhpf-sit | App/managedEnvironments | westus2 | - |
| rg-ihzhhpf-sit | cae-ihzhhpf-sit | App/managedEnvironments | westus2 | - |
| rg-ihzhhpf-sit | cae-po-ihzhhpf-sit | App/managedEnvironments | westus2 | - |
| rg-ihzhhpf-sit | cae-sim-ihzhhpf-sit | App/managedEnvironments | westus2 | - |
| rg-ihzhhpf-sit | cae-skills-sim-ihzhhpf-sit | App/managedEnvironments | westus2 | - |
| rg-ihzhhpf-sit | cae-app-fluent-ihzhhpf-sit/cert-appsit-curavias-ch | App/managedEnvironments/managedCertificates | westus2 | - |
| rg-ihzhhpf-sit | ai-ihzhhpf-sit | CognitiveServices/accounts | westus2 | S0 |
| rg-ihzhhpf-sit | ai-ihzhhpf-sit-eastus2 | CognitiveServices/accounts | eastus2 | S0 |
| rg-ihzhhpf-sit | oai-poihzhhpfsit | CognitiveServices/accounts | eastus2 | S0 |
| rg-ihzhhpf-sit | ai-ihzhhpf-sit-eastus2/ai-ihzhhpf-sit-eastus2-project | CognitiveServices/accounts/projects | eastus2 | - |
| rg-ihzhhpf-sit | ai-ihzhhpf-sit/ai-ihzhhpf-sit-project | CognitiveServices/accounts/projects | westus2 | - |
| rg-ihzhhpf-sit | cri75lbu5sj4hza | ContainerRegistry/registries | westus2 | Standard |
| rg-ihzhhpf-sit | cosmos-csa-ihzhhpf-sit | DocumentDB/databaseAccounts | westus2 | - |
| rg-ihzhhpf-sit | cosmos-ihzhhpf-sit | DocumentDB/databaseAccounts | westus2 | - |
| rg-ihzhhpf-sit | cosmos-po-ihzhhpf-sit | DocumentDB/databaseAccounts | westus2 | - |
| rg-ihzhhpf-sit | stcorpusihzhhpfsit-7471eaae-422e-4650-bce6-ed3078822ecf | EventGrid/systemTopics | westus2 | - |
| rg-ihzhhpf-sit | stdpihzhhpfsity26y-46ed72d1-4ecb-4ac6-95e2-5ceadf82f231 | EventGrid/systemTopics | westus2 | - |
| rg-ihzhhpf-sit | stmasterdataihzhhpfsit-8c652455-8ca4-4a93-8088-231519da264c | EventGrid/systemTopics | westus2 | - |
| rg-ihzhhpf-sit | evh-ihzhhpf-sit-y26y | EventHub/namespaces | westus2 | Standard |
| rg-ihzhhpf-sit | fabricihzhhpfsit | Fabric/capacities | westus2 | F2 |
| rg-ihzhhpf-sit | appi-ihzhhpf-sit | Insights/components | westus2 | - |
| rg-ihzhhpf-sit | kv-ihzhhpf-sit-y26y | KeyVault/vaults | westus2 | - |
| rg-ihzhhpf-sit | kvpoihzhhpfsit | KeyVault/vaults | westus2 | - |
| rg-ihzhhpf-sit | logic-ihzhhpf-sit | Logic/workflows | westus2 | - |
| rg-ihzhhpf-sit | mlw-ihzhhpf-sit | MachineLearningServices/workspaces | westus2 | Basic |
| rg-ihzhhpf-sit | id-api-ihzhhpf-sit | ManagedIdentity/userAssignedIdentities | westus2 | - |
| rg-ihzhhpf-sit | id-bm-copilot-ihzhhpf-sit | ManagedIdentity/userAssignedIdentities | westus2 | - |
| rg-ihzhhpf-sit | id-ca-agent-host-ihzhhpf-sit | ManagedIdentity/userAssignedIdentities | westus2 | - |
| rg-ihzhhpf-sit | id-ca-app-fluent-ihzhhpf-sit | ManagedIdentity/userAssignedIdentities | westus2 | - |
| rg-ihzhhpf-sit | id-ca-sim-capacity-ihzhhpf-sit | ManagedIdentity/userAssignedIdentities | westus2 | - |
| rg-ihzhhpf-sit | id-csa-ihzhhpf-sit | ManagedIdentity/userAssignedIdentities | westus2 | - |
| rg-ihzhhpf-sit | id-platform-ihzhhpf-sit | ManagedIdentity/userAssignedIdentities | westus2 | - |
| rg-ihzhhpf-sit | id-po-ihzhhpf-sit | ManagedIdentity/userAssignedIdentities | westus2 | - |
| rg-ihzhhpf-sit | id-skills-sim-ihzhhpf-sit | ManagedIdentity/userAssignedIdentities | westus2 | - |
| rg-ihzhhpf-sit | curavias.ch | Network/dnszones | global | - |
| rg-ihzhhpf-sit | pe-cosmos-csa-ihzhhpf-sit.nic.22fe0ab9-17b1-4632-858f-37a6e643a1cd | Network/networkInterfaces | westus2 | - |
| rg-ihzhhpf-sit | pe-cosmos-ihzhhpf-sit.nic.4a4b35cc-f649-4b5d-8624-4011b75ebf8a | Network/networkInterfaces | westus2 | - |
| rg-ihzhhpf-sit | vnet-platform-ihzhhpf-sit-snet-app-nsg-westus2 | Network/networkSecurityGroups | westus2 | - |
| rg-ihzhhpf-sit | vnet-platform-ihzhhpf-sit-snet-cae-nsg-westus2 | Network/networkSecurityGroups | westus2 | - |
| rg-ihzhhpf-sit | vnet-platform-ihzhhpf-sit-snet-data-nsg-westus2 | Network/networkSecurityGroups | westus2 | - |
| rg-ihzhhpf-sit | privatelink.documents.azure.com | Network/privateDnsZones | global | - |
| rg-ihzhhpf-sit | privatelink.documents.azure.com/vnet-platform-ihzhhpf-sit-link | Network/privateDnsZones/virtualNetworkLinks | global | - |
| rg-ihzhhpf-sit | pe-cosmos-csa-ihzhhpf-sit | Network/privateEndpoints | westus2 | - |
| rg-ihzhhpf-sit | pe-cosmos-ihzhhpf-sit | Network/privateEndpoints | westus2 | - |
| rg-ihzhhpf-sit | vnet-platform-ihzhhpf-sit | Network/virtualNetworks | westus2 | - |
| rg-ihzhhpf-sit | log-ihzhhpf-sit | OperationalInsights/workspaces | westus2 | - |
| rg-ihzhhpf-sit | srch-ihzhhpf-sit | Search/searchServices | westus2 | standard |
| rg-ihzhhpf-sit | sb-ihzhhpf-sit-y26y | ServiceBus/namespaces | westus2 | Standard |
| rg-ihzhhpf-sit | stcorpusihzhhpfsit | Storage/storageAccounts | westus2 | Standard_LRS |
| rg-ihzhhpf-sit | stdpihzhhpfsity26y | Storage/storageAccounts | westus2 | Standard_LRS |
| rg-ihzhhpf-sit | stmasterdataihzhhpfsit | Storage/storageAccounts | westus2 | Standard_LRS |
| rg-ihzhhpf-sit | asp-platform-ihzhhpf-sit | Web/serverFarms | westus2 | B1 |
| rg-ihzhhpf-sit | app-platform-ihzhhpf-sit-y26y | Web/sites | westus2 | - |
| rg-ihzhhpf-sit | Application Insights Smart Detection | insights/actiongroups | global | - |
