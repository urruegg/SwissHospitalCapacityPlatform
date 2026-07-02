@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

resource logicWorkflow 'Microsoft.Logic/workflows@2019-05-01' = {
  name: 'logic-${nameSuffix}'
  location: location
  tags: tags
  properties: {
    state: 'Disabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      parameters: {}
      triggers: {}
      actions: {}
      outputs: {}
    }
    parameters: {}
  }
}

@description('Integration orchestration module implementation marker.')
output moduleStatus string = 'integration-orchestration-implemented'

@description('Logic App workflow name.')
output logicWorkflowName string = logicWorkflow.name
