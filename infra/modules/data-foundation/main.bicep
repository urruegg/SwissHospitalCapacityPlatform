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

@description('Sprint 23 WS-A4 (ADR-0043) — provision a dedicated per-domain skills-events Event Hub entity + cg-skills-eventstream consumer group. Enabled by the parent when the skills lane runs in sourceMode=EventHub.')
param enableSkillsEventHub bool = false

module eventhubs './eventhubs/main.bicep' = {
  name: 'data-foundation-eventhubs-${nameSuffix}'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
    simulatorMiPrincipalId: simulatorMiPrincipalId
    bmCopilotMiPrincipalId: bmCopilotMiPrincipalId
    csaAgentMiPrincipalId: csaAgentMiPrincipalId
    enableSkillsEventHub: enableSkillsEventHub
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

@description('Sprint 23 WS-A4 (ADR-0043) — dedicated skills-events Event Hub entity name, or empty when not enabled.')
output skillsEventHubName string = eventhubs.outputs.skillsEventHubName

@description('Sprint 23 WS-A4 (ADR-0043) — dedicated skills-events consumer group name, or empty when not enabled.')
output skillsEventHubConsumerGroup string = eventhubs.outputs.skillsEventHubConsumerGroup
