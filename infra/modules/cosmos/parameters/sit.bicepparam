using '../main.bicep'

// Sprint 16 T1 — CSA Cosmos DB (SIT). Demo scope westus2 per ADR-0013.
param environmentName = 'sit'
param solutionShortName = 'ihzhhpf'
param location = 'westus2'

param owner = 'platform-team'
param costCenter = 'ihzhhpf-sit'
param workload = 'hospital-capacity'

// Populated at apply time from the Sprint 13 agent-host managed identity
// principalId. Left empty here so the what-if is deterministic; the deploy
// gate (approved-to-apply) supplies the value.
param agentHostMiPrincipalId = ''
