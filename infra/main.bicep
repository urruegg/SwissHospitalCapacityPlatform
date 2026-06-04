targetScope = 'resourceGroup'

// No-op change for workflow gate dry-run validation.

@description('Deployment environment name.')
@allowed([
  'dev'
  'sit'
  'prod'
])
param environmentName string

@description('Solution short name used in Azure resource names.')
param solutionShortName string = 'chhealthpf'

@description('Location for all resources. Defaults to resource group location.')
param location string = resourceGroup().location

@description('Owner tag value.')
param owner string = 'platform-team'

@description('Cost center tag value.')
param costCenter string = 'tbd'

@description('Workload tag value.')
param workload string = 'hospital-capacity'

@description('Optional Log Analytics retention in days.')
@minValue(30)
@maxValue(730)
param logAnalyticsRetentionInDays int = 90

@description('Enable identity module deployment scaffold.')
param enableIdentityModule bool = false

@description('Enable network module deployment scaffold.')
param enableNetworkModule bool = false

@description('Address prefix for the platform virtual network.')
param networkVnetAddressPrefix string = '10.60.0.0/16'

@description('Address prefix for the platform application subnet.')
param networkAppSubnetPrefix string = '10.60.1.0/24'

@description('Enable observability module deployment scaffold.')
param enableObservabilityModule bool = false

@description('Enable data platform module deployment scaffold.')
param enableDataPlatformModule bool = false

@description('Enable AI platform module deployment scaffold.')
param enableAiPlatformModule bool = false

@description('Enable integration module deployment scaffold.')
param enableIntegrationModule bool = false

@description('Enable experience hosting foundation module deployment.')
param enableExperienceHostingModule bool = false

@description('Enable API runtime foundation module deployment.')
param enableApiRuntimeModule bool = false

@description('Enable data foundation module deployment.')
param enableDataFoundationModule bool = false

@description('Enable AI/ML foundation module deployment.')
param enableAiMlFoundationModule bool = false

@description('Enable integration orchestration foundation module deployment.')
param enableIntegrationOrchestrationModule bool = false

var envSuffix = environmentName == 'dev' ? '' : '-${environmentName}'
var resourceSuffix = '${solutionShortName}${envSuffix}'

var tags = {
  env: environmentName
  owner: owner
  costCenter: costCenter
  workload: workload
}

module platformFoundation './modules/platform-foundation/main.bicep' = {
  name: 'platform-foundation-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    logAnalyticsRetentionInDays: logAnalyticsRetentionInDays
  }
}

module identity './modules/identity/main.bicep' = if (enableIdentityModule) {
  name: 'identity-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module network './modules/network/main.bicep' = if (enableNetworkModule) {
  name: 'network-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    vnetAddressPrefix: networkVnetAddressPrefix
    appSubnetPrefix: networkAppSubnetPrefix
  }
}

module observability './modules/observability/main.bicep' = if (enableObservabilityModule) {
  name: 'observability-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module dataPlatform './modules/data-platform/main.bicep' = if (enableDataPlatformModule) {
  name: 'data-platform-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module aiPlatform './modules/ai-platform/main.bicep' = if (enableAiPlatformModule) {
  name: 'ai-platform-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module integration './modules/integration/main.bicep' = if (enableIntegrationModule) {
  name: 'integration-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module experienceHosting './modules/experience-hosting/main.bicep' = if (enableExperienceHostingModule) {
  name: 'experience-hosting-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module apiRuntime './modules/api-runtime/main.bicep' = if (enableApiRuntimeModule) {
  name: 'api-runtime-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module dataFoundation './modules/data-foundation/main.bicep' = if (enableDataFoundationModule) {
  name: 'data-foundation-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module aiMlFoundation './modules/ai-ml-foundation/main.bicep' = if (enableAiMlFoundationModule) {
  name: 'ai-ml-foundation-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module integrationOrchestration './modules/integration-orchestration/main.bicep' = if (enableIntegrationOrchestrationModule) {
  name: 'integration-orchestration-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

output keyVaultName string = platformFoundation.outputs.keyVaultName
output logAnalyticsWorkspaceName string = platformFoundation.outputs.logAnalyticsWorkspaceName
output moduleStatuses object = {
  identity: enableIdentityModule ? identity!.outputs.moduleStatus : 'identity-disabled'
  network: enableNetworkModule ? network!.outputs.moduleStatus : 'network-disabled'
  observability: enableObservabilityModule ? observability!.outputs.moduleStatus : 'observability-disabled'
  dataPlatform: enableDataPlatformModule ? dataPlatform!.outputs.moduleStatus : 'data-platform-disabled'
  aiPlatform: enableAiPlatformModule ? aiPlatform!.outputs.moduleStatus : 'ai-platform-disabled'
  integration: enableIntegrationModule ? integration!.outputs.moduleStatus : 'integration-disabled'
  experienceHosting: enableExperienceHostingModule ? experienceHosting!.outputs.moduleStatus : 'experience-hosting-disabled'
  apiRuntime: enableApiRuntimeModule ? apiRuntime!.outputs.moduleStatus : 'api-runtime-disabled'
  dataFoundation: enableDataFoundationModule ? dataFoundation!.outputs.moduleStatus : 'data-foundation-disabled'
  aiMlFoundation: enableAiMlFoundationModule ? aiMlFoundation!.outputs.moduleStatus : 'ai-ml-foundation-disabled'
  integrationOrchestration: enableIntegrationOrchestrationModule ? integrationOrchestration!.outputs.moduleStatus : 'integration-orchestration-disabled'
}
