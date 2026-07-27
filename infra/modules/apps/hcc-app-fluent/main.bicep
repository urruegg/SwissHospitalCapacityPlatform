// Sprint 13 T1 — hcc-app-fluent Container App (React/Vite Fluent baseline UI).
// Static bundle served via nginx-unprivileged on port 8080. System-assigned MI so the
// app-shell can request tokens for downstream MSAL OBO flows (Graph, agent-host /chat).
// Minimal by design — the app itself is a static single-page app, not a stateful service.

@description('Azure region.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Container image the app runs (registry/repository:tag). Defaults to nginx-unprivileged placeholder; swap to the built app-fluent image once app-build.yml pushes to ACR.')
param appImage string = 'nginxinc/nginx-unprivileged:1.27-alpine'

@description('Log Analytics workspace resource ID used by the ACA managed environment. Derived from platform-foundation at the top-level main.bicep.')
param logAnalyticsWorkspaceResourceId string

@description('Optional ACR login server (e.g. cri75lbu5sj4hza.azurecr.io) for MI-based image pull. Required together with containerRegistryResourceId to enable no-secrets pull once real images land.')
param containerRegistryLoginServer string = ''

@description('Optional ACR resource ID. Required together with containerRegistryLoginServer.')
param containerRegistryResourceId string = ''

@description('Minimum replica count.')
@minValue(0)
@maxValue(10)
param minReplicas int = 1

@description('Maximum replica count.')
@minValue(1)
@maxValue(30)
param maxReplicas int = 3

@description('Container target port. Fluent Dockerfile serves via nginx-unprivileged on 8080.')
param targetPort int = 8080

@description('#447 — Foundry agent-host base URL injected into the app at container start (window.__ENV__.AGENT_HOST_URL). Per-env value (SIT vs PROD agent-host FQDN); empty keeps the built-in mock. Runtime injection replaces the former build-time VITE_AGENT_HOST_URL bake so a single image is env-agnostic.')
param agentHostUrl string = ''

@description('Public custom hostname for the CA ingress (e.g. appsit.curavias.ch, app.curavias.ch). Empty string leaves the CA on its default *.azurecontainerapps.io hostname. See ADR-0030.')
param customHostname string = ''

@description('When true and customHostname is non-empty, provision a Managed Certificate on the CAE and bind it to the CA ingress. Set FALSE during the first deploy (or when curavias.ch NS delegation to Azure DNS is not yet propagated) to avoid managed-cert issuance failure. Runbook: docs/runbooks/curavias-dns-godaddy-delegation.md.')
param enableCustomDomainCert bool = false

@description('ADR-0031 opt-in. Fully-qualified resource ID of an EXISTING certificate on the CAE (either Microsoft.App/managedEnvironments/certificates — imported from Key Vault — or a pre-provisioned managedCertificates resource). When non-empty AND enableCustomDomainCert=true, this ID is used as the CA customDomains[0].certificateId instead of the Bicep-provisioned managed cert. Empty (default) keeps the current ACA-managed cert path. The Key Vault import itself is provisioned out-of-band in a dedicated module when PROD switches per ADR-0031 §Trigger.')
param existingCustomDomainCertificateResourceId string = ''

// AcrPull role definition id (built-in).
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'
var useAcrMiPull = !empty(containerRegistryLoginServer) && !empty(containerRegistryResourceId)

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-app-fluent-${nameSuffix}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsWorkspaceResourceId, '2023-09-01').customerId
        sharedKey: listKeys(logAnalyticsWorkspaceResourceId, '2023-09-01').primarySharedKey
      }
    }
    zoneRedundant: false
  }
}

// User-assigned MI for the app-fluent CA. Created BEFORE the CA so the AcrPull
// role assignment can land first — the CA then references an already-authorised
// identity when it triggers its first (or updated) revision pull. Matches the
// sim-capacity pattern.
resource appFluentIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-ca-app-fluent-${nameSuffix}'
  location: location
  tags: tags
}

// AcrPull on the ACR when MI-based pull is enabled. Scoped to the ACR resource
// so the identity has only pull rights on this one registry.
resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' existing = if (useAcrMiPull) {
  name: last(split(containerRegistryResourceId, '/'))
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useAcrMiPull) {
  scope: acr
  name: guid(containerRegistryResourceId, appFluentIdentity.id, acrPullRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalId: appFluentIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 13 T1 — hcc-app-fluent CA pulls image from ACR via user-assigned MI.'
  }
}

// Managed certificate for the custom hostname (Azure Container Apps managed PKI —
// currently DigiCert / GeoTrust TLS RSA CA G1 in commercial regions, historically
// Let's Encrypt).
// Provisioned only when the caller has confirmed DNS zone + records are live at Azure DNS
// AND the GoDaddy NS delegation for curavias.ch has propagated (enableCustomDomainCert=true).
// Cert issuance is synchronous — deploy will FAIL if DNS validation cannot complete, so keep
// enableCustomDomainCert=false until the runbook confirms propagation.
//
// ADR-0031: SKIPPED when existingCustomDomainCertificateResourceId is set — the caller
// takes over cert ownership (typically via a Key Vault import). See ADR-0031
// §Trigger for when to switch.
var useExistingCert = !empty(existingCustomDomainCertificateResourceId)

resource managedCert 'Microsoft.App/managedEnvironments/managedCertificates@2024-03-01' = if (enableCustomDomainCert && !empty(customHostname) && !useExistingCert) {
  parent: managedEnvironment
  name: 'cert-${replace(customHostname, '.', '-')}'
  location: location
  properties: {
    subjectName: customHostname
    domainControlValidation: 'CNAME'
  }
}

resource appFluent 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-app-fluent-${nameSuffix}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${appFluentIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: managedEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
        allowInsecure: false
        // ADR-0030 two-phase custom-domain handling. Azure managed cert issuance
        // requires the hostname to already be registered on a CA in the CAE
        // (otherwise: RequireCustomHostnameInEnvironment). Bicep can't create
        // the cert and the hostname binding in one deploy because they have a
        // dependency cycle, so we split it:
        //
        //   * Phase 1 (enableCustomDomainCert=false): register the hostname on
        //     the CA with bindingType=Disabled - no cert yet, but the CAE knows
        //     the hostname is claimed.
        //   * Phase 2 (enableCustomDomainCert=true): create the managed cert
        //     (validation succeeds because the hostname is already registered),
        //     then update the binding to SniEnabled + certificateId.
        //
        // Empty customHostname => empty customDomains (legacy behaviour).
        // ADR-0031: certificateId resolves to `existingCustomDomainCertificateResourceId`
        // when set (KV-backed or imported cert), otherwise the Bicep-provisioned
        // ACA-managed cert.
        customDomains: empty(customHostname) ? [] : (enableCustomDomainCert ? [
          {
            name: customHostname
            bindingType: 'SniEnabled'
            certificateId: useExistingCert ? existingCustomDomainCertificateResourceId : managedCert!.id
          }
        ] : [
          {
            name: customHostname
            bindingType: 'Disabled'
          }
        ])
      }
      registries: useAcrMiPull ? [
        {
          server: containerRegistryLoginServer
          identity: appFluentIdentity.id
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'app-fluent'
          image: appImage
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          // #447 runtime env injection — read at container start by
          // docker-entrypoint.d/30-env-config.sh into window.__ENV__.
          env: [
            {
              name: 'AGENT_HOST_URL'
              value: agentHostUrl
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
      }
    }
  }
  dependsOn: [
    acrPullRoleAssignment
  ]
}

@description('Container App FQDN (ingress URL host).')
output appFluentFqdn string = appFluent.properties.configuration.ingress.fqdn

@description('Container App name.')
output appFluentName string = appFluent.name

@description('User-assigned MI principal ID (for OBO/Graph token wiring).')
output appFluentPrincipalId string = appFluentIdentity.properties.principalId

@description('User-assigned MI client ID.')
output appFluentClientId string = appFluentIdentity.properties.clientId

@description('User-assigned MI resource ID.')
output appFluentIdentityResourceId string = appFluentIdentity.id

@description('Container Apps custom-domain verification ID. Used to populate the asuid.<hostname> TXT record in the curavias.ch DNS zone so the CAE managedCertificate can validate ownership.')
output customDomainVerificationId string = appFluent.properties.customDomainVerificationId
