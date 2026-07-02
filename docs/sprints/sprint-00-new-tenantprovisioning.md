# Sprint 00 — New Tenant Provisioning

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 0.1.0 (scaffold) |

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
| W4 cutover docs | This PR | ADR-0012 filled, OPERATIONS.md updated, AGENTS.md tenant note updated to authoritative |
| W5 sprint retrospective | This PR | This file |

### Deferred / follow-up

- **Gate G2.2 walking-skeleton smoke test** (`Encounter Count > 0` in `sm_capacity_data_product`): requires `enableSourceSqlModule = true` and `enableFabricFoundationModule = true` in `sit.bicepparam` + W1.5 Fabric connection setup. Not attempted this sprint; tracked as follow-up.
- **Old-tenant teardown**: deferred per D6; no action taken in Sprint 00.
- **`Set-GithubEnvironmentConfig.ps1` extension**: the plan enumerated 4 vars + 1 secret per env but each env had 6 additional pre-existing Fabric-scoped vars/secret that were set manually mid-execution. Script should be extended to accept a Fabric-vars bundle.

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
