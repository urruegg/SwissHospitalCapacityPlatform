// Sprint 09 v2.0.0 T2.1 — Event Hub namespace + event hub + Sprint 09 consumer groups + RBAC.
// Grounds design spec §4.2 (EH topology). Refactors the previous inline namespace-only definition
// from data-foundation/main.bicep into a proper submodule so consumer groups can be attached as
// child resources and MI role assignments can be scoped precisely.

@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Name of the event hub within the namespace. Matches design spec §4.2 (single-hub topology, routing by eventKind message property).')
param eventHubName string = 'events'

@description('Object ID of the simulator managed identity. When set, receives Azure Event Hubs Data Sender on the namespace. Wired from apps/sim-capacity (Sprint 09 T3.7).')
param simulatorMiPrincipalId string = ''

@description('Object ID of the BM-Copilot managed identity. When set, receives Azure Event Hubs Data Receiver scoped to cg-bm-copilot-agent. Wired from Foundry module (Sprint 09 T4.5).')
param bmCopilotMiPrincipalId string = ''

@description('Object ID of the CSA (Capacity Simulation Agent) managed identity. When set, receives Azure Event Hubs Data Receiver scoped to cg-csa-agent. Wired from Foundry module (Sprint 09 T4.5).')
param csaAgentMiPrincipalId string = ''

// Event Hub namespaces need globally unique DNS names (<ns>.servicebus.windows.net).
var globalUniquenessSuffix = take(uniqueString(subscription().subscriptionId, resourceGroup().id), 4)

// Built-in role definition IDs (verified 2026-07-03 against Azure docs).
// Source: https://learn.microsoft.com/azure/role-based-access-control/built-in-roles/analytics#azure-event-hubs-data-sender
var eventHubsDataSenderRoleId = '2b629674-e913-4c01-ae53-ef4638d8f975'
var eventHubsDataReceiverRoleId = 'a638d3c7-ab3a-418d-83e6-5f17a39d4fde'

resource eventHubNamespace 'Microsoft.EventHub/namespaces@2022-10-01-preview' = {
  name: 'evh-${nameSuffix}-${globalUniquenessSuffix}'
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Standard'
    capacity: 1
  }
  properties: {
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
  }
}

resource eventHub 'Microsoft.EventHub/namespaces/eventhubs@2022-10-01-preview' = {
  parent: eventHubNamespace
  name: eventHubName
  properties: {
    partitionCount: 4
    messageRetentionInDays: 1
  }
}

// Sprint 09 v2.0.0 consumer groups per design spec §4.2.
resource cgFabricEventstream 'Microsoft.EventHub/namespaces/eventhubs/consumergroups@2022-10-01-preview' = {
  parent: eventHub
  name: 'cg-fabric-eventstream'
  properties: {
    userMetadata: 'Sprint 09 v2.0.0 — consumed by Fabric Eventstream (T2.2). Drives bronze/eventstream/ Delta append.'
  }
}

resource cgBmCopilotAgent 'Microsoft.EventHub/namespaces/eventhubs/consumergroups@2022-10-01-preview' = {
  parent: eventHub
  name: 'cg-bm-copilot-agent'
  properties: {
    userMetadata: 'Sprint 09 v2.0.0 — consumed by BM-Copilot (Foundry) for bed-management context (T4.5).'
  }
}

resource cgCsaAgent 'Microsoft.EventHub/namespaces/eventhubs/consumergroups@2022-10-01-preview' = {
  parent: eventHub
  name: 'cg-csa-agent'
  properties: {
    userMetadata: 'Sprint 09 v2.0.0 — consumed by CSA (Capacity Simulation Agent, Foundry) for advisory what-if (T4.5).'
  }
}

// RBAC — Simulator MI: Data Sender on the event hub (scoped as tightly as the Data Sender role permits;
// Event Hubs data-plane roles apply at the hub or namespace scope, not per consumer group).
resource simulatorSenderRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(simulatorMiPrincipalId)) {
  scope: eventHub
  name: guid(eventHub.id, simulatorMiPrincipalId, eventHubsDataSenderRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', eventHubsDataSenderRoleId)
    principalId: simulatorMiPrincipalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 09 v2.0.0 T2.1 — simulator MI publishes events per design spec §4.2.'
  }
}

// RBAC — BM-Copilot MI: Data Receiver. Note: Event Hubs data-plane roles cannot be scoped to a consumer group
// (Azure ARM authorization boundary stops at the event hub); scoping is at the hub level. The consumer-group
// binding is enforced at the client (SDK) layer by connecting with cg-bm-copilot-agent.
resource bmCopilotReceiverRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(bmCopilotMiPrincipalId)) {
  scope: eventHub
  name: guid(eventHub.id, bmCopilotMiPrincipalId, eventHubsDataReceiverRoleId, 'cg-bm-copilot-agent')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', eventHubsDataReceiverRoleId)
    principalId: bmCopilotMiPrincipalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 09 v2.0.0 T2.1 — BM-Copilot MI receives from cg-bm-copilot-agent (client-enforced binding).'
  }
}

resource csaAgentReceiverRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(csaAgentMiPrincipalId)) {
  scope: eventHub
  name: guid(eventHub.id, csaAgentMiPrincipalId, eventHubsDataReceiverRoleId, 'cg-csa-agent')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', eventHubsDataReceiverRoleId)
    principalId: csaAgentMiPrincipalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 09 v2.0.0 T2.1 — CSA MI receives from cg-csa-agent (client-enforced binding).'
  }
}

@description('Event Hub namespace name.')
output eventHubNamespaceName string = eventHubNamespace.name

@description('Fully qualified Event Hub namespace endpoint (<name>.servicebus.windows.net).')
output eventHubNamespaceEndpoint string = replace(replace(eventHubNamespace.properties.serviceBusEndpoint, 'https://', ''), ':443/', '')

@description('Event Hub name inside the namespace.')
output eventHubName string = eventHub.name

@description('Names of the three Sprint 09 v2.0.0 consumer groups.')
output consumerGroupNames object = {
  fabricEventstream: cgFabricEventstream.name
  bmCopilotAgent: cgBmCopilotAgent.name
  csaAgent: cgCsaAgent.name
}

@description('Event Hubs submodule implementation marker.')
output moduleStatus string = 'eventhubs-implemented'
