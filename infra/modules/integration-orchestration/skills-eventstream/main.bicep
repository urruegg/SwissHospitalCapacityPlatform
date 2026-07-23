targetScope = 'resourceGroup'

// Sprint 23 WS-A4 (#255) — Skills-events Eventstream lane (design D4).
//
// SCAFFOLD-ONLY BICEP + POST-DEPLOY REST-API PATTERN.
//
// Mirrors modules/data-platform/fabric-eventstream/main.bicep: Fabric Eventstream is a
// workspace-scoped Fabric item, NOT an ARM/Bicep resource (the Microsoft.Fabric ARM
// provider exposes only `capacities`). This module therefore declares the design-spec
// parameters as first-class Bicep inputs so parent composition + what-if stay accurate,
// and emits a configuration manifest consumed by a companion post-deploy REST script.
// It provisions no ARM resources itself, so its what-if footprint is additive/empty.
//
// Design D4 (hybrid transport): the Eventstream lane is intentionally NARROW — it carries
// ONLY the three near-real-time skills events that must move faster than the next batch
// master-data load. Everything else (HRIS/LMS master data) goes through the batch/ADLS
// landing-zone lane (WS-A1..A3). Reuses the Sprint 21 real-time rail (Event Hub ->
// Eventstream -> Eventhouse/lakehouse). Ingestion runs as Azure Container Apps, never
// GitHub workflows.

@description('Fabric workspace ID (GUID) that hosts the Eventstream. Obtain via GET /v1/workspaces after workspace creation. Empty at Bicep composition time when provisioned post-deploy; the companion PS1 refuses to run until the manifest carries it.')
param workspaceId string = ''

@description('Fully-qualified Event Hubs namespace hostname (e.g. evh-ihzhhpf-sit-xxxx.servicebus.windows.net). Passed from the data-foundation/eventhubs module output.')
param eventHubNamespace string = ''

@description('Event Hub name carrying the skills-event envelopes. Routing is by the eventKind message property; the Eventstream filters to the three allowed kinds.')
param eventHubName string = ''

@description('Consumer group the Eventstream subscribes to for skills events. Dedicated group keeps this lane isolated from the capacity/fabric consumer groups.')
param eventHubConsumerGroup string = 'cg-skills-eventstream'

@description('Deployment region. switzerlandnorth (ADR-0003 default) or westus2 (ADR-0013 demo-scope carve-out).')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param location string

@description('True when the module deploys under the ADR-0013 demo-scope carve-out (US region, synthetic data only, no PHI). Recorded in the manifest so post-deploy enforces the PHI-gate downstream.')
param demoScope bool = false

@description('Display name for the Eventstream item in the Fabric workspace.')
param eventstreamDisplayName string = 'es-ihzhhpf-skills-events'

@description('Description for the Eventstream item.')
param eventstreamDescription string = 'Sprint 23 WS-A4 (D4) — near-real-time skills events (credential expiry, consent grant/revoke, newly-confirmed assertion); routes by eventKind, appends to bronze/skills-events/ Delta.'

@description('Destination Lakehouse ID (GUID) that receives Delta append writes at bronze/skills-events/. Empty defers destination wiring to a follow-up post-deploy pass.')
param destinationLakehouseId string = ''

@description('Destination Lakehouse table prefix under bronze/ for skills events.')
param destinationTablePrefix string = 'bronze_skills_events'

// D4: the event set is deliberately limited to these three near-real-time kinds. Any
// broadening is a design change (design §6 open items) and must be reviewed — the
// companion post-deploy script asserts the Eventstream filter matches this list exactly.
var allowedEventKinds = [
  'credential-expiry'
  'consent-grant-or-revoke'
  'newly-confirmed-assertion'
]

var skillsEventstreamManifest = {
  provisioningMode: 'fabric-rest-api-post-deploy'
  workspaceId: workspaceId
  eventstream: {
    displayName: eventstreamDisplayName
    description: eventstreamDescription
  }
  source: {
    kind: 'EventHub'
    namespaceHost: eventHubNamespace
    eventHubName: eventHubName
    consumerGroup: eventHubConsumerGroup
    routingProperty: 'eventKind'
    // D4 guardrail: the Eventstream filter admits ONLY these three kinds. Enforced by the
    // post-deploy script and echoed here so operators can audit the narrow scope.
    allowedEventKinds: allowedEventKinds
    authMode: 'fabric-managed-connection'
  }
  destination: {
    kind: 'Lakehouse'
    lakehouseId: destinationLakehouseId
    tablePrefix: destinationTablePrefix
    lakehousePath: 'Files/bronze/skills-events/'
  }
  guardrails: {
    location: location
    demoScope: demoScope
    // PHI gate is enforced by the silver notebook, not by the Eventstream itself; recorded
    // so operators know the Eventstream lands raw synthetic envelopes and gating is downstream.
    phiGateEnforcedBy: 'silver-skills-events-notebook (WS-B)'
    residencyTag: location == 'switzerlandnorth' ? 'CH-North' : 'US-West'
    eventSetScope: 'narrow-D4-three-events'
  }
}

@description('Skills-events Eventstream configuration manifest consumed by the post-deploy REST script.')
output eventstreamManifest object = skillsEventstreamManifest

@description('The exact three near-real-time event kinds this lane carries (design D4).')
output allowedEventKinds array = allowedEventKinds

@description('Human-readable status for the parent orchestration.')
output moduleStatus string = 'skills-eventstream-scaffold-only-see-post-deploy-script'

@description('Path (repo-relative) to the companion post-deploy script that materialises the Eventstream via Fabric REST API.')
output postDeployScriptPath string = 'infra/modules/integration-orchestration/skills-eventstream/post-deploy/configure-skills-eventstream.ps1'
