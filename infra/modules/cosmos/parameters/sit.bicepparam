using '../main.bicep'

// Sprint 16 T1 — CSA Cosmos DB (SIT). Demo scope westus2 per ADR-0013.
param environmentName = 'sit'
param solutionShortName = 'ihzhhpf'
param location = 'westus2'

param owner = 'platform-team'
param costCenter = 'ihzhhpf-sit'
param workload = 'hospital-capacity'

// Populated at apply time from the Sprint 13 agent-host managed identity
// principalId. Left empty here so the what-if is deterministic; the deploy
// gate (approved-to-apply) supplies the value.
param agentHostMiPrincipalId = ''

// Concept 1 network plumbing — REQUIRED in SIT because MCAPSGov policies force
// Cosmos publicNetworkAccess=Disabled. Without a private endpoint, no client
// (Fabric, Container Apps, seed scripts) can reach the data plane.
param enablePrivateEndpoint = true
param vnetResourceId = '/subscriptions/66a9953a-df37-4c51-856c-9971b9bf3e03/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.Network/virtualNetworks/vnet-platform-ihzhhpf-sit'
param privateEndpointSubnetName = 'snet-data'
