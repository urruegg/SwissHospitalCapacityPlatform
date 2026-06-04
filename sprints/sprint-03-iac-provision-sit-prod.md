# Sprint 3 - IaC Provisioning for SIT and PROD

| Field | Value |
| ----- | ----- |
| **Version** | 1.9.0 |
| **Date** | 2026-06-04 |
| **Author** | Urs Rueegg |
| **Status** | In Progress |
| **Previous Version** | 1.8.0 (captured phased SIT rollout and provider-registration constraint handling) |

## Sprint Goal

Provision the platform baseline defined in `docs/SD.md` as infrastructure as code for `SIT` and `PROD`, and establish GitHub Actions CI/CD workflows with approval-gated promotion.

## Trigger Model

This sprint is executed as a GitHub Issue-driven run. The sprint issue is the tracking anchor, and `@copilot` is the execution trigger for creating and validating IaC and workflow artefacts.

## Traceability

- GitHub Issue: [#6](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/6)
- GitHub Project: Swiss Hospital Capacity Platform Delivery
- Design baseline: `docs/SD.md`
- Architecture baseline: `docs/ARCHITECTURE.md`
- Requirement baseline: `docs/PRD.md`
- Repo-wide guardrails: `.github/copilot-instructions.md`

## Scope

### In scope

- Define and implement IaC modules for SIT and PROD landing-zone-aligned platform resources.
- Apply naming standard from SD:
  - solution short name: `chhealthpf`
  - SIT resources must use suffix `-sit`
  - PROD resources must use suffix `-prod`
  - shared resources across environments have no environment suffix
- Build environment parameterization for SIT and PROD with explicit policy and RBAC boundaries.
- Configure CI workflows for lint, validate, and what-if checks on IaC changes.
- Configure CD workflows for gated SIT deploy and approval-gated PROD promote/deploy.
- Publish repository structure for IaC modules, environment parameters, and workflows.

### Out of scope

- Application feature implementation in runtime services.
- Destructive operations (delete/destroy) in production subscriptions.
- Cross-cloud deployment patterns.
- EPR implementation details beyond IaC placeholders.

## Required IaC Deliverables

1. Root composition entrypoint for platform infrastructure (`infra/main.bicep`).
2. Reusable Bicep modules under `infra/modules/` for core domains:
   - identity and access baseline
   - networking baseline
   - observability and diagnostics
   - data and integration platform foundations
   - AI platform foundations (where GA and SD-aligned)
3. Environment parameter files under `infra/environments/`:
   - `sit.bicepparam`
   - `prod.bicepparam`
4. Required tagging enforcement on all resources:
   - `env`, `owner`, `costCenter`, `workload`
5. CI-validatable what-if execution profiles for SIT and PROD scopes.

## Required CI/CD Workflow Configuration

### CI workflow requirements

1. Trigger on pull requests touching `infra/**`, `.github/workflows/**`, and architecture-governance docs impacted by IaC.
2. Run checks in order:
   - markdown lint and link check (when docs changed)
   - Bicep build validation
   - Bicep linter validation
   - what-if simulation for SIT (mandatory)
   - what-if simulation for PROD (mandatory for PRs targeting release/promotion)
3. Publish validation evidence to PR checks and summary.

### CD workflow requirements

1. SIT deploy workflow:
   - trigger: merge to `main` with `infra/**` changes
   - required input: SIT subscription/resource-group context
   - run `what-if` before apply
   - deploy only on successful validation
2. PROD deploy workflow:
   - trigger: manual (`workflow_dispatch`) or promotion event
   - enforce environment approval gate
   - run `what-if` before apply
   - deploy only after explicit approval
3. All deploy workflows must use OIDC/workload identity and never use long-lived secrets.

## Tenant and Environment Configuration Baseline (Best Practice)

### GitHub Environments and Protection Rules

1. Create GitHub Environments:
  - `sit`
  - `prod`
2. Configure protection rules:
  - `sit`: required reviewers optional, short wait timer optional.
  - `prod`: required reviewers mandatory, wait timer mandatory, deployment branch policy restricted.
3. Store non-secret runtime values as **Environment Variables** and sensitive values as **Environment Secrets**.
4. Use OIDC federation for Azure authentication; do not use publish profiles, client secrets, or long-lived credentials.

### GitHub Environment Variables (non-secret)

Use environment-scoped variables (`Settings` -> `Environments` -> `<env>` -> `Variables`) for:

| Variable | SIT | PROD | Notes |
| ----- | ----- | ----- | ----- |
| `AZURE_TENANT_ID` | Required | Required | Tenant where target subscription resides. |
| `AZURE_SUBSCRIPTION_ID` | Required | Required | Subscription per environment. |
| `AZURE_LOCATION` | `switzerlandnorth` | `switzerlandnorth` | Primary deployment region from SD baseline. |
| `AZURE_RESOURCE_GROUP` | Required | Required | Environment-specific target resource group. |
| `BICEP_PARAM_FILE` | `infra/environments/sit.bicepparam` | `infra/environments/prod.bicepparam` | Points workflow to correct parameter file. |
| `ENV_NAME` | `sit` | `prod` | Used for tagging and deployment logs. |
| `SOLUTION_SHORT_NAME` | `chhealthpf` | `chhealthpf` | Naming standard enforcement. |

### GitHub Environment Secrets (only when needed)

Prefer zero secrets with OIDC. If required by tooling, store only environment-scoped sensitive values:

| Secret | SIT | PROD | Notes |
| ----- | ----- | ----- | ----- |
| `AZURE_CLIENT_ID` | Required for OIDC federated identity | Required for OIDC federated identity | Service principal/app registration client ID only; not a secret value by itself but treated as controlled config in environment scope. |
| `KV_BOOTSTRAP_CERT` | Optional | Optional | Only when bootstrap certificate material is required by deployment process. |

Rules:
1. Never store client secrets in GitHub when OIDC is available.
2. Never duplicate PROD secrets at repository-level scope.
3. Rotate any non-OIDC sensitive material and document owner/rotation cadence.

### Azure Key Vault Configuration (SIT and PROD)

Provision separate vaults per environment:
- `kv-chhealthpf-sit`
- `kv-chhealthpf-prod`

Configuration requirements:
1. Enable RBAC authorization model (avoid legacy access policies unless explicitly required).
2. Enable soft-delete and purge protection.
3. Disable public access where landing-zone policy requires private endpoints.
4. Grant least-privilege roles:
  - deployment identity: `Key Vault Secrets Officer` or narrower write scope only when needed
  - runtime identities: `Key Vault Secrets User` read-only scope
5. Keep secrets environment-local; never share SIT secrets with PROD.

### Azure Key Vault Secret and Key Baseline

Use Key Vault for application/integration secrets and certificate material. Keep names consistent across environments.

Recommended secret names in both `sit` and `prod` vaults:
- `appinsights-connection-string`
- `servicebus-connection-string`
- `storage-account-connection-string`
- `external-api-client-secret`
- `entra-client-secret` (only if a non-OIDC flow is unavoidable and approved)

Recommended key and certificate names:
- key: `cmk-platform`
- certificate: `tls-platform`

Operational controls:
1. Set expiration and rotation policy on secrets/keys/certificates.
2. Enable diagnostic logs for secret get/set/delete and key operations.
3. Alert on near-expiry, disabled secrets, and unauthorized access attempts.
4. Reference Key Vault secrets from workloads by URI, not inline values.

## Repository Structure (Sprint 3 Target)

```text
.github/
  workflows/
    ci-infra-validate.yml
    cd-infra-deploy-sit.yml
    cd-infra-deploy-prod.yml
infra/
  main.bicep
  modules/
    identity/
    network/
    observability/
    data-platform/
    ai-platform/
    integration/
  environments/
    sit.bicepparam
    prod.bicepparam
  scripts/
    validate.ps1
    deploy-sit.ps1
    deploy-prod.ps1
docs/
  SD.md
  ARCHITECTURE.md
  INFRASTRUCTURE.md
sprints/
  sprint-03-iac-provision-sit-prod.md
```

## Planned Work Items

1. Confirm SD-derived infrastructure scope and convert to module backlog.
2. Scaffold `infra/` module layout and SIT/PROD parameter files.
3. Implement naming, tags, and environment policy constraints in modules.
4. Add CI workflow for lint, build, and what-if checks.
5. Add CD workflows for SIT auto-deploy and PROD approval-gated deploy.
6. Validate with dry-run evidence and update sprint traceability.

## Implementation Progress (Current)

### Completed in first implementation slice

1. Created IaC scaffold under `infra/`:
  - `infra/main.bicep`
  - `infra/modules/platform-foundation/main.bicep`
  - `infra/environments/sit.bicepparam`
  - `infra/environments/prod.bicepparam`
2. Created CI/CD workflow scaffold under `.github/workflows/`:
  - `ci-infra-validate.yml`
  - `cd-infra-deploy-sit.yml`
  - `cd-infra-deploy-prod.yml`
3. Implemented OIDC-based Azure login pattern in workflow templates.
4. Implemented `what-if` gate before SIT and PROD deployment steps.

### Completed in second implementation slice

1. Aligned SIT deployment workflow trigger to run on merge to `main` with `infra/**` path filtering.
2. Converted PROD deployment workflow to support promotion-event triggering from successful SIT deployment (`workflow_run`) and explicit manual confirmation (`approved-to-apply`).
3. Extended `ci-infra-validate.yml` to include:
  - conditional markdown lint and link checks when IaC-governance docs change,
  - explicit Bicep lint validation,
  - retained mandatory SIT and PROD `what-if` simulation jobs.
4. Added the missing baseline infrastructure documentation file `docs/INFRASTRUCTURE.md`.
5. Scaffolded additional module domains under `infra/modules/`:
  - `identity/`
  - `network/`
  - `observability/`
  - `data-platform/`
  - `ai-platform/`
  - `integration/`

### Completed in third implementation slice

1. Replaced scaffold placeholders with first concrete resources for:
  - `identity/`: user-assigned managed identity baseline,
  - `network/`: virtual network and application subnet baseline,
  - `observability/`: Application Insights component baseline.
2. Added safe composition parameters in `infra/main.bicep` for network CIDR control and retained feature-flag module enablement.
3. Enabled identity, network, and observability modules for `SIT` in `infra/environments/sit.bicepparam`.

### Completed in fourth implementation slice

1. Replaced remaining module scaffolds with first concrete resources for:
  - `data-platform/`: storage account baseline with blob service retention policy,
  - `ai-platform/`: Azure AI Services account baseline,
  - `integration/`: Service Bus namespace baseline.
2. Enabled data-platform, ai-platform, and integration modules for `SIT` in `infra/environments/sit.bicepparam`.

### Completed in fifth implementation slice

1. Configured explicit PROD enablement strategy as **phased rollout** in `infra/environments/prod.bicepparam`.
2. Set module enablement flags to `false` for PROD until SIT end-to-end validation and production approval gates are completed.

### Completed in sixth implementation slice

1. Hardened SIT and PROD deployment workflows to register required Azure resource providers before deployment steps.
2. Added provider registration coverage for namespaces required by current module set (OperationalInsights, KeyVault, ManagedIdentity, Network, Insights, Storage, CognitiveServices, ServiceBus).

### Completed in seventh implementation slice

1. Applied temporary SIT phased enablement for modules requiring subscription-level provider registrations not currently permitted for the deployment identity.
2. Updated deployment workflows so provider-registration attempts are best-effort and emit warnings when authorization is insufficient, instead of hard-failing pre-deploy.

### Pending in next slice

1. Configure repository GitHub Environments (`sit`, `prod`) with required variables and approvals.
2. Configure federated identity credentials and environment-scoped Azure context values.
3. Complete full provider-registration by subscription owner for ManagedIdentity, Network, Storage, CognitiveServices, and ServiceBus.
4. Re-enable currently phased SIT modules and rerun end-to-end verification with full module set.
5. Execute explicit change-controlled enablement for PROD modules after SIT verification evidence is approved.

## Subscription Owner Provider Registration Proposal (Starting Point)

Objective: unblock full SIT parity deployment and reduce promotion risk to PROD by standardizing one owner-executed provider bootstrap.

Scope:

- SIT and PROD subscriptions targeted by Sprint 3 workflows.
- Required namespaces:
  - Microsoft.OperationalInsights
  - Microsoft.KeyVault
  - Microsoft.ManagedIdentity
  - Microsoft.Network
  - Microsoft.Insights
  - Microsoft.Storage
  - Microsoft.CognitiveServices
  - Microsoft.ServiceBus

Execution model:

1. Subscription owner runs provider bootstrap once per subscription.
2. Delivery team reruns SIT deployment with full module set enabled.
3. Promotion to PROD remains approval-gated and evidence-based.

Operator commands:

```powershell
./infra/scripts/register-resource-providers.ps1 -SubscriptionId <sit-subscription-id>
./infra/scripts/register-resource-providers.ps1 -SubscriptionId <prod-subscription-id>
```

Verification command pattern:

```bash
az provider show --namespace Microsoft.CognitiveServices --query registrationState -o tsv
```

Success criteria:

1. All namespaces return `Registered` for both subscriptions.
2. SIT deployment workflow completes with full module set enabled.
3. Deployment evidence is attached to PR and sprint artefacts before PROD module enablement.

## Acceptance Criteria

- SIT and PROD IaC parameterization exists and is CI-validated.
- Resource naming rules for `chhealthpf` are consistently enforced across modules and parameters.
- CI workflow fails on lint/build/what-if violations and reports actionable diagnostics.
- SIT deploy is automated and gated by successful validation.
- PROD deploy requires explicit approval and successful what-if.
- Sprint issue is linked bidirectionally with this sprint document.

## Risks and Dependencies

1. Subscription and RBAC readiness for SIT and PROD may delay deploy enablement.
2. Some control-plane resources may require staged deployment sequencing.
3. Policy assignments may require tenant-level permissions outside sprint ownership.

## Notes

Sprint 3 is the implementation bridge between design baseline (`docs/SD.md`) and repeatable, controlled environment provisioning for SIT and PROD.
