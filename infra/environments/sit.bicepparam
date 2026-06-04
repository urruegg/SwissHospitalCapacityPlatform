using '../main.bicep'

param environmentName = 'sit'
param solutionShortName = 'chhealthpf'
param location = 'switzerlandnorth'

param owner = 'platform-team'
param costCenter = 'chhealthpf-sit'
param workload = 'hospital-capacity'

param logAnalyticsRetentionInDays = 90

// Temporary phased SIT rollout until subscription-level provider registrations are completed.
param enableIdentityModule = false
param enableNetworkModule = false
param enableObservabilityModule = true
param enableDataPlatformModule = false
param enableAiPlatformModule = false
param enableIntegrationModule = false

param networkVnetAddressPrefix = '10.60.0.0/16'
param networkAppSubnetPrefix = '10.60.1.0/24'
