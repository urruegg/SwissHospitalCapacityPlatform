using '../main.bicep'

// Sprint 16 T1 — CSA Cosmos DB (PROD placeholder). Not deployed in the demo
// scope; retained for parity. Region returns to switzerlandnorth when the
// target services reach Swiss GA (ADR-0013).
param environmentName = 'prod'
param solutionShortName = 'ihzhhpf'
param location = 'switzerlandnorth'

param owner = 'platform-team'
param costCenter = 'ihzhhpf-prod'
param workload = 'hospital-capacity'

param agentHostMiPrincipalId = ''
