targetScope = 'resourceGroup'

// Sprint 09 v2.0.0 T2.2 — Fabric Eventstream module.
//
// SCAFFOLD-ONLY BICEP + POST-DEPLOY REST-API PATTERN (see README.md).
//
// Fabric Eventstream is a Fabric-workspace-scoped item ("Microsoft.Fabric/workspaces/eventstreams"
// in some documentation) but the `Microsoft.Fabric` ARM provider only exposes `capacities` today
// (verified via ARM provider metadata 2026-07-03; only `Microsoft.Fabric/capacities` API versions
// 2023-11-01 and 2025-01-15-preview are ARM-visible). Fabric items — workspaces, lakehouses,
// mirrors, eventstreams — are provisioned via the Fabric REST API, not ARM/Bicep.
//
// This mirrors the pattern already established by `data-platform/fabric/main.bicep` +
// `post-deploy/configure-fabric.ps1` for workspace + lakehouse + mirror in Sprint 08.
//
// This module therefore:
//   1. Declares the design-spec §4.2 parameters as first-class Bicep inputs (so parent Bicep
//      composition and what-if remain accurate).
//   2. Emits an eventstream configuration manifest as an output that the companion
//      `post-deploy/configure-eventstream.ps1` script consumes.
//   3. Does NOT deploy the Eventstream from ARM — the parent orchestration must call the
//      PS1 script after this deployment completes.
//
// When Microsoft ships a first-class ARM/Bicep type for Fabric Eventstream, this module
// should be rewritten to declare the resource directly (behind ADR-0014 preview gating).

@description('Fabric workspace ID (GUID) that will host the Eventstream. Obtain via GET /v1/workspaces after workspace creation (configure-fabric.ps1 output). Left empty at Bicep composition time when workspace is provisioned in a post-deploy step; the companion PS1 will refuse to run until this is populated in the manifest.')
param workspaceId string = ''

@description('Fully-qualified Event Hubs namespace hostname (e.g. evh-ihzhhpf-sit-xxxx.servicebus.windows.net). Passed from data-foundation/eventhubs module output.')
param eventHubNamespace string = ''

@description('Event Hub name within the namespace. Design spec §4.2 uses a single hub with routing by eventKind message property.')
param eventHubName string = ''

@description('Consumer group the Eventstream subscribes to. Sprint 09 v2.0.0 T2.1 provisions cg-fabric-eventstream for this purpose.')
param eventHubConsumerGroup string = 'cg-fabric-eventstream'

@description('Deployment region. switzerlandnorth (ADR-0003 default) or westus2 (ADR-0013 demo-scope carve-out).')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param location string

@description('True when the module deploys under the ADR-0013 demo-scope carve-out (US region, synthetic data only, no PHI). Documented in output manifest so post-deploy can enforce PHI-gate.')
param demoScope bool = false

@description('Display name for the Eventstream item in the Fabric workspace.')
param eventstreamDisplayName string = 'es-ihzhhpf-events'

@description('Description for the Eventstream item.')
param eventstreamDescription string = 'Sprint 09 v2.0.0 — receives simulator envelopes from Event Hubs (cg-fabric-eventstream), routes by eventKind, appends to bronze/eventstream/ Delta.'

@description('Destination Lakehouse ID (GUID) that will receive Delta append writes at bronze/eventstream/. Obtain via GET /v1/workspaces/{workspaceId}/lakehouses after lakehouse creation. Leave empty to defer destination wiring to a follow-up post-deploy pass.')
param destinationLakehouseId string = ''

@description('Destination Lakehouse table prefix under bronze/. Design spec §4.6 uses eventstream/ as the bronze subfolder.')
param destinationTablePrefix string = 'bronze_eventstream'

// Emit a manifest that the companion PS1 consumes. Serialised as an object output so the parent
// orchestration can capture it via `deployment().outputs` and pipe it into configure-eventstream.ps1.
var eventstreamManifest = {
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
    // Routing property drives per-eventKind Delta partitioning downstream (design spec §4.2).
    routingProperty: 'eventKind'
    // Fabric-managed connection is created out-of-band (portal or POST /v1/connections) and
    // referenced by displayName; ADR-0013 records the demo-scope tenant identity used.
    authMode: 'fabric-managed-connection'
  }
  destination: {
    kind: 'Lakehouse'
    lakehouseId: destinationLakehouseId
    tablePrefix: destinationTablePrefix
    // Bronze layer per design spec §4.6 — silver/gold notebooks (T2.3/T2.4) read from here.
    lakehousePath: 'Files/bronze/eventstream/'
  }
  guardrails: {
    location: location
    demoScope: demoScope
    // ADR-0016 gate enforced by the silver notebook (T2.3), not by Eventstream itself; recorded here
    // so operators know Eventstream WILL land raw envelopes and PHI gating happens downstream.
    phiGateEnforcedBy: 'silver-eventstream-notebook (T2.3)'
    residencyTag: location == 'switzerlandnorth' ? 'CH-North' : 'US-West'
  }
}

@description('Fabric Eventstream configuration manifest consumed by post-deploy/configure-eventstream.ps1.')
output eventstreamManifest object = eventstreamManifest

@description('Human-readable status for the parent orchestration.')
output moduleStatus string = 'fabric-eventstream-scaffold-only-see-post-deploy-script'

@description('Path (repo-relative) to the companion post-deploy script that materialises the Eventstream via Fabric REST API.')
output postDeployScriptPath string = 'infra/modules/data-platform/fabric-eventstream/post-deploy/configure-eventstream.ps1'
