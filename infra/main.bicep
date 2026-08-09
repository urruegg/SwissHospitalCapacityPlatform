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
param solutionShortName string = 'ihzhhpf'

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

@description('Address prefix for the platform data subnet (private endpoints).')
param networkDataSubnetPrefix string = '10.60.2.0/24'

@description('Address prefix for the Container Apps Environment (CAE) infrastructure subnet (ADR-0029 Option A). Delegated to Microsoft.App/environments. MUST fall inside networkVnetAddressPrefix — set explicitly whenever the VNet prefix is changed from the 10.60.0.0/16 default (e.g. PROD swn uses 10.70.0.0/16).')
param networkCaeSubnetPrefix string = '10.60.4.0/23'

@description('Enable observability module deployment scaffold.')
param enableObservabilityModule bool = false

@description('Enable data platform module deployment scaffold.')
param enableDataPlatformModule bool = false

@description('Enable the source-SQL submodule inside data-platform (Sprint 08 W1.1 synthetic KIS feed).')
param enableSourceSqlModule bool = false

@description('Resource ID of the data subnet used for the source-SQL private endpoint. Required when enableSourceSqlModule = true.')
param sourceSqlDataSubnetId string = ''

@description('Resource ID of the Key Vault that stores the source-SQL admin password. Required when enableSourceSqlModule = true.')
param sourceSqlKeyVaultId string = ''

@description('Name of the Key Vault secret holding the source-SQL admin password. Required when enableSourceSqlModule = true.')
param sourceSqlAdminPasswordSecretName string = ''

@description('Optional. Resource ID of the existing privatelink.database.windows.net private DNS zone for the source-SQL private endpoint. Leave empty to wire DNS externally.')
param sourceSqlPrivateDnsZoneId string = ''

@description('Entra ID login (UPN or group displayName) of the source-SQL AAD admin. Required by tenant AAD-only auth policy when enableSourceSqlModule = true.')
param sourceSqlAadAdminLogin string = ''

@description('Object ID (SID) of the source-SQL AAD admin principal. Required when enableSourceSqlModule = true.')
param sourceSqlAadAdminObjectId string = ''

@description('Principal type of the source-SQL AAD admin.')
@allowed([
  'User'
  'Group'
  'ServicePrincipal'
])
param sourceSqlAadAdminPrincipalType string = 'User'

@description('Enable Fabric foundation submodule (capacity + post-deploy workspace/lakehouse/mirror).')
param enableFabricFoundationModule bool = false

@description('Object ID(s) of Fabric capacity administrators. Required when enableFabricFoundationModule = true.')
param fabricCapacityAdmins array = []

@description('Enable Fabric Eventstream module (Sprint 09 v2.0.0 T2.2). Requires enableDataFoundationModule=true (event hub source) and enableDataPlatformModule + enableFabricFoundationModule (workspace/lakehouse destination). Scaffold-only Bicep + REST-API post-deploy; see modules/data-platform/fabric-eventstream/README.md.')
param enableFabricEventstreamModule bool = false

@description('Fabric workspace ID that hosts the Eventstream. Required when enableFabricEventstreamModule=true. Obtain via configure-fabric.ps1 post-deploy output.')
param fabricEventstreamWorkspaceId string = ''

@description('Optional Fabric Lakehouse ID for the Eventstream destination. Empty defers destination wiring (Eventstream created source-only). Optional at Bicep composition time; required at post-deploy time for full wiring.')
param fabricEventstreamDestinationLakehouseId string = ''

@description('Enable the Sprint 23 skills-events Eventstream lane (WS-A4, design D4). Scaffold-only Bicep + REST-API post-deploy carrying ONLY the three near-real-time skills events. Requires enableDataFoundationModule=true for the Event Hub source. See modules/integration-orchestration/skills-eventstream/main.bicep.')
param enableSkillsEventstreamModule bool = false

@description('Fabric workspace ID that hosts the skills-events Eventstream. Required at post-deploy time when enableSkillsEventstreamModule=true. Obtain via configure-fabric.ps1 post-deploy output.')
param skillsEventstreamWorkspaceId string = ''

@description('Optional Fabric Lakehouse ID for the skills-events Eventstream destination. Empty defers destination wiring (Eventstream created source-only).')
param skillsEventstreamDestinationLakehouseId string = ''

@description('Skills-events Eventstream source transport. CustomEndpoint (default, design D4 demo-scope) is fully live-deployable and mirrors es-capacity-events-sit; EventHub is the Swiss-GA target-state (requires a Fabric-managed connection). See modules/integration-orchestration/skills-eventstream/main.bicep.')
@allowed([
  'CustomEndpoint'
  'EventHub'
])
param skillsEventstreamSourceMode string = 'CustomEndpoint'

// Sprint 23 WS-A4 (ADR-0043) — the dedicated per-domain skills-events Event Hub entity is
// provisioned exactly when the skills lane runs in sourceMode=EventHub (the Swiss-GA / ADR-0043
// path). In CustomEndpoint mode the Container Apps publisher POSTs to the ingestion URL and no
// Event Hub source is needed, so the hub stays un-provisioned (backwards-compatible default).
var skillsEventHubNeeded = enableSkillsEventstreamModule && skillsEventstreamSourceMode == 'EventHub'

@description('Enable AI platform module deployment scaffold.')
param enableAiPlatformModule bool = false

@description('Enable integration module deployment scaffold.')
param enableIntegrationModule bool = false

@description('Enable experience hosting foundation module deployment.')
param enableExperienceHostingModule bool = false

// Sprint 24 Curavias public landing page hosting was retired in Sprint 28 — see
// docs/adr/0044-retire-public-website.md. The Static Web App module, its params,
// and the curavias-web-deploy workflow were removed. The shared curavias.ch DNS
// zone stays: it still serves the hcc-app-fluent Container App (app.curavias.ch).

@description('Enable API runtime foundation module deployment.')
param enableApiRuntimeModule bool = false

@description('Enable data foundation module deployment.')
param enableDataFoundationModule bool = false

@description('Enable the external-signals provider-runner (ca-signal-runner) module. Requires enableAgentHostModule + enableDataFoundationModule. Wires the runner into the CAE + Event Hub namespace so it survives future CAE redeploys.')
param enableSignalRunnerModule bool = false

@description('Enable the Sprint 26 WS-C decision-tier live-apply Container Apps Job (caj-decision-apply). Requires enableAgentHostModule + enableCsaCosmosModule. Manual-trigger only, plan-first by default (AGENTS.md §4); a live apply is an operator-driven `az containerapp job start` override per docs/runbooks/decision-tier-live-apply.md.')
param enableDecisionApplyJobModule bool = false

@description('Container image for the decision-tier apply Job only. Empty = inherit agentHostImage. Set this (not agentHostImage) to give the Job the decision-CLI-enabled image without redeploying the running agent-host Container App.')
param decisionApplyJobImage string = ''

@description('Object ID of the simulator managed identity that publishes to Event Hubs (Sprint 09 v2.0.0 T2.1/T3.7). Empty = role assignment skipped.')
param eventHubsSimulatorMiPrincipalId string = ''

@description('Object ID of the BM-Copilot managed identity that reads from cg-bm-copilot-agent (Sprint 09 v2.0.0 T2.1/T4.5). Empty = role assignment skipped.')
param eventHubsBmCopilotMiPrincipalId string = ''

@description('Object ID of the CSA (Capacity Simulation Agent) managed identity that reads from cg-csa-agent (Sprint 09 v2.0.0 T2.1/T4.5). Empty = role assignment skipped.')
param eventHubsCsaAgentMiPrincipalId string = ''

// Sprint 23 WS-A1 (#255) — ADLS Gen2 landing zone for Curavias org/skills master data.
@description('Enable the Sprint 23 masterdata landing-zone module (ADLS Gen2 storage + landing filesystem for synthetic org/skills extracts).')
param enableMasterdataLandingModule bool = false

@description('Object ID of the ingestion pipeline managed identity that writes org/skills extracts to the landing container. Empty = Storage Blob Data Contributor role assignment skipped. When enableSkillsSimJobsModule=true this is overridden with the skills-sim jobs MI principalId.')
param masterdataLandingPipelinePrincipalId string = ''

@description('Resource ID of the Log Analytics workspace for masterdata landing blob diagnostics. Empty = diagnostics skipped (SIT). Populated in PROD.')
param masterdataLandingLogAnalyticsWorkspaceId string = ''

// Sprint 23 WS-A3 (#255) — Container Apps Jobs for the skills-evidence simulators.
@description('Enable the Sprint 23 skills-sim jobs module (four manual-trigger Container Apps Jobs that seed synthetic extracts into the landing zone). Requires enableMasterdataLandingModule=true for the landing target + RBAC grant.')
param enableSkillsSimJobsModule bool = false

@description('Container image the skills-sim jobs run. Placeholder until the skills-sim CI workflow pushes a real image to ACR (parity with sim-capacity).')
param skillsSimJobsImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

// Sprint 23 WS-A4 (#255) — Container Apps Job for the skills-EVENTS simulator.
@description('Enable the Sprint 23 skills-events sim job (one manual-trigger Container Apps Job that publishes synthetic DC-SKILL-EVENT-v1 records to the live SIT Eventstream CustomEndpoint). The SAS connection string is read from Key Vault via a secret reference.')
param enableSkillsEventSimJobModule bool = false

@description('Container image the skills-events sim job runs. Placeholder until the skills-events-sim CI workflow pushes a real image to ACR (parity with skills-sim).')
param skillsEventSimJobImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Name of the Key Vault secret holding the CustomEndpoint SAS connection string for the skills-events sim job. Populated out-of-band (never in Bicep/git).')
param skillsEventConnectionStringSecretName string = 'skills-events-connection-string'

// Sprint 28 WS-INF (#377) — Curavias Product Owner Agent (Foundry IQ domain #1).
@description('Region for the Sprint 28 PO Agent modules (Search, runtime, Cosmos, Key Vault). Pinned to the ADR-0013 demo-scope variant path; PROD = switzerlandnorth per ADR-0037 / NFR-POA-003.')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param poAgentLocation string = 'westus2'

@description('Region for the PO Agent runtime Azure OpenAI account. Separable from poAgentLocation per ADR-0032: SIT infra runs in westus2 but Azure OpenAI has no quota there, so SIT pins this to eastus2 (the ADR-0013 demo cross-region). Defaults to poAgentLocation to preserve single-region behaviour for PROD (switzerlandnorth per NFR-POA-003).')
param poAgentOpenAiLocation string = poAgentLocation

@description('Enable the Sprint 28 AI Search module (srch-ihzhhpf-<env>) — GA substrate for the Foundry IQ Knowledge Layer.')
param enablePoAgentSearchModule bool = false

@description('Enable the Sprint 28 Foundry IQ knowledge-base marker module (naming + pinned-version contract; provisioned via knowledge-base-rest.md runbook).')
param enablePoAgentKnowledgeBaseModule bool = false

@description('Enable the Sprint 28 corpus landing module (ADLS Gen2 stcorpus<suffix> for synthetic product documents).')
param enablePoAgentCorpusLandingModule bool = false

@description('Enable the Sprint 28 PO Agent runtime module (Container App + scheduled corpus-refresh job + Cosmos audit + Azure OpenAI + Key Vault). Requires enablePoAgentCorpusLandingModule for the Storage RBAC grant and enablePoAgentSearchModule for the Search reader grant.')
param enablePoAgentRuntimeModule bool = false

@description('Container image the PO Agent runtime app runs. Placeholder until po-agent-runtime-build.yml pushes a real image to ACR.')
param poAgentContainerImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Container image the PO Agent corpus-refresh job runs (Sprint 42 fix - separate from poAgentContainerImage since the runtime app and refresh job are different programs). Placeholder until po-agent-corpus-build.yml pushes a real image to ACR.')
param poAgentCorpusRefreshContainerImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Resource ID of the Log Analytics workspace for PO Agent Search/Cosmos/Key Vault diagnostics. Empty = diagnostics skipped (SIT). Populated in PROD.')
param poAgentLogAnalyticsWorkspaceId string = ''

@description('Enable AI/ML foundation module deployment.')
param enableAiMlFoundationModule bool = false

@description('Enable integration orchestration foundation module deployment.')
param enableIntegrationOrchestrationModule bool = false

@description('Enable Foundry-hosted runtime agents module (BM-Copilot + CSA UAMIs + RBAC). Sprint 09 v2.0.0 T4.5.')
param enableFoundryHostedAgents bool = false

@description('Location for the Foundry-hosted agents UAMIs. Must match the Foundry account region — westus2 for the demo scope per ADR-0013.')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param foundryHostedAgentsLocation string = 'westus2'

@description('Event Hub namespace name that BM-Copilot/CSA MIs receive from. Placeholder wiring while T2 (data-foundation Event Hubs) lives on a separate branch.')
param foundryHostedAgentsEventHubNamespace string = ''

@description('Event Hub name that BM-Copilot/CSA MIs receive from. Placeholder wiring while T2 (data-foundation Event Hubs) lives on a separate branch.')
param foundryHostedAgentsEventHubName string = ''

@description('Consumer group name for BM-Copilot.')
param foundryHostedAgentsBmCopilotConsumerGroup string = 'cg-bm-copilot-agent'

@description('Consumer group name for CSA.')
param foundryHostedAgentsCsaConsumerGroup string = 'cg-csa-agent'

@description('Enable the sim-capacity ACA module (Sprint 09 v2 T3.7). Default true in SIT, false in PROD.')
param enableSimCapacityModule bool = false

@description('Region for the sim-capacity ACA module. Pinned to the ADR-0013 demo-scope variant path.')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param simCapacityLocation string = 'westus2'

@description('Container image the sim-capacity Container App runs. Placeholder until the sim-capacity image is published.')
param simCapacityContainerImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Optional ACR login server (e.g. \'cri75lbu5sj4hza.azurecr.io\') for pulling simCapacityContainerImage. Together with simCapacityContainerRegistryResourceId enables MI-based pull (no admin creds).')
param simCapacityContainerRegistryLoginServer string = ''

@description('Optional resource ID of the ACR that hosts simCapacityContainerImage. Required together with simCapacityContainerRegistryLoginServer.')
param simCapacityContainerRegistryResourceId string = ''

@description('Event Hub namespace the sim-capacity producer emits to. When empty and enableDataFoundationModule=true, the sim-capacity module is skipped (no namespace to target).')
param simCapacityEventHubNamespace string = ''

@description('Event Hub entity name the sim-capacity producer emits to.')
param simCapacityEventHubName string = 'demand-encounters'

@description('When true, the sim-capacity deployment is scoped to the Sprint 09 v2 demo path (synthetic data only per ADR-0013 / ADR-0016).')
param simCapacityDemoScope bool = true

// Sprint 13 T5 — Container Apps agent-host (loads BMCA/OOA/DCA/ORSA/SBA/CSA/data-quality
// manifests at startup). Deploys Container App + Cosmos (conversations/audit/approval-events
// per ADR-0007) + optional Azure Managed Redis (grounding cache).
@description('Enable the Sprint 13 agent-host module (Container App + Cosmos + optional Redis per ADR-0007).')
param enableAgentHostModule bool = false

@description('Enable the CSA Cosmos DB module (Sprint 16: EnableNoSQLVectorSearch account + 4 containers). Wired into the orchestrator per issue #252 Phase A so it is covered by CI what-if + SIT/PROD parity; the private endpoint follows enableNetworkModule (PE on with network, public otherwise per ADR-0013).')
param enableCsaCosmosModule bool = false

@description('Container image reference for the agent-host (registry/repository:tag). Placeholder matches sim-capacity pattern until agent-host CI pushes real images to ACR.')
param agentHostImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Enable Azure Managed Redis inside the agent-host module (grounding cache per ADR-0007 §1). Defaults to true (PROD behaviour); set to false in SIT per ADR-0028 (Balanced_B0 SKU not offered in westus2 for MCAPS demo sub; agent-host uses in-memory cache today).')
param agentHostEnableRedis bool = true

@description('Optional live Fabric Data Agent consumption endpoint. Empty string keeps the agent-host synthetic fallback.')
param fabricDataAgentEndpoint string = ''

@description('Optional Fabric workspace ID that hosts the live Fabric Data Agent. Empty string keeps the agent-host synthetic fallback.')
param fabricWorkspaceId string = ''

@description('Optional Fabric Data Agent ID. Empty string keeps the agent-host synthetic fallback.')
param fabricDataAgentId string = ''

@description('Sprint 43 WS-1 — Foundry Agent Service project account root (e.g. https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com). Empty string keeps the agent-host on the deterministic MockChatModel.')
param foundryProjectEndpoint string = ''

@description('Sprint 43 WS-1 — Foundry Agent Service project name (e.g. ai-ihzhhpf-sit-eastus2-project). Empty string keeps the agent-host on the deterministic MockChatModel.')
param foundryProjectName string = ''

@description('Sprint 43 WS-2 — Fabric lakehouse ID for direct OneLake Gold table reads. Empty string keeps FabricAdapter on its synthetic fallback.')
param fabricLakehouseId string = ''

@description('#424 M4 — agent-host RLS provider for the structured golden read. `simulated` (default) filters synthetic rows in-process; `fabric-data-agent` reuses the proven live Fabric Data Agent client but still refuses per-user structured scope until OBO + the dynamic-RLS TMDL predicate land (#424 M5, #510). Config, not code.')
param agentHostRlsProvider string = 'simulated'

@description('#424 M5 — enable the on-behalf-of (OBO) ingress seam on the agent-host golden read. `false` (default) keeps SIT on the simulated/native path (byte-parity with M4). `true` requires a valid caller bearer and exchanges it for a downstream Fabric token; go-live additionally needs OBO_TENANT_ID/CLIENT_ID/CLIENT_SECRET, RLS_PROVIDER=fabric-data-agent, THREAD_PROVIDER=foundry, and #510 (dynamic-RLS TMDL) per ADR-0057. Config, not code.')
param agentHostOboEnabled bool = false

@description('Sprint 43 WS-6 — tenant ID for the OBO On-Behalf-Of exchange (agent-host confidential client).')
param agentHostOboTenantId string = ''

@description('Sprint 43 WS-6 — client ID of the hcc-agent-host app registration used for the OBO exchange.')
param agentHostOboClientId string = ''

@description('Sprint 43 WS-6 — resource ID of the Key Vault storing the agent-host OBO client secret. Empty (default) falls back to the shared platform Key Vault (platformFoundation.outputs.keyVaultName), mirroring sourceSqlKeyVaultId\'s own fallback pattern.')
param agentHostOboKeyVaultId string = ''

@description('Sprint 43 WS-6 — name of the Key Vault secret holding the agent-host OBO client secret. Required when agentHostOboEnabled = true.')
param agentHostOboClientSecretName string = ''

@description('Sprint 43 WS-6 — JWKS URL used to validate the caller bearer (tenant discovery keys endpoint).')
param agentHostOboJwksUrl string = ''

@description('Sprint 43 WS-6 — expected audience on the caller bearer token (api://<agent-host-app-id>).')
param agentHostOboAudience string = ''

@description('Sprint 43 WS-6 — expected issuer on the caller bearer token.')
param agentHostOboIssuer string = ''

@description('Sprint 43 WS-6 — downstream scope for the OBO exchange. auth/obo_context.py defaults this to https://api.fabric.microsoft.com/.default, which does NOT work for OneLake reads (validated live, 401) -- FabricDeltaClient needs a storage.azure.com-scoped token instead.')
param agentHostOboFabricScope string = 'https://storage.azure.com/.default'

// Sprint 13 T1 — Fluent baseline Container App (React/Vite bundle served via nginx on 8080).
@description('Enable the Sprint 13 hcc-app-fluent Container App module.')
param enableAppFluentModule bool = false

@description('Container image reference for the hcc-app-fluent (registry/repository:tag). Placeholder until app-build.yml pushes real images to ACR.')
param appFluentImage string = 'nginxinc/nginx-unprivileged:1.27-alpine'

@description('#447 — Foundry agent-host base URL injected into the hcc-app-fluent at container start (runtime window.__ENV__.AGENT_HOST_URL). Set per-env to the environment-local agent-host FQDN (SIT vs PROD) so the app calls its own region\'s agent-host. Empty keeps the built-in mock. Replaces the former build-time VITE_AGENT_HOST_URL bake so one image is env-agnostic.')
param appFluentAgentHostUrl string = ''

@description('Sprint 42 — dedicated Product Owner Agent (po-agent-service) base URL injected into the hcc-app-fluent at container start (runtime window.__ENV__.PO_AGENT_URL). Without this, the product-owner-agent chat rail falls through to the shared agent-host, which does not register that agent id and 404s. Empty keeps the built-in deterministic mock.')
param appFluentPoAgentUrl string = ''

@description('#424 M2 — golden-source base URL injected into the hcc-app-fluent at container start (runtime window.__ENV__.GOLDEN_SOURCE_URL). The app reads live board payloads from GET <url>/{resource}. Leave empty to auto-derive the agent-host URL suffixed with /golden (Option 1: the agent-host serves the RLS-scoped golden surface); set explicitly only when the golden source diverges from the agent-host.')
param appFluentGoldenSourceUrl string = ''

@description('#424 M3 — when true, injects window.__ENV__.FOUNDRY_THREADS_ENABLED=true so the hcc-app-fluent mints a live per-(user x agent) thread via the agent-host (POST /threads) and threads it onto every chat turn. Requires appFluentAgentHostUrl to be non-empty; with the host unset the app keeps simulated threads. Provider stays native (no OBO) until M5.')
param appFluentFoundryThreadsEnabled bool = false

@description('Sprint A — MSAL application (client) id for the hcc-app-fluent (window.__ENV__.MSAL_CLIENT_ID). Empty keeps the app in demo (no sign-in). Set to the ihzhhpf-app registration id in SIT.')
param appFluentMsalClientId string = ''

@description('Sprint A — MSAL tenant id (MngEnvMCAP164444, ADR-0012) for the hcc-app-fluent (window.__ENV__.MSAL_TENANT_ID).')
param appFluentMsalTenantId string = ''

@description('Sprint A — SPA redirect URI for the hcc-app-fluent (appsit.curavias.ch in SIT). Must match a SPA redirect on the ihzhhpf-app registration.')
param appFluentMsalRedirectUri string = ''

@description('Sprint A — deployment env (dev|sit|prod) injected into the hcc-app-fluent (window.__ENV__.APP_ENV) for the role lens env fallback.')
param appFluentAppEnv string = ''

@description('Sprint A — home hospital for the hcc-app-fluent (window.__ENV__.APP_HOME_HOSPITAL); own-site role scope when the token omits the hospital claim.')
param appFluentHomeHospital string = ''

@description('Sprint 43 WS-6 — the agent-host API scope the SPA requests via MSAL for OBO-forwarded chat grounding (window.__ENV__.AGENT_HOST_SCOPE). Empty (default) keeps the app on OIDC-only sign-in (no Authorization header forwarded).')
param appFluentAgentHostScope string = ''

// Sprint 13.1 T-DNS — curavias.ch public custom hostname for the Fluent app (ADR-0030).
@description('Public custom hostname for the hcc-app-fluent CA ingress. Empty string keeps the CA on its default *.azurecontainerapps.io hostname. Set to appsit.curavias.ch in SIT and app.curavias.ch in PROD per ADR-0030.')
param appFluentCustomHostname string = ''

@description('When true and appFluentCustomHostname is set, provision a managed cert + bind the CA to the custom hostname. Deploy is a two-step process: (1) merge with this false to create the DNS zone + records, (2) do GoDaddy NS delegation, (3) flip to true and redeploy so the CAE can validate ownership + issue a Let\'s Encrypt cert. Runbook: docs/runbooks/curavias-dns-godaddy-delegation.md.')
param appFluentEnableCustomDomainCert bool = false

@description('When true, this deployment OWNS the curavias.ch public DNS zone (zone + records) in its own resource group. SIT sets this true (the zone lives in rg-ihzhhpf-sit). PROD MUST set this false: the zone is shared and owned by SIT, so the PROD RG only claims the custom hostname on its Container App (customHostname + cert) while the `app` CNAME + `asuid.app` TXT records stay in the SIT-owned zone. Setting this false lets PROD bind app.curavias.ch to the PROD CA without creating a conflicting second curavias.ch zone. See ADR-0030 and the module note in infra/modules/dns/curavias.bicep.')
param manageCuraviasDnsZone bool = true

@description('Optional Key Vault name override, forwarded to platform-foundation. Empty (default) keeps the auto-generated deterministic name. Set only to avoid a soft-delete + purge-protection name collision on a same-RG region rebuild (Sprint 19 Switzerland North greenfield).')
param keyVaultNameOverride string = ''

@description('Enable a private endpoint for the platform Key Vault (ADR-0039, extends ADR-0029 Option A). Requires enableNetworkModule=true (needs the VNet + snet-data). Flips the vault to publicNetworkAccess=Disabled and provisions the privatelink.vaultcore.azure.net zone + PE. Non-destructive on its own; PROD swn sets this true alongside enableNetworkModule for SIT network parity.')
param enableKeyVaultPrivateEndpoint bool = false

var envSuffix = environmentName == 'dev' ? '' : '-${environmentName}'
var resourceSuffix = '${solutionShortName}${envSuffix}'

// Deterministic name of the WS-A1 landing storage account, mirrored from the
// masterdata-landing module so the WS-A3 jobs can target it without a circular
// module reference (jobs use it only as a runtime env var).
var masterdataLandingStorageName = toLower('stmasterdata${replace(resourceSuffix, '-', '')}')

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
    keyVaultName: keyVaultNameOverride
    // ADR-0039 — Key Vault private endpoint. vnetResourceId is only consumed by
    // the module when enableKeyVaultPrivateEndpoint=true (which requires
    // enableNetworkModule=true — see the param description). Single-condition
    // guard mirrors the agent-host CAE wiring so Bicep can prove non-null.
    enableKeyVaultPrivateEndpoint: enableKeyVaultPrivateEndpoint
    vnetResourceId: enableNetworkModule ? network!.outputs.vnetResourceId : ''
    keyVaultPrivateEndpointSubnetName: 'snet-data'
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
    dataSubnetPrefix: networkDataSubnetPrefix
    caeSubnetPrefix: networkCaeSubnetPrefix
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
    enableSourceSqlModule: enableSourceSqlModule
    // Auto-wire from network module output when the caller passes empty; otherwise honour the explicit param.
    sourceSqlDataSubnetId: !empty(sourceSqlDataSubnetId) ? sourceSqlDataSubnetId : (enableNetworkModule ? network.outputs.dataSubnetResourceId : '')
    // Auto-wire from platform-foundation module (always deployed) when the caller passes empty.
    sourceSqlKeyVaultId: !empty(sourceSqlKeyVaultId) ? sourceSqlKeyVaultId : resourceId('Microsoft.KeyVault/vaults', platformFoundation.outputs.keyVaultName)
    sourceSqlAdminPasswordSecretName: sourceSqlAdminPasswordSecretName
    sourceSqlPrivateDnsZoneId: sourceSqlPrivateDnsZoneId
    sourceSqlAadAdminLogin: sourceSqlAadAdminLogin
    sourceSqlAadAdminObjectId: sourceSqlAadAdminObjectId
    sourceSqlAadAdminPrincipalType: sourceSqlAadAdminPrincipalType
    enableFabricFoundationModule: enableFabricFoundationModule
    fabricCapacityAdmins: fabricCapacityAdmins
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
    simulatorMiPrincipalId: eventHubsSimulatorMiPrincipalId
    bmCopilotMiPrincipalId: eventHubsBmCopilotMiPrincipalId
    csaAgentMiPrincipalId: eventHubsCsaAgentMiPrincipalId
    enableSkillsEventHub: skillsEventHubNeeded
  }
}

// Sprint 23 WS-A1 (#255) — ADLS Gen2 landing zone for Curavias org/skills master data.
module masterdataLanding './modules/data-foundation/masterdata-landing/main.bicep' = if (enableMasterdataLandingModule) {
  name: 'masterdata-landing-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    // When the skills-sim jobs module is on, grant its MI write access to the
    // landing container; otherwise fall back to the explicit param (empty = skip).
    pipelinePrincipalId: enableSkillsSimJobsModule ? skillsSimJobs!.outputs.principalId : masterdataLandingPipelinePrincipalId
    logAnalyticsWorkspaceId: masterdataLandingLogAnalyticsWorkspaceId
  }
}

// Sprint 23 WS-A3 (#255) — Container Apps Jobs for the skills-evidence simulators.
// Manual-trigger only; never started by a GitHub workflow. Writes synthetic
// extracts to the WS-A1 landing zone via its User-Assigned Managed Identity.
module skillsSimJobs './modules/experience-hosting/skills-sim-jobs/main.bicep' = if (enableSkillsSimJobsModule) {
  name: 'skills-sim-jobs-${environmentName}'
  params: {
    location: simCapacityLocation
    nameSuffix: resourceSuffix
    tags: tags
    containerAppEnvironmentName: 'cae-skills-sim-${resourceSuffix}'
    logAnalyticsWorkspaceResourceId: resourceId('Microsoft.OperationalInsights/workspaces', platformFoundation.outputs.logAnalyticsWorkspaceName)
    containerImage: skillsSimJobsImage
    // Reuse the sim-capacity ACR params — same registry serves all Container Apps.
    containerRegistryLoginServer: simCapacityContainerRegistryLoginServer
    containerRegistryResourceId: simCapacityContainerRegistryResourceId
    landingStorageAccountName: masterdataLandingStorageName
    landingContainerName: 'landing'
    demoScope: simCapacityDemoScope
  }
}

// Sprint 23 WS-A4 (#255) — Container Apps Job for the skills-EVENTS simulator.
// Manual-trigger only; never started by a GitHub workflow. Publishes synthetic
// DC-SKILL-EVENT-v1 records to the live SIT Eventstream CustomEndpoint, reading
// the SAS connection string from Key Vault via a secret reference (keyless).
// Reuses the skills-sim managed environment when that module is enabled to avoid
// a duplicate CAE; otherwise the module creates its own.
module skillsEventSimJob './modules/experience-hosting/skills-event-sim-job/main.bicep' = if (enableSkillsEventSimJobModule) {
  name: 'skills-event-sim-job-${environmentName}'
  params: {
    location: simCapacityLocation
    nameSuffix: resourceSuffix
    tags: tags
    containerAppEnvironmentId: enableSkillsSimJobsModule ? skillsSimJobs!.outputs.managedEnvironmentId : ''
    containerAppEnvironmentName: 'cae-skev-${resourceSuffix}'
    logAnalyticsWorkspaceResourceId: resourceId('Microsoft.OperationalInsights/workspaces', platformFoundation.outputs.logAnalyticsWorkspaceName)
    containerImage: skillsEventSimJobImage
    // Reuse the sim-capacity ACR params — same registry serves all Container Apps.
    containerRegistryLoginServer: simCapacityContainerRegistryLoginServer
    containerRegistryResourceId: simCapacityContainerRegistryResourceId
    keyVaultName: platformFoundation.outputs.keyVaultName
    connectionStringSecretName: skillsEventConnectionStringSecretName
    demoScope: simCapacityDemoScope
  }
}

// Sprint 28 WS-INF (#377) — Curavias Product Owner Agent (Foundry IQ domain #1).
// Deterministic corpus storage name (mirrored from the corpus-landing module) so
// the runtime refresh job can target it without a circular module reference.
var poCorpusStorageName = toLower('stcorpus${replace(resourceSuffix, '-', '')}')

// AI Search — GA substrate for the shared Foundry IQ Knowledge Layer.
module poAgentSearch './modules/knowledge-layer/ai-search/main.bicep' = if (enablePoAgentSearchModule) {
  name: 'po-agent-search-${environmentName}'
  params: {
    location: poAgentLocation
    nameSuffix: resourceSuffix
    tags: tags
    logAnalyticsWorkspaceId: poAgentLogAnalyticsWorkspaceId
  }
}

// Foundry IQ knowledge-base marker (naming + pinned-version contract only;
// provisioned via the knowledge-base-rest.md runbook — not Bicep-provisionable).
module poAgentKnowledgeBase './modules/knowledge-layer/foundry-iq-knowledge-base/main.bicep' = if (enablePoAgentKnowledgeBaseModule) {
  name: 'po-agent-knowledge-base-${environmentName}'
  params: {
    nameSuffix: resourceSuffix
    searchRestApiVersion: enablePoAgentSearchModule ? poAgentSearch!.outputs.pinnedSearchRestApiVersion : '2024-05-01-preview'
  }
}

// PO Agent runtime — Container App + scheduled corpus-refresh job + Cosmos audit
// + Azure OpenAI + Key Vault. Depends on the Search module for the reader grant;
// corpus storage name is deterministic (no module dependency).
module poAgentRuntime './modules/experience-hosting/po-agent-runtime/main.bicep' = if (enablePoAgentRuntimeModule) {
  name: 'po-agent-runtime-${environmentName}'
  params: {
    location: poAgentLocation
    nameSuffix: resourceSuffix
    tags: tags
    containerAppEnvironmentName: 'cae-po-${resourceSuffix}'
    logAnalyticsWorkspaceResourceId: resourceId('Microsoft.OperationalInsights/workspaces', platformFoundation.outputs.logAnalyticsWorkspaceName)
    containerImage: poAgentContainerImage
    corpusRefreshContainerImage: poAgentCorpusRefreshContainerImage
    // Reuse the sim-capacity ACR params — same registry serves all Container Apps.
    containerRegistryLoginServer: simCapacityContainerRegistryLoginServer
    containerRegistryResourceId: simCapacityContainerRegistryResourceId
    searchEndpoint: enablePoAgentSearchModule ? poAgentSearch!.outputs.searchEndpoint : ''
    searchServiceId: enablePoAgentSearchModule ? poAgentSearch!.outputs.searchServiceId : ''
    searchRestApiVersion: enablePoAgentSearchModule ? poAgentSearch!.outputs.pinnedSearchRestApiVersion : '2024-05-01-preview'
    searchIndexName: 'idx-curavias-corpus-${resourceSuffix}'
    fabricDataAgentEndpoint: fabricDataAgentEndpoint
    fabricWorkspaceId: fabricWorkspaceId
    fabricDataAgentId: fabricDataAgentId
    corpusStorageAccountName: poCorpusStorageName
    openAiLocation: poAgentOpenAiLocation
    logAnalyticsWorkspaceId: poAgentLogAnalyticsWorkspaceId
    demoScope: simCapacityDemoScope
  }
}

// Corpus landing — ADLS Gen2 for synthetic product documents. Grants the runtime
// MI (writer) and the Search MI (reader) via RBAC; no keys.
module poAgentCorpusLanding './modules/knowledge-layer/corpus-landing/main.bicep' = if (enablePoAgentCorpusLandingModule) {
  name: 'po-agent-corpus-landing-${environmentName}'
  params: {
    location: poAgentLocation
    nameSuffix: resourceSuffix
    tags: tags
    refreshJobPrincipalId: enablePoAgentRuntimeModule ? poAgentRuntime!.outputs.principalId : ''
    searchPrincipalId: enablePoAgentSearchModule ? poAgentSearch!.outputs.searchPrincipalId : ''
    logAnalyticsWorkspaceId: poAgentLogAnalyticsWorkspaceId
  }
}

module aiMlFoundation './modules/ai-ml-foundation/main.bicep' = if (enableAiMlFoundationModule) {
  name: 'ai-ml-foundation-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    // Pass the actual KV + ACR names so the ML workspace resolves them under
    // environments that use override names / disable api-runtime (PROD swn).
    // Empty falls back to the derived SIT names inside the module.
    keyVaultName: platformFoundation.outputs.keyVaultName
    containerRegistryName: empty(simCapacityContainerRegistryResourceId) ? '' : last(split(simCapacityContainerRegistryResourceId, '/'))
  }
  // Key Vault parallel-operation race. This module resolves the KV via
  // `existing` (matched name), so Bicep cannot infer an implicit dependency;
  // without dependsOn, ARM may re-apply both modules concurrently and hit
  // `ConflictError: parallel operations on Key Vault` (observed on deploy
  // run 29356935951). See ADR-nothing-yet (may promote to ADR if the pattern
  // repeats on other foundation modules).
  dependsOn: [
    platformFoundation
  ]
}

module integrationOrchestration './modules/integration-orchestration/main.bicep' = if (enableIntegrationOrchestrationModule) {
  name: 'integration-orchestration-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

// Sprint 09 v2.0.0 T4.5 — Foundry-hosted runtime agents (BM-Copilot + CSA).
// Attaches Managed Identities + RBAC to the already-provisioned Foundry
// resource `ai-<solutionShortName>-<env>`. Does NOT create the Foundry
// resource itself (owned by ai-platform/main.bicep).
module foundryHostedAgents './modules/agents/foundry-hosted/main.bicep' = if (enableFoundryHostedAgents) {
  name: 'foundry-hosted-agents-${environmentName}'
  params: {
    location: foundryHostedAgentsLocation
    environment: environmentName
    solutionShortName: solutionShortName
    eventHubNamespaceName: foundryHostedAgentsEventHubNamespace
    eventHubName: foundryHostedAgentsEventHubName
    bmCopilotConsumerGroup: foundryHostedAgentsBmCopilotConsumerGroup
    csaConsumerGroup: foundryHostedAgentsCsaConsumerGroup
    tags: tags
  }
}

// Sprint 09 v2 — T3.7: sim-capacity ACA producer. Only deploys when a target Event Hub namespace is known
// (either passed explicitly via simCapacityEventHubNamespace or produced by the data-foundation module).
var simCapacityHasEhSource = !empty(simCapacityEventHubNamespace) || enableDataFoundationModule
var resolvedSimEventHubNamespace = !empty(simCapacityEventHubNamespace)
  ? simCapacityEventHubNamespace
  : (enableDataFoundationModule ? dataFoundation!.outputs.eventHubNamespaceName : '')

module simCapacity './modules/apps/sim-capacity/main.bicep' = if (enableSimCapacityModule && simCapacityHasEhSource) {
  name: 'sim-capacity-${environmentName}'
  params: {
    location: simCapacityLocation
    containerAppName: 'ca-sim-capacity-${resourceSuffix}'
    containerAppEnvironmentName: 'cae-sim-${resourceSuffix}'
    logAnalyticsWorkspaceResourceId: resourceId('Microsoft.OperationalInsights/workspaces', platformFoundation.outputs.logAnalyticsWorkspaceName)
    containerImage: simCapacityContainerImage
    containerRegistryLoginServer: simCapacityContainerRegistryLoginServer
    containerRegistryResourceId: simCapacityContainerRegistryResourceId
    eventHubNamespace: resolvedSimEventHubNamespace
    eventHubName: simCapacityEventHubName
    demoScope: simCapacityDemoScope
    tags: tags
  }
}

// Sprint 13 T5 — Container Apps agent-host + Cosmos (conversations/audit/approval-events)
// + Redis (grounding cache) per ADR-0007. Agent-host image lands via agent-host-build.yml
// once CI push is wired; deploys with placeholder image today (parity with sim-capacity pattern).
// Log Analytics resourceId passed in; module derives customerId/sharedKey internally via
// reference()/listKeys() — same pattern as sim-capacity, no keys crossing module boundaries.
module agentHost './modules/agent-host/main.bicep' = if (enableAgentHostModule) {
  name: 'agent-host-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    agentHostImage: agentHostImage
    logAnalyticsWorkspaceResourceId: resourceId('Microsoft.OperationalInsights/workspaces', platformFoundation.outputs.logAnalyticsWorkspaceName)
    enableRedisModule: agentHostEnableRedis
    fabricDataAgentEndpoint: fabricDataAgentEndpoint
    fabricWorkspaceId: fabricWorkspaceId
    fabricDataAgentId: fabricDataAgentId
    foundryProjectEndpoint: foundryProjectEndpoint
    foundryProjectName: foundryProjectName
    fabricLakehouseId: fabricLakehouseId
    rlsProvider: agentHostRlsProvider
    oboEnabled: agentHostOboEnabled
    oboTenantId: agentHostOboTenantId
    oboClientId: agentHostOboClientId
    oboKeyVaultId: !empty(agentHostOboKeyVaultId) ? agentHostOboKeyVaultId : resourceId('Microsoft.KeyVault/vaults', platformFoundation.outputs.keyVaultName)
    oboClientSecretName: agentHostOboClientSecretName
    oboJwksUrl: agentHostOboJwksUrl
    oboAudience: agentHostOboAudience
    oboIssuer: agentHostOboIssuer
    oboFabricScope: agentHostOboFabricScope
    // Reuse the sim-capacity ACR params — same registry serves all three CAs.
    containerRegistryLoginServer: simCapacityContainerRegistryLoginServer
    containerRegistryResourceId: simCapacityContainerRegistryResourceId
    // ADR-0029 Option A — wire CAE VNet integration + Cosmos PE when the
    // network module is enabled. Empty strings otherwise (keeps the CAE
    // public — matches legacy behaviour).
    caeInfrastructureSubnetResourceId: enableNetworkModule ? network!.outputs.caeSubnetResourceId : ''
    vnetResourceId: enableNetworkModule ? network!.outputs.vnetResourceId : ''
  }
}

// Sprint 16 T1 / issue #252 Phase A — CSA Cosmos DB (vector-search scenario
// catalogue + agent memory). Previously a standalone deploy
// (infra/modules/cosmos/main.bicep); wiring it here brings it under CI what-if
// and the SIT/PROD parity gate. Tags + name suffix match the standalone shape,
// so adopting the already-deployed SIT account is idempotent. The agent-host MI
// (created inside the agent-host module) receives Cosmos DB Built-in Data
// Contributor via agentHostMiPrincipalId — the implicit output reference makes
// csaCosmos deploy after agentHost, so the MI exists before the role bind. PE
// plumbing follows the network module: on in SIT (MCAPSGov requires it), public
// in PROD/eastus2 (network off, synthetic-only per ADR-0013).
module csaCosmos './modules/cosmos/csa.bicep' = if (enableCsaCosmosModule) {
  name: 'csa-cosmos-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    agentHostMiPrincipalId: enableAgentHostModule ? agentHost!.outputs.agentHostMiPrincipalId : ''
    enablePrivateEndpoint: enableNetworkModule
    vnetResourceId: enableNetworkModule ? network!.outputs.vnetResourceId : ''
    privateEndpointSubnetName: 'snet-data'
  }
}

// Sprint 13 T1 — Fluent baseline Container App (React/Vite bundle behind nginx on 8080).
// Sprint 19 follow-up — external-signals provider-runner (ca-signal-runner).
// Wired here so it survives future CAE delete/recreate (ADR-0029 Option A made
// the CAE immutable-after-create; a redeploy previously destroyed the manually
// provisioned runner). Consumes the agent-host CAE resource id + the
// data-foundation Event Hub namespace/name — implicit output references make it
// deploy after both. Grants the runner MI `Azure Event Hubs Data Sender` at the
// namespace scope. Idempotent: same app name/config adopts the live runner.
module signalRunner '../data-platform/external-signals/provider-runner/main.bicep' = if (enableSignalRunnerModule && enableAgentHostModule && enableDataFoundationModule) {
  name: 'signal-runner-${environmentName}'
  params: {
    location: location
    envSuffix: environmentName
    managedEnvironmentId: agentHost!.outputs.managedEnvironmentId
    eventHubNamespace: dataFoundation!.outputs.eventHubNamespaceName
    eventHubName: dataFoundation!.outputs.eventHubName
  }
}

// Sprint 26 WS-C follow-up (#335) — in-VNet decision-tier live-apply job.
// Manual-trigger Container Apps Job on the agent-host CAE (VNet-integrated →
// Cosmos PE reachable, ADR-0029) reusing the agent-host MI (already a Cosmos
// Built-in Data Contributor). Plan-first by default; a live apply is an
// operator-driven `az containerapp job start` override that supplies
// `--approved-to-apply <handle>` (AGENTS.md §4). Consumes the agent-host CAE +
// the CSA Cosmos document endpoint — implicit output references make it deploy
// after both. Idempotent: same job name/config adopts an existing job.
module decisionApplyJob './modules/decision-apply-job/main.bicep' = if (enableDecisionApplyJobModule && enableAgentHostModule && enableCsaCosmosModule) {
  name: 'decision-apply-job-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    managedEnvironmentId: agentHost!.outputs.managedEnvironmentId
    containerImage: empty(decisionApplyJobImage) ? agentHostImage : decisionApplyJobImage
    cosmosEndpoint: csaCosmos!.outputs.documentEndpoint
    cosmosDatabase: csaCosmos!.outputs.databaseName
    containerRegistryLoginServer: simCapacityContainerRegistryLoginServer
    containerRegistryResourceId: simCapacityContainerRegistryResourceId
    demoScope: location != 'switzerlandnorth'
  }
}

// Same reasoning as agent-host for the Log Analytics wiring.
module appFluent './modules/apps/hcc-app-fluent/main.bicep' = if (enableAppFluentModule) {
  name: 'app-fluent-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    appImage: appFluentImage
    logAnalyticsWorkspaceResourceId: resourceId('Microsoft.OperationalInsights/workspaces', platformFoundation.outputs.logAnalyticsWorkspaceName)
    // #447 runtime agent-host URL (per-env), injected into window.__ENV__ at container start.
    agentHostUrl: appFluentAgentHostUrl
    // Sprint 42 runtime po-agent-service URL (per-env), injected into window.__ENV__ at container start.
    poAgentUrl: appFluentPoAgentUrl
    // #424 M2 golden-source URL (per-env); empty auto-derives `${agentHostUrl}/golden`.
    goldenSourceUrl: appFluentGoldenSourceUrl
    // #424 M3 live per-agent thread minting gate (native provider until M5/OBO).
    foundryThreadsEnabled: appFluentFoundryThreadsEnabled
    // Sprint A — MSAL + app-env runtime config injected into window.__ENV__ at container start.
    msalClientId: appFluentMsalClientId
    msalTenantId: appFluentMsalTenantId
    msalRedirectUri: appFluentMsalRedirectUri
    appEnv: appFluentAppEnv
    homeHospital: appFluentHomeHospital
    // Sprint 43 WS-6 — OBO-forwarded chat grounding scope.
    agentHostScope: appFluentAgentHostScope
    // Reuse the sim-capacity ACR params — same registry serves all three CAs.
    containerRegistryLoginServer: simCapacityContainerRegistryLoginServer
    containerRegistryResourceId: simCapacityContainerRegistryResourceId
    // Sprint 13.1 T-DNS — public custom hostname per ADR-0030.
    customHostname: appFluentCustomHostname
    enableCustomDomainCert: appFluentEnableCustomDomainCert
  }
}

// Sprint 13.1 T-DNS — curavias.ch public DNS zone (ADR-0030).
// Deployed when enableAppFluentModule is true AND appFluentCustomHostname is non-empty.
// SIT owns the zone in rg-ihzhhpf-sit; PROD will reference via `existing` in a follow-up
// PR when PROD RG is provisioned.
//
// Record names derived from the custom hostname's leftmost label (e.g. "appsit" from
// "appsit.curavias.ch"). The CNAME target is the CA's Azure-provided ingress FQDN; the
// TXT value is the CA's customDomainVerificationId. Both flow from the app-fluent
// module output — no cross-boundary secrets.
var appFluentSubdomainLabel = (enableAppFluentModule && !empty(appFluentCustomHostname))
  ? substring(appFluentCustomHostname, 0, indexOf(appFluentCustomHostname, '.'))
  : ''

module curaviasDns './modules/dns/curavias.bicep' = if (enableAppFluentModule && !empty(appFluentCustomHostname) && manageCuraviasDnsZone) {
  name: 'curavias-dns-${environmentName}'
  params: {
    zoneName: 'curavias.ch'
    tags: tags
    cnameRecords: [
      {
        name: appFluentSubdomainLabel
        target: appFluent!.outputs.appFluentFqdn
        ttl: 3600
      }
    ]
    txtRecords: [
      {
        name: 'asuid.${appFluentSubdomainLabel}'
        values: [ appFluent!.outputs.customDomainVerificationId ]
        ttl: 3600
      }
    ]
  }
}

@description('Azure DNS name servers for curavias.ch. Set these as NS records at the GoDaddy registrar to delegate the zone. See docs/runbooks/curavias-dns-godaddy-delegation.md.')
output curaviasNameServers array = (enableAppFluentModule && !empty(appFluentCustomHostname) && manageCuraviasDnsZone) ? curaviasDns!.outputs.nameServers : []

// Sprint 09 v2.0.0 T2.2 — Fabric Eventstream scaffold. See modules/data-platform/fabric-eventstream/README.md.
// Region is constrained to switzerlandnorth | westus2 to keep Bicep type-safe; falls back to westus2 for the
// ADR-0013 demo-scope carve-out when the RG location is something else.
module fabricEventstream './modules/data-platform/fabric-eventstream/main.bicep' = if (enableFabricEventstreamModule) {
  name: 'fabric-eventstream-${environmentName}'
  params: {
    workspaceId: fabricEventstreamWorkspaceId
    eventHubNamespace: enableDataFoundationModule ? dataFoundation!.outputs.eventHubNamespaceEndpoint : ''
    eventHubName: enableDataFoundationModule ? dataFoundation!.outputs.eventHubName : ''
    eventHubConsumerGroup: 'cg-fabric-eventstream'
    location: location == 'switzerlandnorth' ? 'switzerlandnorth' : 'westus2'
    demoScope: location != 'switzerlandnorth'
    destinationLakehouseId: fabricEventstreamDestinationLakehouseId
  }
}

// Sprint 23 WS-A4 (#255) — Skills-events Eventstream lane (design D4). Scaffold-only Bicep +
// REST-API post-deploy; carries ONLY the three near-real-time skills events. Reuses the
// Sprint 21 real-time rail (Event Hub source). Region constrained as above.
module skillsEventstream './modules/integration-orchestration/skills-eventstream/main.bicep' = if (enableSkillsEventstreamModule) {
  name: 'skills-eventstream-${environmentName}'
  params: {
    workspaceId: skillsEventstreamWorkspaceId
    sourceMode: skillsEventstreamSourceMode
    eventHubNamespace: enableDataFoundationModule ? dataFoundation!.outputs.eventHubNamespaceEndpoint : ''
    eventHubName: enableDataFoundationModule ? dataFoundation!.outputs.skillsEventHubName : ''
    eventHubConsumerGroup: 'cg-skills-eventstream'
    location: location == 'switzerlandnorth' ? 'switzerlandnorth' : 'westus2'
    demoScope: location != 'switzerlandnorth'
    destinationLakehouseId: skillsEventstreamDestinationLakehouseId
  }
}

output keyVaultName string = platformFoundation.outputs.keyVaultName
output logAnalyticsWorkspaceName string = platformFoundation.outputs.logAnalyticsWorkspaceName
output sourceSqlGatingWarning string = enableSourceSqlModule && !enableDataPlatformModule
  ? 'WARN: enableSourceSqlModule=true requires enableDataPlatformModule=true; source-sql module will NOT deploy.'
  : 'ok'
output fabricFoundationGatingWarning string = enableFabricFoundationModule && !enableDataPlatformModule
  ? 'WARN: enableFabricFoundationModule=true requires enableDataPlatformModule=true; fabric module will NOT deploy.'
  : (enableFabricFoundationModule && empty(fabricCapacityAdmins))
    ? 'WARN: enableFabricFoundationModule=true but fabricCapacityAdmins is empty; deploy will fail.'
    : 'ok'
output fabricEventstreamGatingWarning string = enableFabricEventstreamModule && !enableDataFoundationModule
  ? 'WARN: enableFabricEventstreamModule=true requires enableDataFoundationModule=true; Eventstream module will fail.'
  : (enableFabricEventstreamModule && empty(fabricEventstreamWorkspaceId))
    ? 'WARN: enableFabricEventstreamModule=true but fabricEventstreamWorkspaceId is empty; provide the workspace GUID from configure-fabric.ps1 output.'
    : (enableFabricEventstreamModule && empty(fabricEventstreamDestinationLakehouseId))
      ? 'INFO: fabricEventstreamDestinationLakehouseId empty — Eventstream will be created source-only. Wire lakehouseId post-deploy.'
      : 'ok'
output skillsEventstreamGatingWarning string = enableSkillsEventstreamModule && skillsEventstreamSourceMode == 'EventHub' && !enableDataFoundationModule
  ? 'WARN: enableSkillsEventstreamModule=true with sourceMode=EventHub requires enableDataFoundationModule=true; skills Eventstream has no Event Hub source. (CustomEndpoint source needs no Event Hub.)'
  : (enableSkillsEventstreamModule && empty(skillsEventstreamWorkspaceId))
    ? 'WARN: enableSkillsEventstreamModule=true but skillsEventstreamWorkspaceId is empty; provide the workspace GUID from configure-fabric.ps1 output before post-deploy.'
    : (enableSkillsEventstreamModule && empty(skillsEventstreamDestinationLakehouseId))
      ? 'INFO: skillsEventstreamDestinationLakehouseId empty — Eventstream will be created source-only. Wire lakehouseId post-deploy.'
      : 'ok'
output moduleStatuses object = {
  identity: enableIdentityModule ? identity!.outputs.moduleStatus : 'identity-disabled'
  network: enableNetworkModule ? network!.outputs.moduleStatus : 'network-disabled'
  observability: enableObservabilityModule ? observability!.outputs.moduleStatus : 'observability-disabled'
  dataPlatform: enableDataPlatformModule ? dataPlatform!.outputs.moduleStatus : 'data-platform-disabled'
  sourceSql: enableDataPlatformModule ? dataPlatform!.outputs.sourceSqlStatus : 'source-sql-disabled'
  aiPlatform: enableAiPlatformModule ? aiPlatform!.outputs.moduleStatus : 'ai-platform-disabled'
  integration: enableIntegrationModule ? integration!.outputs.moduleStatus : 'integration-disabled'
  experienceHosting: enableExperienceHostingModule ? experienceHosting!.outputs.moduleStatus : 'experience-hosting-disabled'
  apiRuntime: enableApiRuntimeModule ? apiRuntime!.outputs.moduleStatus : 'api-runtime-disabled'
  dataFoundation: enableDataFoundationModule ? dataFoundation!.outputs.moduleStatus : 'data-foundation-disabled'
  masterdataLanding: enableMasterdataLandingModule ? masterdataLanding!.outputs.moduleStatus : 'masterdata-landing-disabled'
  skillsSimJobs: enableSkillsSimJobsModule ? skillsSimJobs!.outputs.moduleStatus : 'skills-sim-jobs-disabled'
  skillsEventSimJob: enableSkillsEventSimJobModule ? skillsEventSimJob!.outputs.moduleStatus : 'skills-event-sim-job-disabled'
  poAgentSearch: enablePoAgentSearchModule ? poAgentSearch!.outputs.moduleStatus : 'po-agent-search-disabled'
  poAgentKnowledgeBase: enablePoAgentKnowledgeBaseModule ? poAgentKnowledgeBase!.outputs.moduleStatus : 'po-agent-knowledge-base-disabled'
  poAgentCorpusLanding: enablePoAgentCorpusLandingModule ? poAgentCorpusLanding!.outputs.moduleStatus : 'po-agent-corpus-landing-disabled'
  poAgentRuntime: enablePoAgentRuntimeModule ? poAgentRuntime!.outputs.moduleStatus : 'po-agent-runtime-disabled'
  aiMlFoundation: enableAiMlFoundationModule ? aiMlFoundation!.outputs.moduleStatus : 'ai-ml-foundation-disabled'
  integrationOrchestration: enableIntegrationOrchestrationModule ? integrationOrchestration!.outputs.moduleStatus : 'integration-orchestration-disabled'
  fabricEventstream: enableFabricEventstreamModule ? fabricEventstream!.outputs.moduleStatus : 'fabric-eventstream-disabled'
  skillsEventstream: enableSkillsEventstreamModule ? skillsEventstream!.outputs.moduleStatus : 'skills-eventstream-disabled'
}

output foundryHostedAgentsStatus string = enableFoundryHostedAgents ? foundryHostedAgents!.outputs.moduleStatus : 'foundry-hosted-agents-disabled'
output bmCopilotPrincipalId string = enableFoundryHostedAgents ? foundryHostedAgents!.outputs.bmCopilotPrincipalId : ''
output bmCopilotClientId string = enableFoundryHostedAgents ? foundryHostedAgents!.outputs.bmCopilotClientId : ''
output csaPrincipalId string = enableFoundryHostedAgents ? foundryHostedAgents!.outputs.csaPrincipalId : ''
output csaClientId string = enableFoundryHostedAgents ? foundryHostedAgents!.outputs.csaClientId : ''

// Exposed for T2.1 EH module wiring — read by the parent deployment to feed Azure Event Hubs Data Sender RBAC.
output simCapacityPrincipalId string = (enableSimCapacityModule && simCapacityHasEhSource)
  ? simCapacity!.outputs.principalId
  : ''
output simCapacityStatus string = enableSimCapacityModule
  ? (!simCapacityHasEhSource
      ? 'WARN: enableSimCapacityModule=true but no Event Hub namespace resolved (set simCapacityEventHubNamespace or enable data-foundation module).'
      : simCapacity!.outputs.moduleStatus)
  : 'sim-capacity-disabled'
