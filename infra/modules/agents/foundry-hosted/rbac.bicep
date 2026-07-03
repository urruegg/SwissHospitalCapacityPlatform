// Role assignments for Foundry-hosted runtime agents (BM-Copilot + CSA).
//
// Per Sprint 09 v2.0.0 design spec §5.4:
//
//   | Principal      | Role                            | Scope                                  |
//   | -------------- | ------------------------------- | -------------------------------------- |
//   | BM-Copilot MI  | Storage Blob Data Reader        | Fabric gold storage (RG-scoped here)   |
//   | BM-Copilot MI  | Azure Event Hubs Data Receiver  | `cg-bm-copilot-agent` consumer group   |
//   | CSA MI         | Storage Blob Data Reader        | Fabric gold storage (RG-scoped here)   |
//   | CSA MI         | Azure Event Hubs Data Receiver  | `cg-csa-agent` consumer group          |
//
// Notes:
//   * `Fabric IQ Reader` from design spec §5.4 is a Fabric workspace-native
//     role, NOT an Azure RBAC role definition. It is deferred to the T4.6
//     deploy script (`data-platform/scripts/deploy_fabric_data_agent.py`)
//     or a manual portal step. We do NOT invent a GUID for it here.
//   * Storage Blob Data Reader is scoped at the resource group level
//     because the gold storage account name is not exposed as a public
//     output from the data-foundation module on the current branch.
//     When the storage account is exposed post-merge, narrow the scope
//     to the storage account resource.
//   * Event Hubs Data Receiver is scoped at the Event Hub level (parent
//     of the consumer group) with a TODO to narrow to the consumer group
//     itself once the T2 branch (`sprint-09-v2/t2-ingestion`) merges the
//     Event Hub + consumer group resources into `infra/modules/data-foundation/`.

@description('Principal ID (object ID) of the BM-Copilot managed identity.')
param bmCopilotPrincipalId string

@description('Principal ID (object ID) of the CSA managed identity.')
param csaPrincipalId string

@description('Event Hub namespace name (existing).')
param eventHubNamespaceName string

@description('Event Hub name (existing, child of the namespace).')
param eventHubName string

@description('BM-Copilot consumer group name. Reserved for T2-merge scope narrowing.')
#disable-next-line no-unused-params
param bmCopilotConsumerGroup string

@description('CSA consumer group name. Reserved for T2-merge scope narrowing.')
#disable-next-line no-unused-params
param csaConsumerGroup string

// Built-in role definition GUIDs (documented, never invented).
// https://learn.microsoft.com/azure/role-based-access-control/built-in-roles
var storageBlobDataReaderRoleId = '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
var eventHubsDataReceiverRoleId = 'a638d3c7-ab3a-418d-83e6-5f17a39d4fde'

// Existing Event Hubs references. Bicep resolves these to resource IDs at
// compile time. If the namespace / hub does not yet exist on the target
// subscription (T2 not merged), Azure will surface this at what-if / apply
// time — expected and documented in the module main.bicep header.
resource ehNamespace 'Microsoft.EventHub/namespaces@2024-01-01' existing = {
  name: eventHubNamespaceName
}

resource eventHub 'Microsoft.EventHub/namespaces/eventhubs@2024-01-01' existing = {
  name: eventHubName
  parent: ehNamespace
}

// -------------------------------------------------------------------------
// BM-Copilot MI role assignments
// -------------------------------------------------------------------------

resource bmCopilotStorageReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, bmCopilotPrincipalId, storageBlobDataReaderRoleId)
  properties: {
    principalId: bmCopilotPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataReaderRoleId)
  }
}

// TODO(T2 merge): narrow scope to the `cg-bm-copilot-agent` consumer group
// (Microsoft.EventHub/namespaces/eventhubs/consumergroups) once T2 provisions it.
resource bmCopilotEventHubsReceiver 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(eventHub.id, bmCopilotPrincipalId, eventHubsDataReceiverRoleId)
  scope: eventHub
  properties: {
    principalId: bmCopilotPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', eventHubsDataReceiverRoleId)
  }
}

// -------------------------------------------------------------------------
// CSA MI role assignments
// -------------------------------------------------------------------------

resource csaStorageReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, csaPrincipalId, storageBlobDataReaderRoleId)
  properties: {
    principalId: csaPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataReaderRoleId)
  }
}

// TODO(T2 merge): narrow scope to the `cg-csa-agent` consumer group.
resource csaEventHubsReceiver 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(eventHub.id, csaPrincipalId, eventHubsDataReceiverRoleId)
  scope: eventHub
  properties: {
    principalId: csaPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', eventHubsDataReceiverRoleId)
  }
}

output moduleStatus string = 'foundry-hosted-agents-rbac-implemented'
