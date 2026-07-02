@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('App Service plan SKU name.')
param appServicePlanSkuName string = 'B1'

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'asp-platform-${nameSuffix}'
  location: location
  tags: tags
  sku: {
    name: appServicePlanSkuName
    tier: contains(['B1', 'B2', 'B3'], appServicePlanSkuName) ? 'Basic' : 'Standard'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource commandCenterWebApp 'Microsoft.Web/sites@2023-12-01' = {
  name: 'app-platform-${nameSuffix}'
  location: location
  tags: tags
  kind: 'app,linux'
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
      minTlsVersion: '1.2'
      alwaysOn: false
    }
  }
}

@description('Experience hosting module implementation marker.')
output moduleStatus string = 'experience-hosting-implemented'

@description('App Service plan name.')
output appServicePlanName string = appServicePlan.name

@description('Command center web app name.')
output webAppName string = commandCenterWebApp.name
