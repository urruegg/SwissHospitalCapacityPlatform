@description('Environment suffix, e.g. sit or prod')
param envSuffix string
@description('Existing Container Apps managed environment resource id')
param managedEnvironmentId string
@description('Existing Event Hub namespace name (evh-ihzhhpf...)')
param eventHubNamespace string
@description('Event Hub name for external signals')
param eventHubName string
param location string = resourceGroup().location

@description('Provider-runner container image. Defaults to the azure-cli placeholder; bump to <acr>/signal-runner:<tag> (built by ci-build-signal-runner.yml) to deploy the live ingestion runner.')
param providerRunnerImage string = 'mcr.microsoft.com/azure-cli:latest'

@description('Full Key Vault secret URI for the Web IQ API key, e.g. https://<kv>.vault.azure.net/secrets/webiq-api-key. Empty = live Web IQ disabled; the runner falls back to the simulator (key presence is the enablement gate).')
param webiqSecretUri string = ''

@description('Key Vault name holding the Web IQ secret. Set together with webiqSecretUri to grant the runner identity Key Vault Secrets User. Empty = no grant.')
param keyVaultName string = ''

@description('Comma-separated cantons the Web IQ live queries tag (in-scope hospital cantons: USZ/LUKS/SZB).')
param webiqRegionCantons string = 'ZH,LU,SZ'

@description('DC-EXT-SIGNAL-v1 envelope residency. SIT demo = demo-westus2 (ADR-0013); PROD = CH.')
@allowed([ 'CH', 'demo-westus2' ])
param signalResidency string = 'CH'

@description('Enable keyless Web IQ auth via the runner managed identity (Entra ID app-only token). Requires binding this UAMI\'s client id in the Web IQ portal. Preferred over webiqSecretUri on this platform (RBAC-only / keyless posture; private-only vaults). false = simulator-only unless webiqSecretUri is set.')
param webiqEntraEnabled bool = false

@description('ACR login server for the runner image pull (e.g. cri75lbu5sj4hza.azurecr.io). Empty = public image, no pull identity wired.')
param containerRegistryLoginServer string = ''

var appName = 'ca-signal-runner-ihzhhpf-${envSuffix}'
var identityName = 'id-signal-runner-ihzhhpf-${envSuffix}'

// Key presence is the live-binding gate: when webiqSecretUri is empty the runner
// gets no WEBIQ_API_KEY and every live provider falls back to the simulator.
var wireWebIq = !empty(webiqSecretUri)
var keyVaultSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'
var runnerSecrets = wireWebIq ? [
  {
    name: 'webiq-api-key'
    keyVaultUrl: webiqSecretUri
    identity: runnerIdentity.id
  }
] : []
var baseEnv = [
  { name: 'EVENT_HUB_NAMESPACE', value: eventHubNamespace }
  { name: 'EVENT_HUB_NAME', value: eventHubName }
  { name: 'AZURE_CLIENT_ID', value: runnerIdentity.properties.clientId }
  { name: 'WEBIQ_REGION_CANTONS', value: webiqRegionCantons }
  { name: 'SIGNAL_RESIDENCY', value: signalResidency }
  { name: 'WEBIQ_ENTRA_ENABLED', value: webiqEntraEnabled ? 'true' : 'false' }
]
var runnerEnv = wireWebIq ? concat(baseEnv, [ { name: 'WEBIQ_API_KEY', secretRef: 'webiq-api-key' } ]) : baseEnv

// MI-based ACR pull for the private runner image (no admin creds / secrets).
var useAcr = !empty(containerRegistryLoginServer)
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'
var registriesConfig = useAcr ? [
  {
    server: containerRegistryLoginServer
    identity: runnerIdentity.id
  }
] : []

// User-Assigned Managed Identity: unlike a SystemAssigned identity (whose
// principalId is minted fresh on every container-app / CAE recreate), a UAMI
// persists as its own resource, so its principalId is stable across recreates.
// This keeps the Event Hubs role assignment fully idempotent — no
// RoleAssignmentUpdateNotPermitted and no orphaned assignments after a
// destructive CAE rebuild.
resource runnerIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: {
    env: envSuffix
    owner: 'urruegg'
    costCenter: 'curavias-platform'
    workload: 'external-signals'
  }
}

resource runner 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  tags: {
    env: envSuffix
    owner: 'urruegg'
    costCenter: 'curavias-platform'
    workload: 'external-signals'
  }
  properties: {
    managedEnvironmentId: managedEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      secrets: runnerSecrets
      registries: registriesConfig
    }
    template: {
      containers: [
        {
          name: 'provider-runner'
          image: providerRunnerImage
          env: runnerEnv
        }
      ]
      scale: { minReplicas: 0, maxReplicas: 1 }
    }
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${runnerIdentity.id}': {}
    }
  }
}

@description('Azure Event Hubs Data Sender built-in role definition id')
var eventHubsDataSenderRoleId = '2b629674-e913-4c01-ae53-ef4638d8f975'

resource ehNamespace 'Microsoft.EventHub/namespaces@2021-11-01' existing = {
  name: eventHubNamespace
}

resource senderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  // Name is derived from the UAMI's resource id (deterministic, known at the
  // start of deployment) and the UAMI principalId is stable across recreates,
  // so this assignment is idempotent across destructive CAE rebuilds.
  name: guid(ehNamespace.id, runnerIdentity.id, eventHubsDataSenderRoleId)
  scope: ehNamespace
  properties: {
    principalId: runnerIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', eventHubsDataSenderRoleId)
  }
}

// Grant the runner identity read access to the Web IQ secret only when a Key
// Vault is wired. The secret itself is provisioned out-of-band by an operator
// (never in IaC): `az keyvault secret set --vault-name <kv> --name webiq-api-key`.
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = if (!empty(keyVaultName)) {
  name: keyVaultName
}

resource kvSecretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(keyVaultName)) {
  name: guid(resourceGroup().id, keyVaultName, runnerIdentity.id, keyVaultSecretsUserRoleId)
  scope: keyVault
  properties: {
    principalId: runnerIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsUserRoleId)
  }
}

// AcrPull for the runner identity so the Container App can pull the private
// signal-runner image keylessly. ACR assumed same-RG (name from login server).
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = if (useAcr) {
  name: split(containerRegistryLoginServer, '.')[0]
}

resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useAcr) {
  name: guid(resourceGroup().id, containerRegistryLoginServer, runnerIdentity.id, acrPullRoleId)
  scope: acr
  properties: {
    principalId: runnerIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
  }
}

output providerRunnerName string = runner.name
output providerRunnerPrincipalId string = runnerIdentity.properties.principalId
output providerRunnerIdentityName string = runnerIdentity.name
