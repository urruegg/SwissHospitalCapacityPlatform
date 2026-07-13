// ADR-0030 — curavias.ch DNS zone + records.
//
// Fresh domain registered at GoDaddy, delegated to Azure DNS via NS records at
// the registrar. This module owns the public zone and its child records. Zone
// lives in whichever RG this module is deployed to — for Sprint 13.1 that is
// rg-ihzhhpf-sit (co-located with the SIT env). When PROD spins up in its own
// RG, this module must be refactored to accept an `existing` zone reference so
// only records land — the zone stays owned by SIT.
//
// Records are populated by the caller from Container Apps outputs
// (`ingress.fqdn` for CNAME target, `customDomainVerificationId` for TXT
// value). No secret material crosses module boundaries.

targetScope = 'resourceGroup'

@description('DNS zone name. Fresh domain via GoDaddy (registrar).')
param zoneName string = 'curavias.ch'

@description('Resource tags.')
param tags object = {}

@description('CNAME records. Each item: { name: "appsit", target: "ca-app-fluent-....azurecontainerapps.io", ttl: 3600 }. Empty array creates the zone with no CNAME records.')
param cnameRecords array = []

@description('TXT records for Container Apps custom-domain validation. Each item: { name: "asuid.appsit", values: ["<verificationId>"], ttl: 3600 }. Empty array creates no TXT records.')
param txtRecords array = []

resource zone 'Microsoft.Network/dnsZones@2018-05-01' = {
  name: zoneName
  location: 'global'
  tags: tags
  properties: {
    zoneType: 'Public'
  }
}

resource cnames 'Microsoft.Network/dnsZones/CNAME@2018-05-01' = [for r in cnameRecords: {
  parent: zone
  name: r.name
  properties: {
    TTL: r.ttl
    CNAMERecord: {
      cname: r.target
    }
  }
}]

resource txts 'Microsoft.Network/dnsZones/TXT@2018-05-01' = [for r in txtRecords: {
  parent: zone
  name: r.name
  properties: {
    TTL: r.ttl
    TXTRecords: [
      {
        value: r.values
      }
    ]
  }
}]

@description('Zone name (echo).')
output zoneName string = zone.name

@description('Azure DNS name servers. Set these as NS records at the GoDaddy registrar to delegate the zone. See docs/runbooks/curavias-dns-godaddy-delegation.md.')
output nameServers array = zone.properties.nameServers
