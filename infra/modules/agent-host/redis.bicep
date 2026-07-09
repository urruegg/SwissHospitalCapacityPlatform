@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

// Sprint 13 T5 — Azure Cache for Redis grounding + session cache (ADR-0007 §1).
// Basic C0 for the demo scope (ADR-0013). TLS-only; access-key auth is disabled
// in favour of Entra (managed identity) auth.

resource redis 'Microsoft.Cache/redis@2024-03-01' = {
  name: 'redis-${nameSuffix}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'Basic'
      family: 'C'
      capacity: 0
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    redisConfiguration: {
      'aad-enabled': 'true'
    }
    publicNetworkAccess: 'Enabled'
  }
}

output redisName string = redis.name
output redisHostName string = redis.properties.hostName
