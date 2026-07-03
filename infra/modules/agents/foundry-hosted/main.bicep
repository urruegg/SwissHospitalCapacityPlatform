// Foundry-hosted runtime agents — Managed Identities + RBAC.
//
// Scope of this module (Sprint 09 v2.0.0 T4.5):
//   * Creates two User-Assigned Managed Identities (UAMIs) that will be
//     attached to the already-provisioned Foundry AI Services resource
//     `ai-ihzhhpf-<env>` (BM-Copilot + CSA agents per design spec §5).
//   * Wires role assignments via ./rbac.bicep so those identities can
//     read the Fabric OneLake gold zone and receive from Event Hubs.
//
// Explicitly OUT of scope for this module:
//   * Creating or updating the Foundry resource itself — that is done
//     by infra/modules/ai-platform/main.bicep. Foundry-agent attachment
//     of these UAMIs is a Foundry-plane action (T4.6 deploy script /
//     manual portal), not a Bicep operation.
//   * Fabric Data Agent identity — workspace-native, no MI needed.
//   * Fabric IQ Reader assignment — workspace-native role, not an
//     Azure RBAC role definition GUID. Deferred to T4.6 deploy script.

@description('Location for the Managed Identities. Region-pinned per ADR-0013.')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param location string = 'westus2'

@description('Environment tag: dev | sit | prod. Only sit/prod are provisioned in Sprint 09 v2.0.0 T4.5; dev is accepted for parent-type compatibility.')
@allowed([
  'dev'
  'sit'
  'prod'
])
param environment string

@description('Solution short name (per AGENTS.md tenant migration note).')
param solutionShortName string = 'ihzhhpf'

@description('Event Hub namespace name (from data-foundation module output when available).')
param eventHubNamespaceName string

@description('Event Hub name (from data-foundation module output when available). Note: on the sprint-09-v2/t4-semantic-agents branch, T2 data-foundation only creates the namespace, not the hub itself — the hub role assignment will be a no-op until T2 merges.')
param eventHubName string

@description('BM-Copilot consumer group name.')
param bmCopilotConsumerGroup string = 'cg-bm-copilot-agent'

@description('CSA consumer group name.')
param csaConsumerGroup string = 'cg-csa-agent'

@description('Common resource tags.')
param tags object = {}

var bmCopilotIdentityName = 'id-bm-copilot-${solutionShortName}-${environment}'
var csaIdentityName = 'id-csa-${solutionShortName}-${environment}'

resource bmCopilotIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: bmCopilotIdentityName
  location: location
  tags: tags
}

resource csaIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: csaIdentityName
  location: location
  tags: tags
}

module rbac './rbac.bicep' = {
  name: 'foundry-agents-rbac-${environment}'
  params: {
    bmCopilotPrincipalId: bmCopilotIdentity.properties.principalId
    csaPrincipalId: csaIdentity.properties.principalId
    eventHubNamespaceName: eventHubNamespaceName
    eventHubName: eventHubName
    bmCopilotConsumerGroup: bmCopilotConsumerGroup
    csaConsumerGroup: csaConsumerGroup
  }
}

output bmCopilotPrincipalId string = bmCopilotIdentity.properties.principalId
output bmCopilotClientId string = bmCopilotIdentity.properties.clientId
output bmCopilotIdentityResourceId string = bmCopilotIdentity.id
output bmCopilotIdentityName string = bmCopilotIdentity.name

output csaPrincipalId string = csaIdentity.properties.principalId
output csaClientId string = csaIdentity.properties.clientId
output csaIdentityResourceId string = csaIdentity.id
output csaIdentityName string = csaIdentity.name

output moduleStatus string = 'foundry-hosted-agents-implemented'
