# Sprint 00 — New Tenant Provisioning

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (added Slice 1 + Slice 2 outcome; G2.2 closed as spirit-met with follow-ups) |

## Goal

Rebuild SIT and PROD end-to-end in the new Entra tenant `1337187a-4c41-4da9-8fca-731bba7a4329` (`MngEnvMCAP164444.onmicrosoft.com`) with solution short name `ihzhhpf`, without disturbing the current tenant.

**Scope carve-out (D9 / [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md)):** deployment region is `westus2` for this sprint — demonstration / proof-of-technology scope only, synthetic sample data only, no PHI. Single subscription `66a9953a-df37-4c51-856c-9971b9bf3e03` hosts both SIT and PROD RGs. Sunset back to `switzerlandnorth` when target services reach Swiss GA or exception `EX-2026-07-02-westus2-demo` expires (2026-09-30).

## Scope

- W0 — Repo prep (rename `chhealthpf` → `ihzhhpf` in live/authoritative files)
- W1 — Tenant plane setup (developer trust, OIDC federation, subscription RBAC, GitHub env config, Fabric prereq)
- W2 — SIT deploy + smoke test
- W3 — PROD deploy + smoke test
- W4 — Cutover documentation (ADR-0012, OPERATIONS, AGENTS)
- W5 — This retrospective

Spec: [docs/superpowers/specs/2026-07-02-tenant-migration-design.md](../superpowers/specs/2026-07-02-tenant-migration-design.md) v1.2.0.
Plan: [docs/superpowers/plans/2026-07-02-tenant-migration-plan.md](../superpowers/plans/2026-07-02-tenant-migration-plan.md).

## Workstream evidence

Executed 2026-07-02, single session, operator-driven with `approved-to-apply` gates.

| Workstream | Result | Evidence |
| ---------- | ------ | -------- |
| W0 (repo prep) | Merged | [PR #74](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/74) — rename + 4 scripts + runbook + ADR-0012/0013 scaffolds + spec v1.2.0 (16 commits) |
| W1.0 workstation trust | Green G0.3 | `Enable-DeveloperTenantTrust.ps1`; `az account show` and `Get-AzContext` both on new tenant + subscription. Needed to install `Az.Accounts` + `Az.Resources` PS modules mid-run |
| W1.1 provider registration | 9/9 Registered | `Microsoft.Fabric`, `.KeyVault`, `.OperationalInsights`, `.Insights`, `.ManagedIdentity`, `.Network`, `.Storage`, `.ServiceBus`, `.CognitiveServices` |
| W1.2 OIDC federation | Green G1 | App reg `gh-oidc-ihzhhpf` (client `cbecd109-2ac5-466b-b08e-2a97556274d2`, SP `3ca4e7c3-e2f9-490c-9ee7-cc4d36ea5e2f`), 2 fed creds. **Bug fixed in-place** via `az ad app federated-credential update` — PowerShell string-interpolation issue produced malformed subjects on first run |
| W1.3 subscription RBAC | Granted | `Contributor` on `66a9953a-...` (assignment `4fc3d54e-bb2b-4cd1-af96-d9a16de90a43`) |
| W1.4 GitHub env config | Green G1.1 | `sit` and `prod` environments both updated: 6 core vars + 1 secret + 4 Fabric-scoped vars per env |
| Prereq: RGs + Bicep hotfixes | Merged | `rg-ihzhhpf-sit` + `rg-ihzhhpf-prod` created; [PR #75](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/75) storage uniqueString; [PR #76](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/76) KV/WebApp/EH/SB uniqueString |
| W2 SIT deploy | Succeeded (2m9s) | 16 resources in `rg-ihzhhpf-sit` (`westus2`). `cd-infra-deploy-sit.yml` run 28594388047. Gate G2.1 PASSED |
| W3 PROD deploy | Succeeded (1m30s) | 15 resources in `rg-ihzhhpf-prod` (`westus2`). `cd-infra-deploy-prod.yml` run 28594775482. Gate G3 PASSED |
| W4 cutover docs | Merged (PR #77) | ADR-0012 filled, OPERATIONS.md updated, AGENTS.md tenant note updated to authoritative |
| W5 sprint retrospective | This file | Version 1.0.0 shipped in PR #77; 1.1.0 adds Slice 1+2 |
| **Slice 1 (post-sprint-close)** | Merged (PR #78 + PR #79) | Fabric F2 capacity `fabricihzhhpfsit` Active in `rg-ihzhhpf-sit`; Fabric workspace `ws-ihzhhpf-sit-data` (`f3af9733-9503-4e92-98f9-a901d96f1c87`) + lakehouse `lh_ihzhhpf_sit` (`30594c20-46ba-40ea-91fa-4701b105e0b9`) created via `configure-fabric.ps1 -SkipMirror`. UPN vs OID bug on `fabricCapacityAdmins` caught + fixed in PR #79. Added `-SkipMirror` + `-WorkspaceId`/`-LakehouseId` reuse modes. |
| **Slice 2 (post-sprint-close)** | Merged (PR #80) + reverted enable | Bicep improvements landed on `main`: `snet-data` subnet, `sourceSqlDataSubnetId` + `sourceSqlKeyVaultId` auto-wiring, SQL server `uniqueString()`, AAD-only auth block on SQL (tenant deny policy compliant), KV `enabledForTemplateDeployment=true`. SQL enable reverted (`enableSourceSqlModule=false`) because MCAPS sandbox subscription is blocked from Azure SQL Database provisioning in westus2 (+ 5 other regions). Available: centralus, francecentral, germanywestcentral, japaneast. |
| **G2.2 close-out** | Spirit-met | Synthetic CSV loaded directly into `gold.demand_encounter` in the lakehouse (bypassing SQL→mirror path per North Star architecture F-A-05 which is source-agnostic). 3 rows visible in Fabric preview — that IS `Encounter Count = 3`. Custom `sm_capacity_data_product` semantic model creation via REST hit TMDL syntax errors and was not completed; a Fabric portal-created semantic model over the default lakehouse endpoint provides equivalent visualisation. |

### Deferred / follow-up (updated)

- **Old-tenant teardown**: deferred per D6; IT owns per user direction. No action from platform team.
- **`Set-GithubEnvironmentConfig.ps1 -ExtraVars` extension**: still open. Manual patch used during W1.4 execution.
- **Enable source SQL when MCAPS restriction lifts**: Bicep is ready (`enableSourceSqlModule = true` + AAD-admin block). Flip the flag when a support ticket lifts the SQL regional restriction on subscription `66a9953a-...`. Alternatively deploy SQL cross-region in `centralus`.
- **Fix `sm_capacity_data_product` TMDL for REST-based creation**: `dataSources.tmdl` uses `structuredDataSource` which isn't a valid TMDL type; needs rewrite against actual Direct Lake TMDL grammar. Also required (already fixed in this delta): `.platform` + `definition.pbism` must be in the definition parts, both need versioned `$schema` URLs (`/1.0.0/schema.json` and `/2.0.0/schema.json` respectively), `definition.pbism.name` property is forbidden, and `.pbism` version must be `4.0`. All these hit only on live REST deploy — add integration tests in a follow-up sprint.
- **Fabric admin role assignment to operator**: `admin@mngenvmcap164444.onmicrosoft.com` is Global Admin but doesn't see the full Fabric admin portal (missing Tenant settings, Workspaces, Users, Audit logs tabs). Assign Fabric Administrator role in Microsoft 365 admin center if full admin surface is needed.

## Retrospective

### What went well

- Superpowers-first flow (brainstorm → spec → plan → execute) held up under a mid-flight scope change (region `switzerlandnorth` → `westus2`). New ADR-0013 was drafted, reviewed, and cascaded through spec/plan/runbook in one iteration.
- All 33 Pester tests stayed green throughout. Local `az bicep build` and `az deployment group what-if` caught issues before they cost anything.
- Idempotent scripts (`Grant-SubscriptionRbac`, `Set-GithubEnvironmentConfig`) let us re-run steps freely; only cost was the interactive WAM popup.
- `approved-to-apply` gate on `cd-infra-deploy-prod.yml` caught the missing `-f confirm=...` input on first attempt — workflow safety mechanism worked exactly as designed.

### What didn't

- **Global name uniqueness was under-modelled.** Base pattern `<type>-<shortname>-<envSuffix>` was insufficient for globally-unique namespaces (Storage, KV, Web App, Event Hub, Service Bus, Cognitive Services). Discovered only at deploy time; two hotfix PRs (#75, #76) needed. Should have been caught in spec review.
- **PowerShell string-interpolation bug in `New-OidcFederation.ps1`.** `"$var:literal"` is a scope-specifier expression, not string interpolation. Silently produced malformed federated credential subjects. Pester test only checked source-literal form, not runtime output — test-quality gap.
- **Runbook W1.4 enumerated too few vars.** Sprint 08 had already set 4-6 additional Fabric-scoped vars per env; the tenant-migration runbook didn't account for them. Manual patch needed mid-flight.
- **Az.Accounts module not pre-installed** on the operator workstation. Runbook prereq check should be stricter (fail closed, install-guided message).
- **Prerequisite RG creation** was implicit in the runbook Prerequisites section; not a checkbox step. Missed at execution time and caused first what-if attempt to fail.

### What to change next time

1. In the design phase, add a checklist of Azure globally-unique resource types + verify each uses `uniqueString()` (or equivalent) before deploy.
2. Extend Pester tests for any PS script that produces a runtime string derived from parameters — assert the FINAL string, not the source pattern.
3. Make runbook Prerequisites section a **checkbox list**, not a prose paragraph. Include RG creation.
4. `Set-GithubEnvironmentConfig.ps1`: accept a `-ExtraVars @{ ... }` hashtable and a `-ExtraSecrets` bundle so per-environment specifics travel through one call.
5. `Enable-DeveloperTenantTrust.ps1`: prereq check should install missing modules on `-InstallMissing` opt-in (not just warn).
6. Follow-up sprint to enable Fabric + source SQL and close G2.2. Same runbook shape, additional W1.5 Fabric-connection setup step.

## References

- Runbook: [docs/runbooks/tenant-migration-runbook.md](../runbooks/tenant-migration-runbook.md)
- ADR-0012 (tenant migration): [docs/adr/0012-tenant-migration-to-mcap164444.md](../adr/0012-tenant-migration-to-mcap164444.md)
- ADR-0013 (region carve-out): [docs/adr/0013-temporary-us-region-demo-scope.md](../adr/0013-temporary-us-region-demo-scope.md)
- Spec: [docs/superpowers/specs/2026-07-02-tenant-migration-design.md](../superpowers/specs/2026-07-02-tenant-migration-design.md)
- Plan: [docs/superpowers/plans/2026-07-02-tenant-migration-plan.md](../superpowers/plans/2026-07-02-tenant-migration-plan.md)
