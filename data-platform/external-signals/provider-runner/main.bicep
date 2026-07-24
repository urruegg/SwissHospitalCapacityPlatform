@description('Environment suffix, e.g. sit or prod')
param envSuffix string
@description('Existing Container Apps managed environment resource id')
param managedEnvironmentId string
@description('Existing Event Hub namespace name (evh-ihzhhpf...)')
param eventHubNamespace string
@description('Event Hub name for external signals')
param eventHubName string
param location string = resourceGroup().location

var appName = 'ca-signal-runner-ihzhhpf-${envSuffix}'
var identityName = 'id-signal-runner-ihzhhpf-${envSuffix}'

// User-Assigned Managed Identity: unlike a SystemAssigned identity (whose
// principalId is minted fresh on every container-app / CAE recreate), a UAMI
// persists as its own resource, so its principalId is stable across recreates.
// This keeps the Event Hubs role assignment fully idempotent — no
// RoleAssignmentUpdateNotPermitted and no orphaned assignments after a
// destructive CAE rebuild.
resource runnerIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: {
    env: envSuffix
    owner: 'urruegg'
    costCenter: 'curavias-platform'
    workload: 'external-signals'
  }
}

resource runner 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  tags: {
    env: envSuffix
    owner: 'urruegg'
    costCenter: 'curavias-platform'
    workload: 'external-signals'
  }
  properties: {
    managedEnvironmentId: managedEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
    }
    template: {
      containers: [
        {
          name: 'provider-runner'
          image: 'mcr.microsoft.com/azure-cli:latest'
          env: [
            { name: 'EVENT_HUB_NAMESPACE', value: eventHubNamespace }
            { name: 'EVENT_HUB_NAME', value: eventHubName }
            { name: 'AZURE_CLIENT_ID', value: runnerIdentity.properties.clientId }
          ]
        }
      ]
      scale: { minReplicas: 0, maxReplicas: 1 }
    }
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${runnerIdentity.id}': {}
    }
  }
}

@description('Azure Event Hubs Data Sender built-in role definition id')
var eventHubsDataSenderRoleId = '2b629674-e913-4c01-ae53-ef4638d8f975'

resource ehNamespace 'Microsoft.EventHub/namespaces@2021-11-01' existing = {
  name: eventHubNamespace
}

resource senderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  // Name is derived from the UAMI's resource id (deterministic, known at the
  // start of deployment) and the UAMI principalId is stable across recreates,
  // so this assignment is idempotent across destructive CAE rebuilds.
  name: guid(ehNamespace.id, runnerIdentity.id, eventHubsDataSenderRoleId)
  scope: ehNamespace
  properties: {
    principalId: runnerIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', eventHubsDataSenderRoleId)
  }
}

output providerRunnerName string = runner.name
output providerRunnerPrincipalId string = runnerIdentity.properties.principalId
output providerRunnerIdentityName string = runnerIdentity.name
