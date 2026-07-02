# Tenant Migration Runbook — MCAP228255 → MCAP164444

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Status** | Draft — ready for execution |
| **Previous Version** | N/A |

## Purpose and scope

Operator-driven procedure to rebuild SIT and PROD environments in the new Entra tenant, without disturbing the current tenant. Follows the design decisions locked in [docs/superpowers/specs/2026-07-02-tenant-migration-design.md](../superpowers/specs/2026-07-02-tenant-migration-design.md) v1.1.0.

Runbook style: numbered, checkbox-driven. Every real Azure change is gated by an explicit `approved-to-apply` comment on the deploy PR per [AGENTS.md §4](../../AGENTS.md#4-confirmation-rule-for-deploy--delete) and user memory (delete/destructive ops require explicit approval).

Fixed values used throughout:

- Source tenant: `2dfb4d85-3ca7-474e-86eb-9ba3762d9474` (`MngEnvMCAP228255.onmicrosoft.com`)
- Target tenant: `1337187a-4c41-4da9-8fca-731bba7a4329` (`MngEnvMCAP164444.onmicrosoft.com`)
- Target subscription (SIT + PROD, single sub for demo scope): `66a9953a-df37-4c51-856c-9971b9bf3e03`
- Region: `westus2` — **demo scope only** per [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md); [ADR-0003](../adr/0003-swiss-regional-inference-for-phi.md) `switzerlandnorth` remains the default for all PHI and production scope
- Data: **synthetic sample data only** (`data/synthetic/`) — no PHI, no real patient identifiers, no connection to any Swiss KIS source
- Solution short name (new): `ihzhhpf`
- SIT resource group: `rg-ihzhhpf-sit`
- PROD resource group: `rg-ihzhhpf-prod`
- GitHub repo: `urruegg/SwissHospitalCapacityPlatform`

## Prerequisites (before §1)

- [ ] Operator has full Entra tenant admin + subscription Owner in the new tenant
- [ ] Single subscription `66a9953a-df37-4c51-856c-9971b9bf3e03` provisioned in the new tenant (hosts both SIT and PROD RGs per D9)
- [ ] Empty resource groups `rg-ihzhhpf-sit` and `rg-ihzhhpf-prod` pre-created in that subscription in `westus2`
- [ ] Workstation has PowerShell 7+, Azure CLI 2.60+, Az PowerShell 12+, GitHub CLI 2.50+, Pester 5.x
- [ ] Spec [`2026-07-02-tenant-migration-design.md`](../superpowers/specs/2026-07-02-tenant-migration-design.md) v1.2.0 and this runbook are merged to `main`
- [ ] [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md) is Accepted and the exception `EX-2026-07-02-westus2-demo` is present in `policy/exceptions.json`
- [ ] Phase-1 PR from plan Task 15 is merged (scripts + rename are on `main`)

---

## §1 Tenant plane (W1)

Purpose: everything one-time in the new tenant that must happen before any SIT/PROD deploy.

### 1.0 Developer workstation trust

- [ ] Run [`Enable-DeveloperTenantTrust.ps1`](../../infra/scripts/tenant-migration/Enable-DeveloperTenantTrust.ps1):

  ```powershell
  ./infra/scripts/tenant-migration/Enable-DeveloperTenantTrust.ps1 `
      -TenantId 1337187a-4c41-4da9-8fca-731bba7a4329 `
      -SubscriptionId 66a9953a-df37-4c51-856c-9971b9bf3e03
  ```

- [ ] Confirm the script prints `az account show` matches the new tenant + subscription
- [ ] Confirm `Get-AzContext` matches
- [ ] Confirm VS Code Azure Resources extension lists new-tenant subscriptions without a device-code prompt
- [ ] Optional: complete Workplace Join (Settings → Accounts → Access work or school → Connect); verify with `dsregcmd /status`

**Gate G0.3** — pass criteria: silent SSO works from Azure CLI, Az PowerShell, and VS Code.

### 1.1 Provider registration on SIT and PROD subscriptions

- [ ] For each subscription (SIT then PROD), register the required resource providers:

  ```powershell
  $providers = @(
      'Microsoft.Fabric',
      'Microsoft.KeyVault',
      'Microsoft.OperationalInsights',
      'Microsoft.Insights',
      'Microsoft.ManagedIdentity',
      'Microsoft.Network',
      'Microsoft.Storage',
      'Microsoft.ServiceBus',
      'Microsoft.CognitiveServices'
  )
  foreach ($p in $providers) { az provider register --namespace $p --wait }
  ```

- [ ] Verify all show `registrationState = Registered`:

  ```powershell
  foreach ($p in $providers) { az provider show --namespace $p --query "{ns:namespace, state:registrationState}" -o tsv }
  ```

### 1.2 Entra app registration + federated credentials

- [ ] Run [`New-OidcFederation.ps1`](../../infra/scripts/tenant-migration/New-OidcFederation.ps1):

  ```powershell
  $oidc = ./infra/scripts/tenant-migration/New-OidcFederation.ps1 `
      -DisplayName 'gh-oidc-ihzhhpf' `
      -RepoFullName 'urruegg/SwissHospitalCapacityPlatform'
  ```

- [ ] Record `$oidc.ClientId` and `$oidc.PrincipalId` in the [sprint report](../sprints/sprint-00-new-tenantprovisioning.md) evidence table
- [ ] Verify via portal or CLI:

  ```powershell
  az ad app show --id $oidc.ClientId --query '{id:appId, dn:displayName}' -o table
  az ad app federated-credential list --id $oidc.ClientId --query '[].{name:name, subject:subject}' -o table
  ```

  Expected: two credentials with subjects `repo:urruegg/SwissHospitalCapacityPlatform:environment:sit` and `...:environment:prod`.

### 1.3 Subscription RBAC

- [ ] Grant `Contributor` on the shared subscription (one call — both RGs live in the same sub per D9):

  ```powershell
  ./infra/scripts/tenant-migration/Grant-SubscriptionRbac.ps1 `
      -PrincipalId $oidc.PrincipalId `
      -SubscriptionId 66a9953a-df37-4c51-856c-9971b9bf3e03
  ```

- [ ] Verify:

  ```powershell
  az role assignment list --assignee $oidc.PrincipalId --query "[].{scope:scope, role:roleDefinitionName}" -o table
  ```

**Gate G1** — pass criteria: app reg + 2 fed creds + Contributor on both subs.

### 1.4 GitHub environment configuration

- [ ] Convert the OIDC client ID to a `SecureString` to avoid shell-history leaks:

  ```powershell
  $clientSecure = ConvertTo-SecureString $oidc.ClientId -AsPlainText -Force
  ```

- [ ] Configure the `sit` environment:

  ```powershell
  ./infra/scripts/tenant-migration/Set-GithubEnvironmentConfig.ps1 `
      -RepoFullName 'urruegg/SwissHospitalCapacityPlatform' `
      -Environment sit `
      -TenantId 1337187a-4c41-4da9-8fca-731bba7a4329 `
      -SubscriptionId 66a9953a-df37-4c51-856c-9971b9bf3e03 `
      -ResourceGroup 'rg-ihzhhpf-sit' `
      -BicepParamFile 'infra/environments/sit.bicepparam' `
      -ClientId $clientSecure
  ```

- [ ] Configure the `prod` environment (same script, `-Environment prod`, same subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`, `rg-ihzhhpf-prod`, `prod.bicepparam`)
- [ ] Verify:

  ```powershell
  gh api /repos/urruegg/SwissHospitalCapacityPlatform/environments/sit/variables --jq '.variables[] | {name, value}'
  gh api /repos/urruegg/SwissHospitalCapacityPlatform/environments/prod/variables --jq '.variables[] | {name, value}'
  ```

**Gate G1.1** — pass criteria: both environments show new tenant + subscription IDs.

### 1.5 Fabric prerequisite (source SQL + connection)

_Deferred to just before W2.3 when SIT source-SQL exists. If source SQL has not been deployed yet, skip this step now; it becomes actionable during §2._

- [ ] After SIT source SQL is deployed (see §2), enable its System-Assigned Managed Identity if not already enabled
- [ ] In the Fabric portal (Data Factory → Connections) or via `POST /v1/connections`, create a Fabric connection to the source Azure SQL database in the new tenant
- [ ] Record the resulting `connectionId` — required for `configure-fabric.ps1` in §2.3

---

## §2 SIT deploy + smoke test (W2)

- [ ] **2.1 Dispatch what-if validation:**

  ```powershell
  gh workflow run ci-infra-validate.yml --repo urruegg/SwissHospitalCapacityPlatform --ref main --field environment=sit
  gh run watch --repo urruegg/SwissHospitalCapacityPlatform --exit-status
  ```

  Review the `what-if` output in the workflow logs. If any unexpected deletes appear → STOP, fix Bicep or `sit.bicepparam`, re-run.

- [ ] **2.2 Dispatch SIT deploy:**

  ```powershell
  gh workflow run cd-infra-deploy-sit.yml --repo urruegg/SwissHospitalCapacityPlatform --ref main
  ```

  On the resulting deploy PR/issue thread, comment `approved-to-apply` when the what-if diff is acceptable. Wait for the workflow to complete.

- [ ] **2.3 Fabric post-deploy** (after `Microsoft.Fabric` capacity is provisioned in the SIT RG):

  1. Complete step 1.5 above (create Fabric connection to source SQL, capture `connectionId`)
  2. Run:

     ```powershell
     ./infra/modules/data-platform/fabric/post-deploy/configure-fabric.ps1 `
         -CapacityName 'fabricihzhhpfsit' `
         -ConnectionId '<connection-id-from-1.5>' `
         -SourceDatabase 'kis'
     ```

- [ ] **2.4 Regenerate synthetic data** into the new source SQL:

  ```powershell
  python data/synthetic/generate_planning_datasets.py --root data/synthetic
  # then load into the SIT SQL server — follow data/synthetic/README.md
  ```

- [ ] **2.5 Smoke test** — verify Fabric mirror rehydrated the lakehouse and the semantic model exposes the expected measure. Follow the Verification section of [`docs/superpowers/plans/2026-06-14-sprint-08-week-1-walking-skeleton.md`](../superpowers/plans/2026-06-14-sprint-08-week-1-walking-skeleton.md) — open Power BI, connect to workspace `ws-ihzhhpf-sit-data`, refresh `sm_capacity_data_product`, confirm `Encounter Count > 0`.

**Gates G2, G2.1, G2.2** — pass criteria: what-if clean, deployment `Succeeded`, `Encounter Count > 0`.

---

## §3 PROD deploy + smoke test (W3)

_Only proceed if all §2 gates are green._

- [ ] **3.1 Dispatch what-if for PROD:**

  ```powershell
  gh workflow run ci-infra-validate.yml --repo urruegg/SwissHospitalCapacityPlatform --ref main --field environment=prod
  ```

- [ ] **3.2 Dispatch PROD deploy** (Fabric module remains opt-out per `prod.bicepparam`):

  ```powershell
  gh workflow run cd-infra-deploy-prod.yml --repo urruegg/SwissHospitalCapacityPlatform --ref main
  ```

  Comment `approved-to-apply` on the resulting deploy PR/issue. Wait for completion.

- [ ] **3.3 Verify PROD resource footprint:**

  ```powershell
  az resource list -g rg-ihzhhpf-prod --query "[].{name:name, type:type}" -o table
  ```

**Gate G3** — pass criteria: PROD deployment `Succeeded`, resource footprint matches SIT minus Fabric.

---

## §4 Cutover documentation (W4)

- [ ] **4.1** Fill in [ADR-0012](../adr/0012-tenant-migration-to-mcap164444.md) `Context` / `Decision` / `Consequences` sections with actual execution evidence (dates, subscription IDs, remaining risks). Change status `Proposed` → `Accepted`.
- [ ] **4.2** Update `docs/OPERATIONS.md` service-ownership section to reference the new tenant + subscriptions. Bump SemVer per [copilot-instructions.md §9](../../.github/copilot-instructions.md).
- [ ] **4.3** Update the tenant note added to [`AGENTS.md`](../../AGENTS.md) to read **"new tenant is authoritative; old tenant frozen, teardown deferred"**. Bump SemVer.
- [ ] **4.4** Open a docs-only PR containing 4.1–4.3.

---

## §5 Sprint retrospective (W5)

- [ ] Populate [`sprint-00-new-tenantprovisioning.md`](../sprints/sprint-00-new-tenantprovisioning.md) evidence table with actual dates and PR/workflow URLs
- [ ] Write retrospective bullets (went well / didn't / change next time)
- [ ] Bump sprint file version `0.1.0` → `1.0.0`; set status `Reviewed`
- [ ] Open final sprint PR

---

## Rollback

Mirrors [spec §6](../superpowers/specs/2026-07-02-tenant-migration-design.md#6-rollback):

| Failure point | Rollback |
| ------------- | -------- |
| W0 rename PR breaks a downstream check | `git revert -m 1 <sha>`; historical docs and CI still valid because they weren't renamed. |
| W1 OIDC / RBAC misconfigured | Re-run scripts (idempotent); or `az ad app delete --id <client-id>` (**requires explicit user approval per user memory — no auto-delete**). Old tenant unaffected. |
| W2 SIT what-if diff unexpected | Do not apply. Investigate diff; fix Bicep or `sit.bicepparam`; re-run what-if. |
| W2 SIT apply partial-fail | `az deployment group list -g rg-ihzhhpf-sit` to inspect; **only with explicit user approval**: `az group delete -n rg-ihzhhpf-sit --yes` (no PHI, no durable data) and re-run W2 from 2.1. |
| W2 Fabric post-deploy fails | Re-run `configure-fabric.ps1` (already idempotent per its Pester tests). |
| W3 PROD deploy fails post-apply | Do NOT touch old tenant. Roll forward: fix, re-what-if, re-apply. Old tenant remains fully operational as fallback per D6. |
| W4 doc misfire | `git revert`; no cloud resources touched in W4. |
| GitHub env vars corrupted | `Set-GithubEnvironmentConfig.ps1 -Restore -Environment <env> -SnapshotPath <snapshot.json>` restores previous values from the snapshot captured at 1.4. |

**Nuclear rollback:** delete both RGs in new tenant (**explicit user approval required per user memory**), revert W0 PR merge, run `Set-GithubEnvironmentConfig.ps1 -Restore` for both environments. Old tenant continues serving unchanged.

---

## References

- Spec: [`docs/superpowers/specs/2026-07-02-tenant-migration-design.md`](../superpowers/specs/2026-07-02-tenant-migration-design.md) v1.1.0
- Plan: [`docs/superpowers/plans/2026-07-02-tenant-migration-plan.md`](../superpowers/plans/2026-07-02-tenant-migration-plan.md)
- Script pack: [`infra/scripts/tenant-migration/README.md`](../../infra/scripts/tenant-migration/README.md)
- ADR-0012: [`docs/adr/0012-tenant-migration-to-mcap164444.md`](../adr/0012-tenant-migration-to-mcap164444.md)
- Sprint report: [`docs/sprints/sprint-00-new-tenantprovisioning.md`](../sprints/sprint-00-new-tenantprovisioning.md)
- Confirmation rule: [`AGENTS.md §4`](../../AGENTS.md#4-confirmation-rule-for-deploy--delete)
- Doc versioning: [`.github/copilot-instructions.md §9`](../../.github/copilot-instructions.md)
