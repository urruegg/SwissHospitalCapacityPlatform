// Sprint 42 ST-2a — subscription-scope RBAC for the PO Agent runtime MI.
// Split out of main.bicep because subscription-scoped roleAssignments cannot
// be declared in a resourceGroup-scoped file (BCP139); this module is
// deployed with `scope: subscription()` from main.bicep's resourceGroup scope.
targetScope = 'subscription'

@description('principalId of the po-agent-runtime managed identity.')
param principalId string

@description('Resource ID of the po-agent-runtime managed identity, used only for guid() name uniqueness.')
param identityResourceId string

@description('Built-in "Reader" role definition ID.')
param readerRoleId string

@description('Built-in "Cost Management Reader" role definition ID.')
param costManagementReaderRoleId string

resource readerRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, identityResourceId, readerRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', readerRoleId)
    principalId: principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 42 — PO Agent runtime MI queries Azure Resource Graph (Class B live-proof, keyless).'
  }
}

resource costManagementReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, identityResourceId, costManagementReaderRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', costManagementReaderRoleId)
    principalId: principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 42 — PO Agent runtime MI queries Cost Management (Class C cost reconciliation, keyless).'
  }
}
