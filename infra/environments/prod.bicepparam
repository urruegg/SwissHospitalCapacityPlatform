using '../main.bicep'

param environmentName = 'prod'
param solutionShortName = 'chhealthpf'
param location = 'switzerlandnorth'

param owner = 'platform-team'
param costCenter = 'tbd'
param workload = 'hospital-capacity'

param logAnalyticsRetentionInDays = 180

// Phased rollout strategy for PROD: keep newly implemented modules disabled
// until SIT end-to-end verification and change-approval gates are complete.
param enableIdentityModule = false
param enableNetworkModule = false
param enableObservabilityModule = false
param enableDataPlatformModule = false
param enableAiPlatformModule = false
param enableIntegrationModule = false
