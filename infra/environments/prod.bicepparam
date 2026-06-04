using '../main.bicep'

param environmentName = 'prod'
param solutionShortName = 'chhealthpf'
param location = 'switzerlandnorth'

param owner = 'platform-team'
param costCenter = 'chhealthpf-prod'
param workload = 'hospital-capacity'

param logAnalyticsRetentionInDays = 180

param enableIdentityModule = true
param enableNetworkModule = true
param enableObservabilityModule = true
param enableDataPlatformModule = true
param enableAiPlatformModule = true
param enableIntegrationModule = true
