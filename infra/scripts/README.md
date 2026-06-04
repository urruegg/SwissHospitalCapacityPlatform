# Infra Scripts

Sprint 03 baseline is workflow-first.

No imperative deployment scripts are required for standard deployments because GitHub Actions workflows under `.github/workflows/` run Bicep build, what-if, and deployment.

## Bootstrap Exception

`register-resource-providers.ps1` is provided for subscription-owner bootstrap. Use this when deployment identities do not have permissions to register Azure resource providers.

Example:

```powershell
./infra/scripts/register-resource-providers.ps1 -SubscriptionId <subscription-id>
```
