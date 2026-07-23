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

output providerRunnerName string = runner.name
