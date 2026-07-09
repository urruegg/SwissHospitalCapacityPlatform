// Sample Bicep module (fixture)
resource sampleVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-sample'
}

resource sampleStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stsample'
}
