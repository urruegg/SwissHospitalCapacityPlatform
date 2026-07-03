@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Object ID of the simulator managed identity for Event Hubs Data Sender (Sprint 09 T3.7 wiring).')
param simulatorMiPrincipalId string = ''

@description('Object ID of the BM-Copilot managed identity for Event Hubs Data Receiver (Sprint 09 T4.5 wiring).')
param bmCopilotMiPrincipalId string = ''

@description('Object ID of the CSA managed identity for Event Hubs Data Receiver (Sprint 09 T4.5 wiring).')
param csaAgentMiPrincipalId string = ''

module eventhubs './eventhubs/main.bicep' = {
  name: 'data-foundation-eventhubs-${nameSuffix}'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
    simulatorMiPrincipalId: simulatorMiPrincipalId
    bmCopilotMiPrincipalId: bmCopilotMiPrincipalId
    csaAgentMiPrincipalId: csaAgentMiPrincipalId
  }
}

@description('Data foundation module implementation marker.')
output moduleStatus string = 'data-foundation-implemented'

@description('Event Hub namespace name.')
output eventHubNamespaceName string = eventhubs.outputs.eventHubNamespaceName

@description('Fully qualified Event Hub namespace endpoint (<name>.servicebus.windows.net).')
output eventHubNamespaceEndpoint string = eventhubs.outputs.eventHubNamespaceEndpoint

@description('Event Hub name inside the namespace.')
output eventHubName string = eventhubs.outputs.eventHubName

@description('Sprint 09 v2.0.0 consumer group names.')
output eventHubConsumerGroupNames object = eventhubs.outputs.consumerGroupNames
