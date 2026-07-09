// Sprint 12 — Entra demo org: adoption telemetry diagnostic setting.
//
// Routes Entra ID SignInLogs (and AuditLogs) to the SIT Log Analytics workspace
// so the adoption-telemetry pipeline (data-platform/notebooks/adoption/) can
// export nightly sign-in events to Fabric Bronze (design spec §7). No PHI —
// sign-in logs carry UPN + IP (redacted to /24 downstream) only.
//
// Azure AD diagnostic settings (microsoft.aadiam/diagnosticSettings) are
// tenant-scoped, so this module is deployed on its own:
//   az deployment tenant create --location westus2 \
//     --template-file infra/modules/entra/adoption-telemetry.bicep \
//     --parameters logAnalyticsWorkspaceResourceId=<la-resource-id>
//
// This is a `deploy`-ceiling action gated behind an `approved-to-apply` comment
// (AGENTS.md §4). It is intentionally NOT chained into main.bicep (which is
// subscription-scoped for the Microsoft Graph resources).

targetScope = 'tenant'

@description('Resource ID of the log-ihzhhpf-sit Log Analytics workspace that receives Entra sign-in logs.')
param logAnalyticsWorkspaceResourceId string

@description('Name of the Azure AD diagnostic setting.')
param diagnosticSettingName string = 'ihzhhpf-adoption-signin'

resource aadDiagnostics 'microsoft.aadiam/diagnosticSettings@2017-04-01-preview' = {
  name: diagnosticSettingName
  scope: tenant()
  properties: {
    workspaceId: logAnalyticsWorkspaceResourceId
    logs: [
      {
        category: 'SignInLogs'
        enabled: true
      }
      {
        category: 'AuditLogs'
        enabled: true
      }
      {
        category: 'NonInteractiveUserSignInLogs'
        enabled: true
      }
      {
        category: 'ServicePrincipalSignInLogs'
        enabled: true
      }
    ]
  }
}

output diagnosticSettingId string = aadDiagnostics.id
