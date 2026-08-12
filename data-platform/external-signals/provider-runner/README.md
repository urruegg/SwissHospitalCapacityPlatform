# Provider-runner Container App

The provider-runner Container App hosts signal provider adapters, simulators, and internal providers. It orchestrates their execution and publishes standardized `DC-EXT-SIGNAL-v1` records to an existing Event Hub for consumption by the data-quality and signal-triage pipelines.

## Purpose

The provider-runner is a stateless Container App that:

1. **Hosts provider adapters** - adapters for live external bindings (SED, Alertswiss, etc.) and internal forecast generators.
2. **Runs simulators** - synthetic data generators for CI/test environments and demo scenarios.
3. **Publishes standardized signals** - all outputs conform to the `DC-EXT-SIGNAL-v1` schema and are sent to an Event Hub for downstream consumption.
4. **Manages lifecycle** - scales from zero when idle; fires on-demand or on schedule.

## Deployment

Deployment of the provider-runner is **gated by human approval**:

1. **Plan phase** - the landing-zone agent or drift analyzer generates a `what-if` summary showing the Container App resource delta (create or update).
2. **Approval gate** - a human reviewer reads the plan and replies on the issue or PR thread with a comment containing the exact phrase: `approved-to-apply`.
3. **Apply phase** - only after approval is the Container App provisioned or updated.

This gate ensures that any changes to provider connectivity, Event Hub bindings, or workload identity configuration are reviewed before live deployment.

## CI and Live Bindings

### CI (Continuous Integration)

In CI pipelines:

- All live external bindings (SED, Alertswiss, etc.) are **mocked**.
- Only internal simulators and synthetic providers run.
- Mocked providers emit sample `DC-EXT-SIGNAL-v1` records for contract validation.
- The pipeline does **not** call real endpoints or consume real licenses.

### Live Deployment

Live deployment to SIT or PROD:

- Requires explicit endpoint URLs and credential stores (Azure Key Vault references, not inline secrets).
- Requires a vetted **license verification list** (provider credentials, API keys, OAuth scopes) approved by the compliance lane before promotion.
- The Container App uses **Workload Identity Federation** - no connection strings, API keys, or secrets are embedded in code or configuration.
- Each live binding is tagged with its data source, license status, and approval date in the Event Hub message envelope.

## Identity and Access

The provider-runner uses a **system-assigned managed identity**:

- The identity is created automatically when the Container App is deployed.
- It is scoped to publish messages to the Event Hub via the `Azure Event Hubs Data Sender` role. This role assignment is **provisioned declaratively by `main.bicep`** as a namespace-scoped assignment, so every environment (SIT, PROD) grants it consistently at deploy time.
- Workload Identity Federation (OIDC) is configured in the Container Apps environment to allow the identity to assume Azure roles without storing credentials.

## Target environment parameters

The template is environment-parameterised. Discovered parameter sets for the
`ihzhhpf` demo tenant (`MngEnvMCAP164444`, region `westus2` per ADR-0013):

| Parameter | SIT (deployed) | PROD (prepared) |
|-----------|----------------|-----------------|
| `envSuffix` | `sit` | `prod` |
| resource group | `rg-ihzhhpf-sit` | `rg-ihzhhpf-prod` |
| `managedEnvironmentId` | `cae-sim-ihzhhpf-sit` | `cae-ihzhhpf-prod` |
| `eventHubNamespace` | `evh-ihzhhpf-sit-y26y` | `evh-ihzhhpf-prod-i62t` |
| `eventHubName` | `events` | `events` |

PROD deployment follows the same gate: `what-if` plan, human `approved-to-apply`,
then `az deployment group create`. PROD has no `cae-sim` environment, so the
runner targets the general `cae-ihzhhpf-prod` managed environment.

## Configuration

Key parameters passed to the Bicep template:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `envSuffix` | Environment suffix (sit, prod) | `sit` |
| `managedEnvironmentId` | Resource ID of the Container Apps managed environment | `/subscriptions/.../resourceGroups/.../providers/Microsoft.App/managedEnvironments/cae-ihzhhpf-sit` |
| `eventHubNamespace` | Event Hub namespace name | `evh-ihzhhpf-sit` |
| `eventHubName` | Event Hub name for external signals | `external-signals` |
| `location` | Azure region (defaults to resource group location) | `switzerlandnorth` |

The Container App is configured with:

- **Image** - `mcr.microsoft.com/azure-cli:latest` (placeholder; replaced with a custom provider-runner image at deployment time).
- **Scale** - min replicas: 0, max replicas: 1 (scales to zero when idle, up to 1 active instance when processing).
- **Environment variables** - `EVENT_HUB_NAMESPACE` and `EVENT_HUB_NAME` injected at runtime.

## Schema and Output

All signals published by the provider-runner conform to the **DC-EXT-SIGNAL-v1** schema (defined in `docs/data-contracts/DC-EXT-SIGNAL-v1.md`).

A signal is a JSON document:

```json
{
  "version": "DC-EXT-SIGNAL-v1",
  "timestamp": "2026-07-23T10:35:52.349+02:00",
  "provider": "seda-adapter",
  "signal_type": "bed_occupancy",
  "facility_id": "hospital-st-gallen-001",
  "data": {
    "occupied_beds": 120,
    "total_beds": 150
  },
  "metadata": {
    "source": "SED",
    "license_status": "valid",
    "approval_date": "2026-07-01"
  }
}
```

## Bicep Template

The provider-runner is provisioned via the Bicep template in `main.bicep`:

```bash
az deployment group create \
  --resource-group <rg> \
  --template-file data-platform/external-signals/provider-runner/main.bicep \
  --parameters envSuffix=sit \
    managedEnvironmentId=/subscriptions/.../providers/Microsoft.App/managedEnvironments/cae-ihzhhpf-sit \
    eventHubNamespace=evh-ihzhhpf-sit \
    eventHubName=external-signals
```

## Related Artifacts

- **Data contract** - `docs/data-contracts/DC-EXT-SIGNAL-v1.md`
- **Signal-triage-agent** - `agents/signal-triage-agent/AGENT.md` (consumes, deduplicates, and triages signals)
- **Data-quality-agent** - `agents/data-quality-agent/AGENT.md` (validates schema, handles quarantine)
- **Eventstream topology** - Signal records are loaded into an Eventstream for real-time downstream consumption

## Live Web IQ activation (SIT / PROD)

The runner ships **simulator-only** by default. Two auth paths exist; **keyless
Entra ID (managed identity) is preferred** on this platform — it matches the
RBAC-only / keyless posture and sidesteps the private Key Vaults (the SIT vault
`kv-ihzhhpf-sit-y26y` has no private endpoint, so a Container App Key Vault
secret reference can't resolve it there).

### Preferred: keyless Entra ID

1. **Deploy the runner** (real `signal-runner` image from
   `ci-build-signal-runner.yml`) so its identity `id-signal-runner-ihzhhpf-<env>`
   exists, then read its client id:

   ```bash
   az identity show -g rg-ihzhhpf-sit --name id-signal-runner-ihzhhpf-sit --query clientId -o tsv
   ```

2. **Bind that client id** in the Web IQ portal → Profile Management →
   *Application (Client) IDs* → *Bind Application (Client) ID*. If the tab is
   absent, request a dedicated AppID via your Microsoft contact (Entra auth can
   be unavailable in trial scenarios).

3. **Enable + deploy** through the `what-if` → `approved-to-apply` gate:

   | Param | SIT | PROD |
   |-------|-----|------|
   | `providerRunnerImage` | `cri75lbu5sj4hza.azurecr.io/signal-runner:<sha>` | `crihzhhpfprod.azurecr.io/signal-runner:<sha>` (import from SIT ACR first) |
   | `webiqEntraEnabled` | `true` | `true` |
   | `managedEnvironmentId` | `cae-ihzhhpf-sit` (VNet-integrated) | `cae-ihzhhpf-prod` (VNet-integrated) |
   | `signalResidency` | `demo-westus2` | `CH` |

No Key Vault, no secret, no private-network path required.

### Fallback: x-apikey (local / eval)

Set `webiqSecretUri` (Key Vault secret `webiq-api-key`) + `keyVaultName`. This
needs the Container App to reach the vault's private endpoint — viable on PROD
(`kv-ihzhhpf-prod-swn1` has a PE) but **not SIT** (`kv-ihzhhpf-sit-y26y` has
none). The operator provisions the secret out-of-band
(`az keyvault secret set --vault-name kv-ihzhhpf-prod-swn1 --name webiq-api-key
--value <KEY>`), never in IaC.

Leaving both unset keeps the environment simulator-only (the live binding falls
back automatically). CI always runs simulator-only (`NFR-EXT-PLG-001`). See
[ADR-0060](../../../docs/adr/0060-webiq-external-signal-channel.md).
