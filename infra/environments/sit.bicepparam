using '../main.bicep'

param environmentName = 'sit'
param solutionShortName = 'chhealthpf'
param location = 'switzerlandnorth'

param owner = 'platform-team'
param costCenter = 'tbd'
param workload = 'hospital-capacity'

param logAnalyticsRetentionInDays = 90

param enableIdentityModule = true
param enableNetworkModule = true
param enableObservabilityModule = true

param networkVnetAddressPrefix = '10.60.0.0/16'
param networkAppSubnetPrefix = '10.60.1.0/24'
