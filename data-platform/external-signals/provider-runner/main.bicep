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
          ]
        }
      ]
      scale: { minReplicas: 0, maxReplicas: 1 }
    }
  }
  identity: { type: 'SystemAssigned' }
}

@description('Azure Event Hubs Data Sender built-in role definition id')
var eventHubsDataSenderRoleId = '2b629674-e913-4c01-ae53-ef4638d8f975'

resource ehNamespace 'Microsoft.EventHub/namespaces@2021-11-01' existing = {
  name: eventHubNamespace
}

resource senderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(ehNamespace.id, runner.id, eventHubsDataSenderRoleId)
  scope: ehNamespace
  properties: {
    principalId: runner.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', eventHubsDataSenderRoleId)
  }
}

output providerRunnerName string = runner.name
output providerRunnerPrincipalId string = runner.identity.principalId
