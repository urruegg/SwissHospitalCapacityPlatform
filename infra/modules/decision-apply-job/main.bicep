// Sprint 26 WS-C follow-up (#335) — in-VNet gated "decision-tier live apply" job.
//
// A single manual-trigger Container Apps Job that runs the two merged decision
// apply CLIs from inside the SIT VNet:
//   * `python -m coordination.seed_live`          (writes the 6-role plans/actions
//                                                   to the private-endpoint Cosmos)
//   * `python -m foundry.register_decision_tier`  (registers the decision-tier
//                                                   tool on the 6 eastus2 agents)
//
// WHY A JOB: the SIT Cosmos account is `publicNetworkAccess: Disabled` +
// private-endpoint only (ADR-0029) and Foundry is eastus2 (ADR-0032), so the
// apply can only reach those data planes in-VNet. This job runs on the
// **agent-host** managed environment (already VNet-integrated → Cosmos PE
// reachable) and reuses the **agent-host User-Assigned MI**, which already holds
// `Cosmos DB Built-in Data Contributor` (granted in modules/cosmos/csa.bicep).
// The one extra grant — `Cognitive Services User` on the eastus2 Foundry account
// for that MI — is a documented runbook prerequisite (cross-region resource,
// not deployed by this template).
//
// HARD GATE (AGENTS.md §4): the default container command runs BOTH CLIs in
// `--action plan` (dry-run) mode, so an accidental `az containerapp job start`
// with no override mutates nothing. A live apply requires an operator to
// override the command at start time and pass `--approved-to-apply <handle>`
// (see docs/runbooks/decision-tier-live-apply.md). No approver handle is ever
// baked into this template.

@description('Azure region. Region-pinned to the ADR-0013 demo-scope variant path.')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to every resource this module creates.')
param tags object = {}

@description('Resource ID of the agent-host Container Apps managed environment (VNet-integrated per ADR-0029 Option A). The job MUST run here so it reaches the Cosmos private endpoint.')
@minLength(2)
param managedEnvironmentId string

@description('Container image the apply job runs. Reuse the hcc-agent-host image — it bakes in data-platform/decision/ (Sprint 26 WS-C) and the azure-identity/azure-cosmos runtime deps.')
param containerImage string

@description('Cosmos document endpoint the seed writes to (e.g. https://cosmos-csa-ihzhhpf-sit.documents.azure.com:443/). Passed to the container as CSA_COSMOS_ENDPOINT.')
param cosmosEndpoint string

@description('Cosmos database name that holds the plans/proposed_actions containers.')
param cosmosDatabase string = 'csa'

@description('Foundry project data-plane account endpoint (ADR-0032, eastus2). Passed as FOUNDRY_PROJECT_ENDPOINT.')
param foundryEndpoint string = 'https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com'

@description('Foundry project name (ADR-0032). Passed as FOUNDRY_PROJECT_NAME.')
param foundryProject string = 'ai-ihzhhpf-sit-eastus2-project'

@description('Optional ACR login server for MI-based image pull. Set together with containerRegistryResourceId. When empty, the job relies on public/anonymous pull.')
param containerRegistryLoginServer string = ''

@description('Optional resource ID of the ACR that hosts containerImage. Required together with containerRegistryLoginServer.')
param containerRegistryResourceId string = ''

@description('Replica timeout (seconds) for a single apply execution.')
@minValue(60)
@maxValue(3600)
param replicaTimeoutSeconds int = 1800

@description('When true, emits a demoScope tag for provenance (ADR-0013).')
param demoScope bool = false

var effectiveTags = union(tags, {
  demoScope: demoScope ? 'true' : 'false'
})

var useAcrMiPull = !empty(containerRegistryLoginServer) && !empty(containerRegistryResourceId)

// Reuse the agent-host User-Assigned MI (created in modules/agent-host —
// `id-ca-agent-host-<suffix>`). It already holds Cosmos DB Built-in Data
// Contributor and AcrPull, so no new identity or Cosmos role assignment is
// needed here. The Foundry `Cognitive Services User` grant is a runbook prereq.
resource agentHostIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: 'id-ca-agent-host-${nameSuffix}'
}

// Default command = dry-run PLAN for both CLIs (AGENTS.md §4 plan-first gate).
// A live apply overrides `args` at `az containerapp job start` time with the
// operator's `--approved-to-apply <handle>` (never baked into the template).
var planCommand = 'cd /app/data-platform/decision && python -m coordination.seed_live --action plan && python -m foundry.register_decision_tier --action plan'

resource applyJob 'Microsoft.App/jobs@2024-03-01' = {
  name: 'caj-decision-apply-${nameSuffix}'
  location: location
  tags: effectiveTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${agentHostIdentity.id}': {}
    }
  }
  properties: {
    environmentId: managedEnvironmentId
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: replicaTimeoutSeconds
      replicaRetryLimit: 0
      manualTriggerConfig: {
        parallelism: 1
        replicaCompletionCount: 1
      }
      registries: useAcrMiPull ? [
        {
          server: containerRegistryLoginServer
          identity: agentHostIdentity.id
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'decision-apply'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          command: [
            '/bin/sh'
            '-c'
            planCommand
          ]
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: agentHostIdentity.properties.clientId
            }
            {
              name: 'CSA_COSMOS_ENDPOINT'
              value: cosmosEndpoint
            }
            {
              name: 'CSA_COSMOS_DATABASE'
              value: cosmosDatabase
            }
            {
              name: 'FOUNDRY_PROJECT_ENDPOINT'
              value: foundryEndpoint
            }
            {
              name: 'FOUNDRY_PROJECT_NAME'
              value: foundryProject
            }
          ]
        }
      ]
    }
  }
}

@description('Name of the manual-trigger decision-apply Container Apps Job.')
output jobName string = applyJob.name

@description('Resource ID of the decision-apply job.')
output jobResourceId string = applyJob.id

@description('Client ID of the reused agent-host MI (for runbook cross-checks).')
output identityClientId string = agentHostIdentity.properties.clientId

@description('Decision-apply job module implementation marker.')
output moduleStatus string = 'decision-apply-job-implemented'
