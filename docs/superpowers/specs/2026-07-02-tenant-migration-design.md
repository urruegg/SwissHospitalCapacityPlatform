# Tenant Migration Design — MCAP228255 → MCAP164444

| Field | Value |
| ----- | ----- |
| **Version** | 1.2.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüeegg |
| **Status** | Draft — awaiting user review |
| **Previous Version** | 1.1.0 (added D9 westus2 demo-scope carve-out per ADR-0013 and known subscription 66a9953a-df37-4c51-856c-9971b9bf3e03 shared by SIT + PROD) |

---

## Table of Contents

1. [Context and Goal](#1-context-and-goal)
2. [Decisions](#2-decisions)
3. [Architecture](#3-architecture)
4. [Workstreams](#4-workstreams)
5. [Sequencing](#5-sequencing)
6. [Rollback](#6-rollback)
7. [Validation Gates](#7-validation-gates)
8. [File Plan](#8-file-plan)
9. [Risks and Open Questions](#9-risks-and-open-questions)
10. [References](#10-references)

---

## 1. Context and Goal

The Swiss Hospital Capacity Platform currently deploys SIT and PROD environments into an MCAP sandbox Entra tenant (`2dfb4d85-3ca7-474e-86eb-9ba3762d9474` — `MngEnvMCAP228255.onmicrosoft.com`). A new MCAP sandbox tenant (`1337187a-4c41-4da9-8fca-731bba7a4329` — `MngEnvMCAP164444.onmicrosoft.com`) has been assigned to the solution.

**Goal.** Rebuild both environments in the new tenant end-to-end, without disturbing the existing tenant, using a Markdown-first runbook and small idempotent helper scripts. Preserve the repo's Superpowers-first execution model (per [.github/copilot-instructions.md](../../../.github/copilot-instructions.md) §1 and [AGENTS.md](../../../AGENTS.md) §Superpowers Skill Enforcement) and the `approved-to-apply` gate for every real Azure change ([AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete)).

**Non-goals.**
- Migrating live data (there is none — SIT/PROD hold synthetic data only per [ADR-0003](../../adr/0003-swiss-regional-inference-for-phi.md)).
- Decommissioning the old tenant during this sprint (deferred per Q6 below).
- Introducing new orchestration tooling (no `azd`, no Terraform).

**Assumptions (validated).**
- Both tenants are MCAP sandboxes; cross-tenant subscription transfer is not attempted.
- Operator has full Entra tenant admin + subscription Owner on the new tenant.
- Fabric F2 capacity remains the smallest SKU supporting Direct Lake + Mirroring per [docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md](2026-06-14-sprint-08-data-platform-design.md).
- Region remains `switzerlandnorth` **for any PHI or production scope**. For the new-tenant demo scope only, `westus2` is used per [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md) with synthetic-only data enforcement.

---

## 2. Decisions

| # | Decision | Rationale |
| --- | --- | --- |
| D1 | Brand-new SIT and PROD subscriptions in the new tenant; no transfer attempt. | MCAP → MCAP transfers are typically blocked; rebuild is safer and faster than a support ticket loop. |
| D2 | Regenerate Key Vault secrets in new tenant (do not export/import); regenerate SQL synthetic data via `data/synthetic/generate_planning_datasets.py`; Fabric lakehouse rehydrates automatically via the SQL mirror; leave Log Analytics / App Insights history in the old tenant for read-only retention. | No durable data of value in current environments (synthetic only). Regenerating is faster, deterministic (per `traceability.json`), and eliminates cross-tenant secret handling. |
| D3 | Rename solution short name `chhealthpf` → `ihzhhpf` in live/authoritative files only (Bicep params, module descriptions, Fabric PS1 + tests + notebooks + module READMEs, `.github/copilot-instructions.md §8`, `ci-infra-validate.yml`, `docs/SD.md`, `docs/INFRASTRUCTURE.md`). Historical sprint plans and specs stay as-is. | Prevents any accidental cross-tenant name collision; preserves audit trail of what was built when. Shorter name (`ihzhhpf` = 7 chars) also frees length budget for Azure resource-name limits. |
| D4 | Sprint file: `docs/sprints/sprint-00-new-tenantprovisioning.md`. | Uses a bootstrap `sprint-00` slot (preceding existing 01–09) — no collision with existing sprint numbering. |
| D5 | Staged cutover: SIT first, prove it green, then PROD. | Lowest-risk cadence; keeps old tenant fully operational as fallback throughout. |
| D6 | Keep old tenant running post-cutover; teardown decision deferred. | User retains rollback surface; billing exposure is acceptable in the short term. Teardown handled by a separate later decision (out of scope for this sprint). |
| D7 | Runbook-first (Approach 1). Small idempotent helper scripts under `infra/scripts/tenant-migration/`; no `azd`, no new orchestrator. | Matches repo Markdown-first model (ADR-0002); once-per-lifetime operation doesn't warrant heavy automation; human-in-the-loop is a feature. |
| D8 | Establish machine trust on the operator's workstation via the Windows Account Manager (WAM) broker so `az`, `Az PowerShell`, VS Code Azure Account / Azure Resources extensions, and Bicep tooling reuse a TPM-bound device key for silent sign-in to the new tenant. Optional Workplace Join for Conditional Access "device compliant" claims. | Removes repeated MFA / device-code prompts, gives the operator the same VS Code SSO experience they have on the existing tenant, and produces a persistent audit-friendly login trail. |
| D9 | Deploy the new-tenant SIT + PROD environments in `westus2` (both hosted by the single subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`) as a time-limited demonstration and proof-of-technology scope. Synthetic sample data only; no PHI. Sunset when required services reach GA in `switzerlandnorth` or exception `EX-2026-07-02-westus2-demo` in `policy/exceptions.json` expires (2026-09-30) — whichever comes first. | Unblocks validation of North Star services (Fabric IQ Ontology and adjacent paths) not yet GA in `switzerlandnorth`. Formal carve-out via [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md) supersedes ADR-0003 and ADR-0004 for this scope only; both ADRs remain authoritative for all PHI and future production scope. |

---

## 3. Architecture

**Single source of truth:** `docs/runbooks/tenant-migration-runbook.md` — a numbered, checkbox-driven Markdown runbook. Every `az`, `gh`, and `Invoke-Fabric*` command is printed inline. Operator ticks each checkbox as they proceed.

**Automation surface:** four PowerShell 7+ scripts under `infra/scripts/tenant-migration/`, each with `-WhatIf` support and safe re-run behavior. Written to be idempotent so an operator can re-run without state corruption.

| Script | Responsibility | Idempotency strategy |
| --- | --- | --- |
| `Enable-DeveloperTenantTrust.ps1` | Enables the WAM broker for Azure CLI (`az config set core.enable_broker_on_windows=true`) and the Az PowerShell module, runs `az login --tenant <new>` + `Connect-AzAccount -Tenant <new>` via the broker so subsequent tooling reuses the TPM-bound device key, validates the VS Code Azure Account / Azure Resources extension can list new-tenant subscriptions, and prints the recommended Workplace Join steps (Settings → Accounts → Access work or school → Connect). No RBAC or resource changes. | All commands are idempotent; the broker toggle is a no-op if already set; interactive sign-in reuses the cached token if valid. Script exits early with a green summary when the workstation is already trusted. |
| `New-OidcFederation.ps1` | Creates the Entra app registration in the new tenant; adds federated credentials for `sit` and `prod` (subject `repo:urruegg/SwissHospitalCapacityPlatform:environment:<env>`, audience `https://management.azure.com`); outputs the resulting client ID. | Detects existing app by `displayName`; skips fed-cred creation if a matching subject exists. |
| `Grant-SubscriptionRbac.ps1` | Grants the OIDC service principal `Contributor` on the target subscription (or a narrower custom role via `-RoleName`). | `New-AzRoleAssignment` is idempotent when scope + role + principal are unchanged; script pre-checks with `Get-AzRoleAssignment` to keep output clean. |
| `Set-GithubEnvironmentConfig.ps1` | Wraps `gh api` to set `vars.AZURE_TENANT_ID`, `vars.AZURE_SUBSCRIPTION_ID`, `vars.AZURE_RESOURCE_GROUP`, `vars.BICEP_PARAM_FILE`, and `secrets.AZURE_CLIENT_ID` on GitHub environments `sit` and `prod`. Supports `-Restore` mode using a JSON snapshot for rollback. | Uses PUT semantics of `gh api`; captures previous values into a snapshot file before overwriting. |

**No new tooling.** No `azd`, no Bicep for identity, no Terraform. Everything uses `az`, `gh`, `Az.Accounts` / `Az.Resources`, and `Invoke-RestMethod` — tools already implicit in the current stack.

**Gates preserved.** The `approved-to-apply` human confirmation pattern from [AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete) gates every real Azure change. The runbook's structure is `plan → what-if → wait for approval → apply → verify`.

**No cross-tenant traffic.** No workstream in W1–W3 touches the old tenant. The runbook is additive-only until W4 (documentation cutover), which is why deferring teardown (D6) is safe by default.

---

## 4. Workstreams

| # | Workstream | Deliverables | Scope guard |
| --- | --- | --- | --- |
| **W0** | Repo prep (rename + governance) | 1 PR renaming `chhealthpf` → `ihzhhpf` in the 13–15 live files identified in §8; updates `.github/copilot-instructions.md §8` naming rule; bumps `docs/SD.md`, `docs/INFRASTRUCTURE.md`, `.github/copilot-instructions.md`, and `AGENTS.md` per §9 versioning. Must merge to `main` **before** any deployment. | Historical sprint/spec docs untouched. |
| **W1** | Tenant plane (new tenant, one-time) | Runbook §1: **W1.0 Developer workstation trust** (`Enable-DeveloperTenantTrust.ps1` — WAM broker on, `az login --tenant <new>`, `Connect-AzAccount -Tenant <new>`, verify VS Code Azure Account extension sees new-tenant subscriptions, optional Workplace Join); then register `Microsoft.Fabric` + `Microsoft.KeyVault` + `Microsoft.OperationalInsights` + `Microsoft.Insights` + `Microsoft.ManagedIdentity` on new subscriptions; `New-OidcFederation.ps1` creates app reg + fed creds; `Grant-SubscriptionRbac.ps1` grants `Contributor` on SIT + PROD subs; `Set-GithubEnvironmentConfig.ps1` updates `sit` + `prod` GitHub environments; Fabric prereq — bootstrap source SQL managed identity and create the Fabric connection to source SQL. | Only touches new tenant; no changes to old tenant. W1.0 is a per-workstation prerequisite; it does not modify any Azure resource. |
| **W2** | SIT deploy + smoke test | Runbook §2: `gh workflow run ci-infra-validate.yml` against SIT → `cd-infra-deploy-sit.yml` with `approved-to-apply` → `configure-fabric.ps1` post-deploy → regenerate synthetic data (`data/synthetic/generate_planning_datasets.py`) → smoke check per Sprint 08 walking-skeleton verification. | Uses existing workflows unchanged after W0 lands. |
| **W3** | PROD deploy + smoke test | Runbook §3: same shape as W2 for PROD, gated by W2 success + explicit `approved-to-apply` on the PROD deploy PR. Fabric module remains opt-out for PROD per existing `prod.bicepparam`. | Won't fire until W2 is green. |
| **W4** | Cutover completion & documentation | Runbook §4: create `docs/adr/0012-tenant-migration-to-mcap164444.md`; update `docs/OPERATIONS.md` service-ownership section; add "old tenant frozen, teardown pending" marker in `AGENTS.md`. No teardown steps (D6). | Ends with new tenant declared authoritative. |
| **W5** | Sprint report | `docs/sprints/sprint-00-new-tenantprovisioning.md` capturing goal, workstreams W0–W4, evidence artefacts, retrospective. Written last, referencing merged PRs. | Follows existing sprint-plan format. |

---

## 5. Sequencing

```text
W0 — Repo prep PR (rename + governance)
     └─► merged to main; workflows now expect new naming; nothing deployed yet
W1 — Tenant plane (new tenant, one-time; no destructive ops in old tenant)
     ├─ 1.0 Enable-DeveloperTenantTrust.ps1 (WAM broker + az login + Az PowerShell + VS Code SSO check + optional Workplace Join)
     ├─ 1.1 Register providers on new-tenant SIT + PROD subs
     ├─ 1.2 New-OidcFederation.ps1 → app reg + fed creds for sit + prod
     ├─ 1.3 Grant-SubscriptionRbac.ps1 → Contributor on both subs
     ├─ 1.4 Set-GithubEnvironmentConfig.ps1 → update sit + prod env vars/secrets
     └─ 1.5 Fabric prereqs: bootstrap source SQL managed identity, create Fabric
             connection to source SQL, capture connectionId
W2 — SIT deploy + smoke test
     ├─ 2.1 gh workflow run ci-infra-validate.yml → SIT what-if clean
     ├─ 2.2 gh workflow run cd-infra-deploy-sit.yml → wait for approved-to-apply → apply
     ├─ 2.3 configure-fabric.ps1 -CapacityName fabricihzhhpfsit -ConnectionId <from 1.5>
     ├─ 2.4 Regenerate SQL synthetic (data/synthetic/generate_planning_datasets.py)
     └─ 2.5 Smoke: verify mirror, gold table, semantic model, Encounter Count > 0
W3 — PROD deploy + smoke test
     └─ Same shape as W2 (Fabric module remains opt-out per existing prod.bicepparam)
W4 — Cutover completion
     ├─ 4.1 Author ADR-0012 tenant-migration-to-mcap164444
     ├─ 4.2 Update docs/OPERATIONS.md service-ownership + AGENTS.md tenant note
     └─ 4.3 Freeze marker in old tenant docs
W5 — Sprint report
     └─ docs/sprints/sprint-00-new-tenantprovisioning.md — retrospective + evidence
```

Every W2 / W3 apply step is gated by `approved-to-apply` on the deploy PR per [AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete).

---

## 6. Rollback

| Failure point | Rollback |
| --- | --- |
| W0 rename PR breaks a downstream check | Revert the merge commit (`git revert -m 1 <sha>`); historical docs and CI still valid because they weren't renamed. |
| W1 OIDC / RBAC misconfigured | Re-run scripts (they are idempotent); or `az ad app delete --id <client-id>` and start over. Old tenant unaffected. |
| W2 SIT what-if diff unexpected | Do not apply. Investigate diff; fix Bicep or `sit.bicepparam`; re-run what-if. |
| W2 SIT apply partial-fail | `az deployment group list -g rg-ihzhhpf-sit` to inspect; `az group delete -n rg-ihzhhpf-sit --yes` (no PHI, no durable data) and re-run W2 from 2.1. **Delete requires explicit user confirmation** per user memory. |
| W2 Fabric post-deploy fails | Re-run `configure-fabric.ps1` (already idempotent per existing tests). |
| W3 PROD deploy fails post-apply | Do NOT touch old tenant. Roll forward: fix, re-what-if, re-apply. Old tenant remains fully operational as fallback per D6. |
| W4 doc misfire | `git revert` — no cloud resources touched in W4. |
| GitHub env vars corrupted | `Set-GithubEnvironmentConfig.ps1 -Restore -SnapshotFile <path>` restores from snapshot captured at W1.4. |

**Nuclear rollback:** delete both RGs in new tenant (explicit user confirmation required), revert W0 PR, run `Set-GithubEnvironmentConfig.ps1 -Restore`. Old tenant continues serving unchanged.

---

## 7. Validation Gates

| Gate | Command | Pass criteria |
| --- | --- | --- |
| G0 | `markdownlint-cli2` + `markdown-link-check` on W0 PR | Zero errors |
| G0.1 | `az bicep build --file infra/main.bicep` | Zero errors after rename |
| G0.2 | Pester on `infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1` | All tests pass with renamed lakehouse / workspace / mirror names |
| G0.3 | `Enable-DeveloperTenantTrust.ps1` post-run: `az account show --query tenantId -o tsv` returns `1337187a-4c41-4da9-8fca-731bba7a4329`; `Get-AzContext` returns the same tenant; VS Code Azure Resources extension lists new-tenant subscriptions | Workstation is trusted to the new tenant; no device-code prompt on subsequent `az`/`Az` calls within the token lifetime |
| G1 | `az ad app show --id <new-client-id>` + `az role assignment list --assignee <sp>` | App reg exists in new tenant with 2 federated credentials; service principal has `Contributor` on both SIT and PROD subscriptions |
| G1.1 | `gh api /repos/urruegg/SwissHospitalCapacityPlatform/environments/sit/variables` | Returns new tenant + subscription IDs |
| G2 | `ci-infra-validate.yml` (SIT job) | What-if returns green diff (creates only, no unexpected deletes) |
| G2.1 | `cd-infra-deploy-sit.yml` completes | Deployment `provisioningState = Succeeded` |
| G2.2 | Sprint 08 walking-skeleton smoke (see [docs/superpowers/plans/2026-06-14-sprint-08-week-1-walking-skeleton.md](../plans/2026-06-14-sprint-08-week-1-walking-skeleton.md) §Verification) | `Encounter Count > 0` in `sm_capacity_data_product` |
| G3 | Repeat G2 series for PROD | Same |
| G4 | ADR-0012 exists; `docs/OPERATIONS.md` and `AGENTS.md` version bumped | Pass repo's [copilot-instructions.md §9](../../../.github/copilot-instructions.md) doc versioning rule |

**Definition of Done for the sprint:** all gates G0–G4 green + `docs/sprints/sprint-00-new-tenantprovisioning.md` merged.

---

## 8. File Plan

### 8.1 New files

- `docs/runbooks/tenant-migration-runbook.md`
- `infra/scripts/tenant-migration/Enable-DeveloperTenantTrust.ps1`
- `infra/scripts/tenant-migration/New-OidcFederation.ps1`
- `infra/scripts/tenant-migration/Grant-SubscriptionRbac.ps1`
- `infra/scripts/tenant-migration/Set-GithubEnvironmentConfig.ps1`
- `infra/scripts/tenant-migration/README.md`
- `docs/adr/0012-tenant-migration-to-mcap164444.md`
- `docs/sprints/sprint-00-new-tenantprovisioning.md`
- `docs/superpowers/specs/2026-07-02-tenant-migration-design.md` (this spec)

### 8.2 Modified files (W0 PR — rename `chhealthpf` → `ihzhhpf`)

Live / authoritative — MUST rename:

- `infra/main.bicep`, `infra/main.json`
- `infra/environments/sit.bicepparam`, `sit.json`
- `infra/environments/prod.bicepparam`, `prod.json`
- `infra/modules/*/main.bicep` — description strings only (12 modules — see inventory)
- `infra/modules/data-platform/fabric/post-deploy/configure-fabric.ps1`
- `infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1`
- `infra/modules/data-platform/fabric/notebooks/nb_gold_publish.py`
- `infra/modules/data-platform/fabric/notebooks/nb_silver_transform.py`
- `infra/modules/data-platform/fabric/README.md`
- `infra/modules/data-platform/fabric/semantic-model/README.md`
- `infra/modules/data-platform/source-sql/README.md`
- `.github/copilot-instructions.md` (§8 Naming Conventions — bump SemVer per §9)
- `.github/workflows/ci-infra-validate.yml` (parity-check hardcoded RG names)
- `docs/SD.md` (bump SemVer)
- `docs/INFRASTRUCTURE.md` (bump SemVer)
- `AGENTS.md` (bump SemVer — tenant note added in W4)

### 8.3 Untouched (historical — preserve audit trail)

- `docs/sprints/sprint-01..09.md`
- `docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md`
- `docs/superpowers/plans/2026-06-14-sprint-08-week-1-walking-skeleton.md`
- All files under `agents-archive/`
- All prior review reports under `docs/reviews/`

---

## 9. Risks and Open Questions

| # | Risk | Severity | Mitigation |
| --- | --- | --- | --- |
| R-01 | Rename regex is too greedy and modifies historical docs | M | The W0 PR lists exact files (§8.2). Reviewer diff-checks. If any file outside the list changed, PR is rejected. |
| R-02 | Fabric F2 capacity in new-tenant `westus2` is out of quota | M | W1.1 validates capacity availability with `az fabric capacity list-skus --location westus2` before deploy. |
| R-03 | OIDC federated credentials misconfigured (wrong subject) causes CI failures at G2 | L | `New-OidcFederation.ps1` prints the exact subject strings it wrote; runbook step G1.1 verifies. |
| R-04 | Source SQL managed identity not enabled or Fabric connection not created before W2.3 | M | W1.5 is explicit; W2.3 fails fast with clear error if `-ConnectionId` is empty. |
| R-05 | Fabric IQ Ontology preview status may change during sprint | L | Out of scope per [ADR-0002](../../adr/0002-defer-fabric-iq-ontology-from-mvp.md); no impact on this migration. |
| R-06 | Old-tenant Fabric F2 capacity continues billing while deferred | L | Explicitly accepted per D6. Cost impact documented in ADR-0012 for future teardown decision. |
| R-07 | GitHub env var updates leak sensitive values into shell history | M | `Set-GithubEnvironmentConfig.ps1` reads secrets via `-AsSecureString` and never echoes them to console. |
| R-08 | Windows workstation lacks TPM or WAM broker prerequisites (older Windows build, group policy blocking broker) | L | `Enable-DeveloperTenantTrust.ps1` detects and reports missing prerequisites; falls back to `az login --use-device-code` with a warning; does not proceed silently. |

**Open questions (defer to plan phase):**
- Should `Migrate-KeyVaultSecrets.ps1` be added as a placeholder for the eventual data-migration story (currently N/A per D2)?
- Do we want per-environment sub-runbooks or one runbook with `-Environment sit|prod` sections? (Leaning toward single runbook with per-env sections.)

---

## 10. References

- [.github/copilot-instructions.md](../../../.github/copilot-instructions.md) — repo baseline (§1 Superpowers, §8 Naming, §9 Versioning)
- [AGENTS.md](../../../AGENTS.md) — agent registry (§4 Confirmation Rule for Deploy / Delete)
- [docs/adr/0002-defer-fabric-iq-ontology-from-mvp.md](../../adr/0002-defer-fabric-iq-ontology-from-mvp.md)
- [docs/adr/0003-swiss-regional-inference-for-phi.md](../../adr/0003-swiss-regional-inference-for-phi.md)
- [docs/adr/0009-reliability-and-dr-baseline-for-sit-prod.md](../../adr/0009-reliability-and-dr-baseline-for-sit-prod.md)
- [docs/adr/0010-policy-as-code-and-release-evidence-gates.md](../../adr/0010-policy-as-code-and-release-evidence-gates.md)
- [docs/SD.md](../../SD.md)
- [docs/INFRASTRUCTURE.md](../../INFRASTRUCTURE.md)
- [docs/SECURITY.md](../../SECURITY.md)
- [docs/sprints/sprint-03-iac-provision-sit-prod.md](../../sprints/sprint-03-iac-provision-sit-prod.md) — OIDC federation baseline
- [docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md](2026-06-14-sprint-08-data-platform-design.md) — Fabric capacity / lakehouse / mirror design
- [docs/superpowers/plans/2026-06-14-sprint-08-week-1-walking-skeleton.md](../plans/2026-06-14-sprint-08-week-1-walking-skeleton.md) — Smoke test reference
- [infra/modules/data-platform/fabric/README.md](../../../infra/modules/data-platform/fabric/README.md) — Fabric pre-requisites
- [infra/modules/data-platform/fabric/post-deploy/configure-fabric.ps1](../../../infra/modules/data-platform/fabric/post-deploy/configure-fabric.ps1) — Fabric post-deploy script

---

*End of spec. Next step per [Superpowers brainstorming skill](file:///c%3A/Users/urruegg/.copilot/installed-plugins/superpowers-marketplace/superpowers/skills/brainstorming/SKILL.md): user reviews this spec; on approval, invoke `writing-plans` skill to produce the implementation plan.*
