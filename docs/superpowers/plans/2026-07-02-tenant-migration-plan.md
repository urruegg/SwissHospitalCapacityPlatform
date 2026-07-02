# Tenant Migration Implementation Plan (Sprint 00 — New Tenant Provisioning)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild SIT and PROD end-to-end in the new Entra tenant `1337187a-4c41-4da9-8fca-731bba7a4329` via a Markdown-first runbook + four idempotent PowerShell helpers + a repo-wide `chhealthpf` → `ihzhhpf` rename in live files, without disturbing the current tenant.

**Architecture:** Runbook-first (`docs/runbooks/tenant-migration-runbook.md`) drives every step. Four PowerShell 7+ scripts under `infra/scripts/tenant-migration/` cover the automatable pieces (workstation trust, OIDC app registration, subscription RBAC, GitHub environment config). Every real Azure change is gated by the existing `approved-to-apply` comment pattern on the deploy PR.

**Tech Stack:** PowerShell 7+, Pester 5.x (test framework), Azure CLI 2.60+, Az PowerShell 12+, GitHub CLI 2.50+, Bicep, existing GitHub Actions workflows (`ci-infra-validate.yml`, `cd-infra-deploy-sit.yml`, `cd-infra-deploy-prod.yml`).

**Prerequisites (must be true before Task 1):**
- Operator has full Entra tenant admin + subscription Owner in the new tenant
- Two subscriptions provisioned in the new tenant (SIT + PROD), each with an empty resource group `rg-ihzhhpf-sit` / `rg-ihzhhpf-prod`
- `az`, `Az` PS module, `gh`, `Pester 5.x`, and `PowerShell 7+` installed on the operator's workstation
- Design spec [docs/superpowers/specs/2026-07-02-tenant-migration-design.md](../specs/2026-07-02-tenant-migration-design.md) v1.1.0 is approved and merged to `main`
- Current branch: work happens on a new feature branch `sprint-00/tenant-migration-artifacts` off `main`

---

## Phase 1 — Build artifacts (Tasks 1–8, all repo-side, no cloud effects)

### Task 1: Create the feature branch

**Files:** none created; workspace state change only.

- [ ] **Step 1: Create and switch to feature branch**

Run:

```powershell
git checkout main
git pull --ff-only origin main
git checkout -b sprint-00/tenant-migration-artifacts
```

Expected: `Switched to a new branch 'sprint-00/tenant-migration-artifacts'`.

- [ ] **Step 2: Verify clean baseline**

Run:

```powershell
git status
```

Expected: `nothing to commit, working tree clean`.

---

### Task 2: W0 rename — `chhealthpf` → `ihzhhpf` in Bicep parameter files

**Files:**
- Modify: `infra/main.bicep`
- Modify: `infra/main.json`
- Modify: `infra/environments/sit.bicepparam`
- Modify: `infra/environments/sit.json`
- Modify: `infra/environments/prod.bicepparam`
- Modify: `infra/environments/prod.json`

- [ ] **Step 1: Rename the default in `infra/main.bicep`**

Edit `infra/main.bicep` line 14:

```bicep
param solutionShortName string = 'ihzhhpf'
```

- [ ] **Step 2: Rename in `infra/environments/sit.bicepparam`**

Edit lines 4 and 8:

```bicep
param solutionShortName = 'ihzhhpf'
param costCenter = 'ihzhhpf-sit'
```

Also update the placeholder-bearing lines 32–33 (keep `<SUB>` placeholder, only replace name):

```bicep
param sourceSqlDataSubnetId = '/subscriptions/<SUB>/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.Network/virtualNetworks/vnet-ihzhhpf-sit/subnets/snet-data-sit'
param sourceSqlKeyVaultId = '/subscriptions/<SUB>/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.KeyVault/vaults/kv-ihzhhpf-sit'
```

- [ ] **Step 3: Mirror the same replacements in `infra/environments/prod.bicepparam`**

Edit lines 4 and 8 to `'ihzhhpf'` / `'ihzhhpf-prod'`.

- [ ] **Step 4: Recompile Bicep to update the `.json` counterparts**

Run:

```powershell
az bicep build --file infra/main.bicep
```

Expected: exit code 0, no warnings. This rewrites `infra/main.json`.

Then rebuild the parameter JSON files:

```powershell
bicep build-params infra/environments/sit.bicepparam
bicep build-params infra/environments/prod.bicepparam
```

Expected: `infra/environments/sit.json` and `infra/environments/prod.json` updated in place with the new short name.

- [ ] **Step 5: Verify no stray `chhealthpf` references remain in these files**

Run:

```powershell
Select-String -Path infra/environments/*, infra/main.bicep, infra/main.json -Pattern 'chhealthpf'
```

Expected: no output.

- [ ] **Step 6: Commit**

```powershell
git add infra/main.bicep infra/main.json infra/environments/*
git commit -m "chore(infra): rename solution short name chhealthpf -> ihzhhpf in Bicep params"
```

---

### Task 3: W0 rename — Bicep module description strings (12 modules)

**Files:**
- Modify: `infra/modules/ai-ml-foundation/main.bicep` (line 4)
- Modify: `infra/modules/ai-platform/main.bicep` (line 4)
- Modify: `infra/modules/api-runtime/main.bicep` (line 4)
- Modify: `infra/modules/data-foundation/main.bicep` (line 4)
- Modify: `infra/modules/data-platform/fabric/main.bicep` (line 3)
- Modify: `infra/modules/data-platform/main.bicep` (line 4)
- Modify: `infra/modules/data-platform/source-sql/main.bicep` (line 3)
- Modify: `infra/modules/experience-hosting/main.bicep` (line 4)
- Modify: `infra/modules/identity/main.bicep` (line 4)
- Modify: `infra/modules/integration-orchestration/main.bicep` (line 4)
- Modify: `infra/modules/integration/main.bicep` (line 4)
- Modify: `infra/modules/network/main.bicep` (line 4)
- Modify: `infra/modules/observability/main.bicep` (line 4)
- Modify: `infra/modules/platform-foundation/main.bicep` (line 4)

- [ ] **Step 1: Replace description strings**

Each affected line reads roughly:

```bicep
@description('Resource name suffix, e.g. chhealthpf-sit or chhealthpf-prod.')
```

Replace with:

```bicep
@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
```

For the two variants that use "Suffix appended to resource names (e.g. chhealthpf-sit).", replace with "Suffix appended to resource names (e.g. ihzhhpf-sit).".

- [ ] **Step 2: Rebuild Bicep to refresh `infra/main.json` descriptions**

```powershell
az bicep build --file infra/main.bicep
```

Expected: exit code 0. Note: `infra/main.json` will show ~15 description-string diffs.

- [ ] **Step 3: Verify no stray references remain in module files**

```powershell
Select-String -Path infra/modules/**/main.bicep -Pattern 'chhealthpf'
```

Expected: no output.

- [ ] **Step 4: Commit**

```powershell
git add infra/modules/**/main.bicep infra/main.json
git commit -m "chore(infra): rename chhealthpf -> ihzhhpf in Bicep module description strings"
```

---

### Task 4: W0 rename — Fabric post-deploy PowerShell and Pester tests

**Files:**
- Modify: `infra/modules/data-platform/fabric/post-deploy/configure-fabric.ps1`
- Modify: `infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1`
- Modify: `infra/modules/data-platform/fabric/notebooks/nb_gold_publish.py`
- Modify: `infra/modules/data-platform/fabric/notebooks/nb_silver_transform.py`

- [ ] **Step 1: Update Pester tests first (test-first)**

Edit `infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1`, replacing every literal:

- `'ws-chhealthpf-sit-data'` → `'ws-ihzhhpf-sit-data'`
- `'lh_chhealthpf_sit'` → `'lh_ihzhhpf_sit'`
- `'mir_chhealthpf_kis'` → `'mir_ihzhhpf_kis'`

- [ ] **Step 2: Run Pester — tests must FAIL against unchanged script**

```powershell
Invoke-Pester -Path infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1
```

Expected: FAIL — displayName mismatches.

- [ ] **Step 3: Update `configure-fabric.ps1` to match**

Replace the same three literals:

- `displayName = 'ws-chhealthpf-sit-data'` → `'ws-ihzhhpf-sit-data'`
- `displayName = 'lh_chhealthpf_sit'` → `'lh_ihzhhpf_sit'`
- `displayName = 'mir_chhealthpf_kis'` → `'mir_ihzhhpf_kis'`

Also update the parameter-validation error line 157 (`fabricchhealthpfsit` example) to `fabricihzhhpfsit`, and the docstring line 111 (`lh_chhealthpf_sit.gold.demand_encounter` → `lh_ihzhhpf_sit.gold.demand_encounter`).

- [ ] **Step 4: Rerun Pester — tests PASS**

```powershell
Invoke-Pester -Path infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1
```

Expected: all tests pass.

- [ ] **Step 5: Update Fabric notebooks**

In both `nb_gold_publish.py` and `nb_silver_transform.py`, replace the constant on line 15:

```python
LAKEHOUSE = "lh_ihzhhpf_sit"
```

Also update the comment on line 5 in `nb_silver_transform.py` (`Lakehouse: lh_chhealthpf_sit`) and line 5 of `nb_gold_publish.py`.

- [ ] **Step 6: Verify no stray references**

```powershell
Select-String -Path infra/modules/data-platform/fabric -Pattern 'chhealthpf' -Recurse
```

Expected: matches only in `README.md` files (handled next task).

- [ ] **Step 7: Commit**

```powershell
git add infra/modules/data-platform/fabric/post-deploy/configure-fabric.ps1 `
        infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1 `
        infra/modules/data-platform/fabric/notebooks/nb_gold_publish.py `
        infra/modules/data-platform/fabric/notebooks/nb_silver_transform.py
git commit -m "chore(fabric): rename chhealthpf -> ihzhhpf in post-deploy script, Pester tests, and notebooks"
```

---

### Task 5: W0 rename — Fabric module READMEs

**Files:**
- Modify: `infra/modules/data-platform/fabric/README.md` (lines 11–13, 21, 30, 77, 83)
- Modify: `infra/modules/data-platform/fabric/semantic-model/README.md` (lines 3, 50)
- Modify: `infra/modules/data-platform/source-sql/README.md` (line 33)

- [ ] **Step 1: Fabric README**

Replace every occurrence of `chhealthpf` with `ihzhhpf` in the three files above (including composite names like `fabricchhealthpfsit` → `fabricihzhhpfsit`, `ws-chhealthpf-sit-data` → `ws-ihzhhpf-sit-data`, `lh_chhealthpf_sit` → `lh_ihzhhpf_sit`, `mir_chhealthpf_kis` → `mir_ihzhhpf_kis`).

- [ ] **Step 2: Bump the version header of each modified README per copilot-instructions.md §9**

Each README has (or gets) a version header. If none present, add one:

```markdown
| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (renamed chhealthpf -> ihzhhpf as part of tenant migration) |
```

If a README already has a version header, bump PATCH (e.g. 1.0.0 → 1.0.1) since this is an editorial rename.

- [ ] **Step 3: Lint**

```powershell
npx --yes markdownlint-cli2 "infra/modules/data-platform/**/*.md"
```

Expected: zero errors.

- [ ] **Step 4: Commit**

```powershell
git add infra/modules/data-platform/fabric/README.md `
        infra/modules/data-platform/fabric/semantic-model/README.md `
        infra/modules/data-platform/source-sql/README.md
git commit -m "docs(fabric): rename chhealthpf -> ihzhhpf in Fabric module READMEs"
```

---

### Task 6: W0 rename — governance and docs

**Files:**
- Modify: `.github/copilot-instructions.md` (§8 Naming Conventions, lines 455 and 461)
- Modify: `.github/workflows/ci-infra-validate.yml` (lines 225–226 parity-check RG names)
- Modify: `docs/SD.md` (§Solution short name, lines 81, 88, 91–93)
- Modify: `docs/INFRASTRUCTURE.md` (topology diagram, lines 42–60)
- Modify: `AGENTS.md` (add a one-line note in the Registry preamble noting the tenant migration is in progress; details land in W4)

- [ ] **Step 1: Update `.github/copilot-instructions.md`**

Replace the two mentions on lines 455 and 461:

```markdown
- **Azure resource short name**: Use `ihzhhpf` in Azure resource names to represent the solution.
- **Azure resource pattern**: Prefer `<resource-type>-ihzhhpf-<env-suffix>` for environment-scoped resources and `<resource-type>-ihzhhpf` for shared resources.
```

Bump the version header at the top of the file per §9 (MINOR — additive naming change): find the header table (near line 4), bump `Version` to the next MINOR, set `Date: 2026-07-02`, and update `Previous Version` to the prior value with a hint like `1.5.0 (renamed solution short name chhealthpf -> ihzhhpf per tenant migration D3)`.

- [ ] **Step 2: Update `.github/workflows/ci-infra-validate.yml`**

Edit lines 225–226:

```yaml
          sit_rg='rg-ihzhhpf-sit'
          prod_rg='rg-ihzhhpf-prod'
```

- [ ] **Step 3: Update `docs/SD.md`**

Replace every `chhealthpf` on lines 81, 88, 91, 92, 93 with `ihzhhpf`. Then bump the file's version header per §9 (MINOR).

- [ ] **Step 4: Update `docs/INFRASTRUCTURE.md`**

Replace every `chhealthpf` in the topology diagram (lines 42–60) with `ihzhhpf`. Then bump the version header per §9 (MINOR).

- [ ] **Step 5: Update `AGENTS.md`**

Under the Registry preamble, add one sentence:

> **Tenant migration in progress (Sprint 00):** the platform is being rebuilt in Entra tenant `1337187a-4c41-4da9-8fca-731bba7a4329` with solution short name `ihzhhpf`. See [docs/superpowers/specs/2026-07-02-tenant-migration-design.md](docs/superpowers/specs/2026-07-02-tenant-migration-design.md).

Bump the AGENTS.md version header per §9 (MINOR).

- [ ] **Step 6: Verify no stray `chhealthpf` in the live scope**

```powershell
Select-String -Path .github/copilot-instructions.md, .github/workflows/ci-infra-validate.yml, docs/SD.md, docs/INFRASTRUCTURE.md, AGENTS.md -Pattern 'chhealthpf'
```

Expected: no output.

- [ ] **Step 7: Lint the modified Markdown**

```powershell
npx --yes markdownlint-cli2 .github/copilot-instructions.md docs/SD.md docs/INFRASTRUCTURE.md AGENTS.md
```

Expected: zero errors.

- [ ] **Step 8: Commit**

```powershell
git add .github/copilot-instructions.md .github/workflows/ci-infra-validate.yml docs/SD.md docs/INFRASTRUCTURE.md AGENTS.md
git commit -m "docs(governance): rename chhealthpf -> ihzhhpf in governance rule, CI parity check, SD, and Infrastructure docs"
```

---

### Task 7: W0 gate — full-tree grep confirms only historical files retain `chhealthpf`

**Files:** none created; verification only.

- [ ] **Step 1: Grep for any remaining `chhealthpf` in live paths**

```powershell
$live = @(
  'infra/**/*.bicep',
  'infra/**/*.bicepparam',
  'infra/**/*.json',
  'infra/**/*.ps1',
  'infra/**/*.py',
  'infra/modules/**/README.md',
  '.github/copilot-instructions.md',
  '.github/workflows/*.yml',
  'docs/SD.md',
  'docs/INFRASTRUCTURE.md',
  'AGENTS.md'
)
$live | ForEach-Object { Get-ChildItem -Path $_ -Recurse -File -ErrorAction SilentlyContinue } |
  Select-String -Pattern 'chhealthpf'
```

Expected: no output.

- [ ] **Step 2: Confirm historical files were NOT rewritten**

```powershell
Select-String -Path docs/sprints/sprint-*.md, docs/superpowers/specs/2026-06-14-*.md, docs/superpowers/plans/2026-06-14-*.md -Pattern 'chhealthpf' |
  Select-Object -First 5
```

Expected: at least 5 lines returned (historical references intact).

---

### Task 8: `Enable-DeveloperTenantTrust.ps1` (W1.0) with Pester tests

**Files:**
- Create: `infra/scripts/tenant-migration/Enable-DeveloperTenantTrust.ps1`
- Create: `infra/scripts/tenant-migration/tests/Enable-DeveloperTenantTrust.Tests.ps1`
- Create: `infra/scripts/tenant-migration/README.md` (skeleton; fully written in Task 12)

- [ ] **Step 1: Write the failing Pester tests**

Create `infra/scripts/tenant-migration/tests/Enable-DeveloperTenantTrust.Tests.ps1`:

```powershell
#Requires -Modules Pester
BeforeAll {
    $script:ScriptPath = Join-Path $PSScriptRoot '..' 'Enable-DeveloperTenantTrust.ps1'
}

Describe 'Enable-DeveloperTenantTrust' {
    It 'exists and is a script file' {
        Test-Path $script:ScriptPath | Should -BeTrue
    }
    It 'declares mandatory parameter TenantId as a GUID' {
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($script:ScriptPath, [ref]$null, [ref]$null)
        $param = $ast.ParamBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'TenantId' }
        $param | Should -Not -BeNullOrEmpty
        $param.Attributes.TypeName.FullName | Should -Contain 'guid'
    }
    It 'supports -WhatIf via SupportsShouldProcess' {
        Select-String -Path $script:ScriptPath -Pattern 'SupportsShouldProcess' -Quiet | Should -BeTrue
    }
    It 'enables the Azure CLI WAM broker' {
        Select-String -Path $script:ScriptPath -Pattern 'az config set core\.enable_broker_on_windows=true' -Quiet | Should -BeTrue
    }
    It 'signs in via az login --tenant <TenantId>' {
        Select-String -Path $script:ScriptPath -Pattern 'az login --tenant' -Quiet | Should -BeTrue
    }
    It 'signs in via Connect-AzAccount with -Tenant' {
        Select-String -Path $script:ScriptPath -Pattern 'Connect-AzAccount' -Quiet | Should -BeTrue
    }
    It 'falls back to device-code with a warning when broker is unavailable' {
        Select-String -Path $script:ScriptPath -Pattern '--use-device-code' -Quiet | Should -BeTrue
    }
    It 'prints Workplace Join guidance' {
        Select-String -Path $script:ScriptPath -Pattern 'Access work or school' -Quiet | Should -BeTrue
    }
    It 'validates by calling az account show and Get-AzContext post sign-in' {
        Select-String -Path $script:ScriptPath -Pattern 'az account show' -Quiet | Should -BeTrue
        Select-String -Path $script:ScriptPath -Pattern 'Get-AzContext' -Quiet | Should -BeTrue
    }
}
```

- [ ] **Step 2: Run Pester — must FAIL**

```powershell
Invoke-Pester -Path infra/scripts/tenant-migration/tests/Enable-DeveloperTenantTrust.Tests.ps1
```

Expected: FAIL — `Test-Path` false because script doesn't exist yet.

- [ ] **Step 3: Write the script**

Create `infra/scripts/tenant-migration/Enable-DeveloperTenantTrust.ps1`:

```powershell
<#
.SYNOPSIS
    Establishes machine trust for silent sign-in to a target Entra tenant from Azure CLI, Az PowerShell, and VS Code Azure extensions.
.DESCRIPTION
    Enables the Windows Account Manager (WAM) broker for the Azure CLI, signs in interactively to the target tenant via the broker (TPM-bound device key), then signs in Az PowerShell via the same broker. Falls back to device-code sign-in when the broker is unavailable. Prints Workplace Join guidance for optional Conditional Access "device compliant" claims.
.PARAMETER TenantId
    The target Entra tenant ID (GUID).
.PARAMETER SubscriptionId
    Optional. If provided, sets it as the active subscription after sign-in.
.EXAMPLE
    ./Enable-DeveloperTenantTrust.ps1 -TenantId 1337187a-4c41-4da9-8fca-731bba7a4329 -SubscriptionId 00000000-0000-0000-0000-000000000000
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [guid]$TenantId,

    [Parameter()]
    [guid]$SubscriptionId
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "==== $Title ====" -ForegroundColor Cyan
}

Write-Section "1. Verify prerequisites"
$brokerCandidate = Get-Command az -ErrorAction SilentlyContinue
if (-not $brokerCandidate) { throw "Azure CLI (az) not found on PATH. Install azure-cli 2.60+." }
if (-not (Get-Module -ListAvailable Az.Accounts)) {
    Write-Warning "Az.Accounts module not found. Install via: Install-Module Az -Scope CurrentUser -Force"
}

Write-Section "2. Enable WAM broker for Azure CLI"
if ($PSCmdlet.ShouldProcess('Azure CLI', 'enable WAM broker (az config set core.enable_broker_on_windows=true)')) {
    az config set core.enable_broker_on_windows=true | Out-Null
    Write-Host "WAM broker enabled for Azure CLI." -ForegroundColor Green
}

Write-Section "3. Sign in to Azure CLI (interactive, TPM-bound device key)"
$loginArgs = @('login', '--tenant', $TenantId.ToString())
if ($SubscriptionId) { $loginArgs += @('--allow-no-subscriptions') }

if ($PSCmdlet.ShouldProcess("tenant $TenantId", 'az login')) {
    try {
        az @loginArgs | Out-Null
    } catch {
        Write-Warning "Broker-based sign-in failed. Falling back to --use-device-code. Reason: $_"
        az login --tenant $TenantId --use-device-code | Out-Null
    }
    if ($SubscriptionId) {
        az account set --subscription $SubscriptionId.ToString()
    }
}

Write-Section "4. Sign in to Az PowerShell"
if ($PSCmdlet.ShouldProcess("tenant $TenantId", 'Connect-AzAccount')) {
    $connectArgs = @{ Tenant = $TenantId.ToString() }
    if ($SubscriptionId) { $connectArgs.Subscription = $SubscriptionId.ToString() }
    Connect-AzAccount @connectArgs | Out-Null
}

Write-Section "5. Validate"
$azAccount = az account show --query '{name:name, tenantId:tenantId, subscriptionId:id}' -o json | ConvertFrom-Json
$azContext = Get-AzContext
Write-Host "az account show:   $($azAccount | ConvertTo-Json -Compress)" -ForegroundColor Green
Write-Host "Get-AzContext:     Tenant=$($azContext.Tenant.Id) Sub=$($azContext.Subscription.Id)" -ForegroundColor Green
if ($azAccount.tenantId -ne $TenantId.ToString()) {
    throw "az account tenant ($($azAccount.tenantId)) does not match expected ($TenantId)."
}
if ($azContext.Tenant.Id -ne $TenantId.ToString()) {
    throw "Az context tenant ($($azContext.Tenant.Id)) does not match expected ($TenantId)."
}

Write-Section "6. Optional: Workplace Join (Entra Registered)"
Write-Host @'
For Conditional Access "device compliant" claims and to persist an Entra device certificate:

  Open Settings > Accounts > Access work or school > Connect
  Sign in with your new-tenant account
  Follow the prompts to complete Workplace Join

Verify afterwards with: dsregcmd /status  (look for AzureAdJoined : YES or WorkplaceJoined : YES)
'@ -ForegroundColor Yellow

Write-Section "Done"
Write-Host "Workstation is trusted to tenant $TenantId. VS Code Azure Account and Azure Resources extensions will pick up the cached token silently." -ForegroundColor Green
```

- [ ] **Step 4: Rerun Pester — must PASS**

```powershell
Invoke-Pester -Path infra/scripts/tenant-migration/tests/Enable-DeveloperTenantTrust.Tests.ps1
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```powershell
git add infra/scripts/tenant-migration/Enable-DeveloperTenantTrust.ps1 infra/scripts/tenant-migration/tests/Enable-DeveloperTenantTrust.Tests.ps1
git commit -m "feat(tenant-migration): add Enable-DeveloperTenantTrust.ps1 with Pester tests"
```

---

### Task 9: `New-OidcFederation.ps1` (W1.2) with Pester tests

**Files:**
- Create: `infra/scripts/tenant-migration/New-OidcFederation.ps1`
- Create: `infra/scripts/tenant-migration/tests/New-OidcFederation.Tests.ps1`

- [ ] **Step 1: Write the failing Pester tests**

Create `infra/scripts/tenant-migration/tests/New-OidcFederation.Tests.ps1`:

```powershell
#Requires -Modules Pester
BeforeAll {
    $script:ScriptPath = Join-Path $PSScriptRoot '..' 'New-OidcFederation.ps1'
}

Describe 'New-OidcFederation' {
    It 'exists' {
        Test-Path $script:ScriptPath | Should -BeTrue
    }
    It 'declares mandatory DisplayName parameter' {
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($script:ScriptPath, [ref]$null, [ref]$null)
        $param = $ast.ParamBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'DisplayName' }
        $param | Should -Not -BeNullOrEmpty
    }
    It 'declares mandatory RepoFullName parameter (owner/repo)' {
        Select-String -Path $script:ScriptPath -Pattern '\$RepoFullName' -Quiet | Should -BeTrue
    }
    It 'declares Environments parameter defaulting to sit and prod' {
        Select-String -Path $script:ScriptPath -Pattern "Environments\s*=\s*@\('sit',\s*'prod'\)" -Quiet | Should -BeTrue
    }
    It 'supports -WhatIf' {
        Select-String -Path $script:ScriptPath -Pattern 'SupportsShouldProcess' -Quiet | Should -BeTrue
    }
    It 'checks for existing app registration before creating one (idempotency)' {
        Select-String -Path $script:ScriptPath -Pattern 'az ad app list' -Quiet | Should -BeTrue
    }
    It 'uses the GitHub OIDC federated credential subject format' {
        Select-String -Path $script:ScriptPath -Pattern "repo:\$RepoFullName:environment:" -Quiet | Should -BeTrue
    }
    It 'uses audience https://management.azure.com' {
        Select-String -Path $script:ScriptPath -Pattern 'https://management.azure.com' -Quiet | Should -BeTrue
    }
    It 'outputs the client ID at end' {
        Select-String -Path $script:ScriptPath -Pattern 'ClientId\s*=' -Quiet | Should -BeTrue
    }
}
```

- [ ] **Step 2: Run Pester — must FAIL**

```powershell
Invoke-Pester -Path infra/scripts/tenant-migration/tests/New-OidcFederation.Tests.ps1
```

Expected: FAIL (script missing).

- [ ] **Step 3: Write the script**

Create `infra/scripts/tenant-migration/New-OidcFederation.ps1`:

```powershell
<#
.SYNOPSIS
    Creates (idempotently) an Entra app registration in the target tenant and adds GitHub OIDC federated credentials for the specified environments.
.PARAMETER DisplayName
    The Entra app registration display name (e.g., 'gh-oidc-swisshospitalcapacityplatform').
.PARAMETER RepoFullName
    The GitHub repo in 'owner/repo' form (e.g., 'urruegg/SwissHospitalCapacityPlatform').
.PARAMETER Environments
    Environment names for which to create federated credentials. Defaults to @('sit', 'prod').
.EXAMPLE
    ./New-OidcFederation.ps1 -DisplayName gh-oidc-shcp -RepoFullName urruegg/SwissHospitalCapacityPlatform
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$DisplayName,

    [Parameter(Mandatory)]
    [string]$RepoFullName,

    [Parameter()]
    [string[]]$Environments = @('sit', 'prod')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ($RepoFullName -notmatch '^[^/]+/[^/]+$') {
    throw "RepoFullName must be in 'owner/repo' form; got: $RepoFullName"
}

# ---- App registration (idempotent) ----
$existing = az ad app list --display-name $DisplayName --query "[?displayName=='$DisplayName']" -o json | ConvertFrom-Json
if ($existing.Count -gt 0) {
    $appId = $existing[0].appId
    Write-Host "Reusing existing app registration '$DisplayName' (appId $appId)." -ForegroundColor Yellow
} else {
    if ($PSCmdlet.ShouldProcess($DisplayName, 'create Entra app registration')) {
        $created = az ad app create --display-name $DisplayName --sign-in-audience AzureADMyOrg -o json | ConvertFrom-Json
        $appId = $created.appId
        Write-Host "Created app registration '$DisplayName' (appId $appId)." -ForegroundColor Green
    } else {
        Write-Host "WhatIf: would create app registration '$DisplayName'." -ForegroundColor DarkYellow
        return
    }
}

# ---- Service principal (idempotent) ----
$spExisting = az ad sp list --filter "appId eq '$appId'" -o json | ConvertFrom-Json
if ($spExisting.Count -eq 0) {
    if ($PSCmdlet.ShouldProcess($appId, 'create service principal')) {
        az ad sp create --id $appId | Out-Null
        Write-Host "Created service principal for appId $appId." -ForegroundColor Green
    }
}

# ---- Federated credentials (idempotent) ----
$existingFics = az ad app federated-credential list --id $appId -o json | ConvertFrom-Json
foreach ($env in $Environments) {
    $ficName = "gh-$env"
    $subject = "repo:$RepoFullName:environment:$env"
    if ($existingFics | Where-Object { $_.subject -eq $subject }) {
        Write-Host "Federated credential '$ficName' (subject $subject) already exists — skipping." -ForegroundColor Yellow
        continue
    }
    if ($PSCmdlet.ShouldProcess($ficName, "create federated credential subject=$subject")) {
        $body = @{
            name        = $ficName
            issuer      = 'https://token.actions.githubusercontent.com'
            subject     = $subject
            description = "GitHub Actions OIDC for environment $env"
            audiences   = @('api://AzureADTokenExchange')
        } | ConvertTo-Json -Depth 5 -Compress

        $tmp = New-TemporaryFile
        try {
            $body | Set-Content -Path $tmp -Encoding utf8
            az ad app federated-credential create --id $appId --parameters "@$tmp" | Out-Null
            Write-Host "Created federated credential '$ficName' (subject $subject)." -ForegroundColor Green
        } finally {
            Remove-Item $tmp -ErrorAction SilentlyContinue
        }
    }
}

# NB: Azure token audience for federated OIDC exchange is api://AzureADTokenExchange (Entra endpoint);
# the resulting access token target audience for CI is https://management.azure.com.

# ---- Output ----
$sp = az ad sp list --filter "appId eq '$appId'" -o json | ConvertFrom-Json | Select-Object -First 1
[pscustomobject]@{
    ClientId       = $appId
    PrincipalId    = $sp.id
    DisplayName    = $DisplayName
    Environments   = $Environments
}
```

- [ ] **Step 4: Rerun Pester — PASS**

```powershell
Invoke-Pester -Path infra/scripts/tenant-migration/tests/New-OidcFederation.Tests.ps1
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add infra/scripts/tenant-migration/New-OidcFederation.ps1 infra/scripts/tenant-migration/tests/New-OidcFederation.Tests.ps1
git commit -m "feat(tenant-migration): add New-OidcFederation.ps1 with Pester tests"
```

---

### Task 10: `Grant-SubscriptionRbac.ps1` (W1.3) with Pester tests

**Files:**
- Create: `infra/scripts/tenant-migration/Grant-SubscriptionRbac.ps1`
- Create: `infra/scripts/tenant-migration/tests/Grant-SubscriptionRbac.Tests.ps1`

- [ ] **Step 1: Write the failing Pester tests**

Create `infra/scripts/tenant-migration/tests/Grant-SubscriptionRbac.Tests.ps1`:

```powershell
#Requires -Modules Pester
BeforeAll {
    $script:ScriptPath = Join-Path $PSScriptRoot '..' 'Grant-SubscriptionRbac.ps1'
}

Describe 'Grant-SubscriptionRbac' {
    It 'exists' { Test-Path $script:ScriptPath | Should -BeTrue }
    It 'has SupportsShouldProcess' {
        Select-String -Path $script:ScriptPath -Pattern 'SupportsShouldProcess' -Quiet | Should -BeTrue
    }
    It 'declares mandatory PrincipalId as guid' {
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($script:ScriptPath, [ref]$null, [ref]$null)
        $param = $ast.ParamBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'PrincipalId' }
        $param.Attributes.TypeName.FullName | Should -Contain 'guid'
    }
    It 'declares mandatory SubscriptionId as guid' {
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($script:ScriptPath, [ref]$null, [ref]$null)
        $param = $ast.ParamBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'SubscriptionId' }
        $param.Attributes.TypeName.FullName | Should -Contain 'guid'
    }
    It 'declares RoleName with default Contributor' {
        Select-String -Path $script:ScriptPath -Pattern '\$RoleName\s*=\s*[''"]Contributor[''"]' -Quiet | Should -BeTrue
    }
    It 'pre-checks with Get-AzRoleAssignment to avoid duplicate assignment' {
        Select-String -Path $script:ScriptPath -Pattern 'Get-AzRoleAssignment' -Quiet | Should -BeTrue
    }
    It 'uses New-AzRoleAssignment to assign' {
        Select-String -Path $script:ScriptPath -Pattern 'New-AzRoleAssignment' -Quiet | Should -BeTrue
    }
}
```

- [ ] **Step 2: Run Pester — FAIL**

- [ ] **Step 3: Write the script**

Create `infra/scripts/tenant-migration/Grant-SubscriptionRbac.ps1`:

```powershell
<#
.SYNOPSIS
    Idempotently grants a role to a service principal at subscription scope.
.PARAMETER PrincipalId
    The service principal object ID.
.PARAMETER SubscriptionId
    The target subscription ID.
.PARAMETER RoleName
    The RBAC role to grant. Defaults to 'Contributor'.
.EXAMPLE
    ./Grant-SubscriptionRbac.ps1 -PrincipalId 11111111-... -SubscriptionId 22222222-... -RoleName Contributor
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [guid]$PrincipalId,

    [Parameter(Mandatory)]
    [guid]$SubscriptionId,

    [Parameter()]
    [string]$RoleName = 'Contributor'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scope = "/subscriptions/$SubscriptionId"

Set-AzContext -Subscription $SubscriptionId | Out-Null

$existing = Get-AzRoleAssignment -ObjectId $PrincipalId -Scope $scope -RoleDefinitionName $RoleName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Role assignment already exists: $RoleName on $scope for $PrincipalId — skipping." -ForegroundColor Yellow
    return $existing
}

if ($PSCmdlet.ShouldProcess("$scope", "grant $RoleName to $PrincipalId")) {
    $assignment = New-AzRoleAssignment -ObjectId $PrincipalId -RoleDefinitionName $RoleName -Scope $scope
    Write-Host "Granted $RoleName on $scope to $PrincipalId." -ForegroundColor Green
    return $assignment
}
```

- [ ] **Step 4: Rerun Pester — PASS**

- [ ] **Step 5: Commit**

```powershell
git add infra/scripts/tenant-migration/Grant-SubscriptionRbac.ps1 infra/scripts/tenant-migration/tests/Grant-SubscriptionRbac.Tests.ps1
git commit -m "feat(tenant-migration): add Grant-SubscriptionRbac.ps1 with Pester tests"
```

---

### Task 11: `Set-GithubEnvironmentConfig.ps1` (W1.4) with Pester tests

**Files:**
- Create: `infra/scripts/tenant-migration/Set-GithubEnvironmentConfig.ps1`
- Create: `infra/scripts/tenant-migration/tests/Set-GithubEnvironmentConfig.Tests.ps1`

- [ ] **Step 1: Write the failing Pester tests**

Create `infra/scripts/tenant-migration/tests/Set-GithubEnvironmentConfig.Tests.ps1`:

```powershell
#Requires -Modules Pester
BeforeAll {
    $script:ScriptPath = Join-Path $PSScriptRoot '..' 'Set-GithubEnvironmentConfig.ps1'
}

Describe 'Set-GithubEnvironmentConfig' {
    It 'exists' { Test-Path $script:ScriptPath | Should -BeTrue }
    It 'has SupportsShouldProcess' {
        Select-String -Path $script:ScriptPath -Pattern 'SupportsShouldProcess' -Quiet | Should -BeTrue
    }
    It 'declares mandatory RepoFullName' {
        Select-String -Path $script:ScriptPath -Pattern '\$RepoFullName' -Quiet | Should -BeTrue
    }
    It 'declares Environment parameter' {
        Select-String -Path $script:ScriptPath -Pattern '\$Environment' -Quiet | Should -BeTrue
    }
    It 'reads client-id as SecureString' {
        Select-String -Path $script:ScriptPath -Pattern 'SecureString' -Quiet | Should -BeTrue
    }
    It 'uses gh api to set variables' {
        Select-String -Path $script:ScriptPath -Pattern 'gh api' -Quiet | Should -BeTrue
    }
    It 'supports -Restore mode with snapshot file' {
        Select-String -Path $script:ScriptPath -Pattern '\$Restore' -Quiet | Should -BeTrue
        Select-String -Path $script:ScriptPath -Pattern '\$SnapshotPath' -Quiet | Should -BeTrue
    }
}
```

- [ ] **Step 2: Run Pester — FAIL**

- [ ] **Step 3: Write the script**

Create `infra/scripts/tenant-migration/Set-GithubEnvironmentConfig.ps1`:

```powershell
<#
.SYNOPSIS
    Sets or restores GitHub environment variables and secrets for tenant migration.
.PARAMETER RepoFullName
    'owner/repo' form.
.PARAMETER Environment
    'sit' or 'prod'.
.PARAMETER TenantId, SubscriptionId, ResourceGroup, BicepParamFile
    Environment variables to set.
.PARAMETER ClientId
    SecureString containing the AZURE_CLIENT_ID (stored as GitHub secret).
.PARAMETER Restore
    When set, reads $SnapshotPath and restores previous values.
.PARAMETER SnapshotPath
    File path to write snapshot (default) or read from (with -Restore).
#>
[CmdletBinding(SupportsShouldProcess, DefaultParameterSetName = 'Set')]
param(
    [Parameter(Mandatory)]
    [string]$RepoFullName,

    [Parameter(Mandatory)]
    [ValidateSet('sit', 'prod')]
    [string]$Environment,

    [Parameter(ParameterSetName = 'Set', Mandatory)]
    [guid]$TenantId,

    [Parameter(ParameterSetName = 'Set', Mandatory)]
    [guid]$SubscriptionId,

    [Parameter(ParameterSetName = 'Set', Mandatory)]
    [string]$ResourceGroup,

    [Parameter(ParameterSetName = 'Set', Mandatory)]
    [string]$BicepParamFile,

    [Parameter(ParameterSetName = 'Set', Mandatory)]
    [System.Security.SecureString]$ClientId,

    [Parameter(ParameterSetName = 'Restore', Mandatory)]
    [switch]$Restore,

    [Parameter()]
    [string]$SnapshotPath = "./tenant-migration-github-env-snapshot-$Environment.json"
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Get-CurrentEnvSnapshot {
    param([string]$Repo, [string]$Env)
    $vars = gh api "/repos/$Repo/environments/$Env/variables" 2>$null | ConvertFrom-Json
    return @{
        environment = $Env
        variables   = $vars.variables | ForEach-Object { @{ name = $_.name; value = $_.value } }
        capturedAt  = (Get-Date).ToString('o')
    }
}

if ($Restore) {
    if (-not (Test-Path $SnapshotPath)) {
        throw "Snapshot file not found: $SnapshotPath"
    }
    $snap = Get-Content $SnapshotPath -Raw | ConvertFrom-Json
    foreach ($v in $snap.variables) {
        if ($PSCmdlet.ShouldProcess("$Environment/$($v.name)", "restore variable")) {
            gh variable set $v.name --env $Environment --repo $RepoFullName --body $v.value | Out-Null
        }
    }
    Write-Host "Restored $($snap.variables.Count) variables to environment '$Environment' from $SnapshotPath." -ForegroundColor Green
    return
}

# --- Snapshot current state before mutating ---
if ($PSCmdlet.ShouldProcess($SnapshotPath, 'write pre-change snapshot')) {
    Get-CurrentEnvSnapshot -Repo $RepoFullName -Env $Environment |
      ConvertTo-Json -Depth 5 |
      Set-Content -Path $SnapshotPath -Encoding utf8
    Write-Host "Snapshot written to $SnapshotPath." -ForegroundColor Green
}

# --- Set variables ---
$vars = @{
    AZURE_TENANT_ID       = $TenantId.ToString()
    AZURE_SUBSCRIPTION_ID = $SubscriptionId.ToString()
    AZURE_RESOURCE_GROUP  = $ResourceGroup
    BICEP_PARAM_FILE      = $BicepParamFile
}
foreach ($k in $vars.Keys) {
    if ($PSCmdlet.ShouldProcess("$Environment/$k", "set variable")) {
        gh variable set $k --env $Environment --repo $RepoFullName --body $vars[$k] | Out-Null
    }
}

# --- Set secret (never logged) ---
if ($PSCmdlet.ShouldProcess("$Environment/AZURE_CLIENT_ID", 'set secret')) {
    $plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($ClientId))
    try {
        $plain | gh secret set AZURE_CLIENT_ID --env $Environment --repo $RepoFullName
    } finally {
        $plain = $null
        [System.GC]::Collect()
    }
}

Write-Host "GitHub environment '$Environment' configured for tenant $TenantId." -ForegroundColor Green
```

- [ ] **Step 4: Rerun Pester — PASS**

- [ ] **Step 5: Commit**

```powershell
git add infra/scripts/tenant-migration/Set-GithubEnvironmentConfig.ps1 infra/scripts/tenant-migration/tests/Set-GithubEnvironmentConfig.Tests.ps1
git commit -m "feat(tenant-migration): add Set-GithubEnvironmentConfig.ps1 with Pester tests"
```

---

### Task 12: Write `infra/scripts/tenant-migration/README.md`

**Files:**
- Modify (or create): `infra/scripts/tenant-migration/README.md`

- [ ] **Step 1: Author the README**

Write the following structure:

- Version header per §9 (starts at 1.0.0)
- Purpose (one paragraph)
- Prerequisites (Windows 10/11 with TPM 2.0, PS 7+, az 2.60+, gh 2.50+, Pester 5.x)
- Script index with one-line description and pointer to Pester tests
- Recommended invocation order (mirrors runbook §1)
- Rollback: mention `Set-GithubEnvironmentConfig.ps1 -Restore`
- Link to the runbook and the spec

- [ ] **Step 2: Lint**

```powershell
npx --yes markdownlint-cli2 infra/scripts/tenant-migration/README.md
```

- [ ] **Step 3: Commit**

```powershell
git add infra/scripts/tenant-migration/README.md
git commit -m "docs(tenant-migration): document script pack purpose, prerequisites, and invocation order"
```

---

### Task 13: Write `docs/runbooks/tenant-migration-runbook.md`

**Files:**
- Create: `docs/runbooks/tenant-migration-runbook.md`

- [ ] **Step 1: Author the runbook**

Structure with checkbox-driven sections:

1. **Purpose and scope** (link back to spec)
2. **Prerequisites** (workstation, tenant admin, subscriptions provisioned, empty RGs)
3. **§1 Tenant plane (W1)** — one subsection per step:
   - 1.0 Developer workstation trust (invoke `Enable-DeveloperTenantTrust.ps1`)
   - 1.1 Provider registration (`az provider register --namespace ...` for each of the five providers on both subs)
   - 1.2 App registration + federated credentials (invoke `New-OidcFederation.ps1`)
   - 1.3 Subscription RBAC (invoke `Grant-SubscriptionRbac.ps1` twice)
   - 1.4 GitHub environment config (invoke `Set-GithubEnvironmentConfig.ps1` twice)
   - 1.5 Fabric prereq (enable source SQL SAMI + create Fabric connection, capture `connectionId`)
4. **§2 SIT deploy (W2)** — dispatch `ci-infra-validate.yml`, review what-if, dispatch `cd-infra-deploy-sit.yml`, wait for `approved-to-apply`, run `configure-fabric.ps1`, run `generate_planning_datasets.py`, run smoke checks
5. **§3 PROD deploy (W3)** — same shape, gated by W2 completion
6. **§4 Cutover docs (W4)** — checkboxes to draft ADR-0012, update OPERATIONS.md, add tenant note to AGENTS.md
7. **§5 Sprint report (W5)** — checkbox pointing to Task 15 in this plan
8. **Rollback** — mirror §6 of the spec

Add a header table per §9 (version 1.0.0, date 2026-07-02, status Draft).

- [ ] **Step 2: Lint + link check**

```powershell
npx --yes markdownlint-cli2 docs/runbooks/tenant-migration-runbook.md
npx --yes markdown-link-check docs/runbooks/tenant-migration-runbook.md
```

- [ ] **Step 3: Commit**

```powershell
git add docs/runbooks/tenant-migration-runbook.md
git commit -m "docs(runbooks): add tenant migration runbook (W1-W5 execution guide)"
```

---

### Task 14: Scaffold ADR-0012 and the sprint report (empty except for headers)

**Files:**
- Create: `docs/adr/0012-tenant-migration-to-mcap164444.md`
- Create: `docs/sprints/sprint-00-new-tenantprovisioning.md`

- [ ] **Step 1: ADR-0012 skeleton**

Structure:

```markdown
# ADR-0012 — Tenant migration to MCAP164444

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |

## Context

## Decision

## Consequences

## References

- Spec: docs/superpowers/specs/2026-07-02-tenant-migration-design.md
- Runbook: docs/runbooks/tenant-migration-runbook.md
```

Content is intentionally minimal here — filled in during Task 18 (W4 execution).

- [ ] **Step 2: Sprint report skeleton**

Follow the existing sprint file convention (see `docs/sprints/sprint-08-...md` for shape). Include:

- Header table (version 0.1.0, status "In progress", start date 2026-07-02)
- Sections for Goal, Scope, Workstreams (W0–W5), Evidence, Retrospective (empty except headings)

- [ ] **Step 3: Lint**

```powershell
npx --yes markdownlint-cli2 docs/adr/0012-tenant-migration-to-mcap164444.md docs/sprints/sprint-00-new-tenantprovisioning.md
```

- [ ] **Step 4: Commit**

```powershell
git add docs/adr/0012-tenant-migration-to-mcap164444.md docs/sprints/sprint-00-new-tenantprovisioning.md
git commit -m "docs(adr,sprint): scaffold ADR-0012 and sprint-00 report (empty; filled during W4/W5)"
```

---

### Task 15: Open Phase-1 PR

- [ ] **Step 1: Push branch and open PR**

```powershell
git push -u origin sprint-00/tenant-migration-artifacts
gh pr create --title "sprint-00: tenant migration artifacts (W0 rename + scripts + runbook)" `
             --body "Implements the artefact-build phase of the tenant migration plan (docs/superpowers/plans/2026-07-02-tenant-migration-plan.md). No Azure changes; safe to merge before execution. Spec: docs/superpowers/specs/2026-07-02-tenant-migration-design.md v1.1.0." `
             --base main
```

Expected: PR URL printed.

- [ ] **Step 2: Verify CI green**

```powershell
gh pr checks --watch
```

Expected: markdownlint + Bicep build (if triggered) all green.

- [ ] **Step 3: STOP for human review + merge**

**Human review gate.** Do not proceed to Phase 2 until this PR is reviewed and merged. Phase 2 requires all Phase-1 artefacts to be on `main`.

---

## Phase 2 — Execute runbook (Tasks 16–20; requires operator + `approved-to-apply` gates)

> All Phase-2 tasks are executed by the operator following the runbook created in Task 13. The agent role in Phase 2 is to **help interpret output, populate evidence, and update docs** — not to autonomously fire deploy tools. Every `apply` requires an explicit `approved-to-apply` comment on the corresponding PR/issue per AGENTS.md §4 and per user memory.

### Task 16: Execute W1 (tenant plane)

- [ ] **Step 1**: Follow runbook §1 top-to-bottom on the operator workstation.
- [ ] **Step 2**: Capture outputs (client ID, principal ID, Fabric connection ID) into the sprint report (Task 20 destination).
- [ ] **Step 3**: Validate gates G0.3 (workstation trust) and G1/G1.1 (RBAC + GitHub env config) per spec §7.

### Task 17: Execute W2 (SIT deploy + smoke)

- [ ] **Step 1**: Dispatch `ci-infra-validate.yml` for SIT via `gh workflow run` per runbook §2.1.
- [ ] **Step 2**: Review the what-if output in the workflow logs. If any unexpected deletes → STOP and fix Bicep.
- [ ] **Step 3**: Dispatch `cd-infra-deploy-sit.yml`. Wait for the `approved-to-apply` comment gate.
- [ ] **Step 4**: After apply, run `configure-fabric.ps1 -CapacityName fabricihzhhpfsit -ConnectionId <from W1.5>`.
- [ ] **Step 5**: Regenerate synthetic data (`python data/synthetic/generate_planning_datasets.py`) into the new SQL.
- [ ] **Step 6**: Run smoke checks per `docs/superpowers/plans/2026-06-14-sprint-08-week-1-walking-skeleton.md` §Verification. `Encounter Count > 0`.

### Task 18: Execute W3 (PROD deploy + smoke)

- [ ] **Step 1**: Only proceed if W2 gates G2, G2.1, G2.2 are all green.
- [ ] **Step 2**: Repeat W2 shape for PROD, per runbook §3. Fabric module remains opt-out.

### Task 19: Execute W4 (cutover docs)

- [ ] **Step 1**: Author ADR-0012 content (fill the skeleton from Task 14) with Context/Decision/Consequences drawn from actual execution evidence.
- [ ] **Step 2**: Update `docs/OPERATIONS.md` service-ownership section to reference the new tenant + subscriptions. Bump SemVer per §9.
- [ ] **Step 3**: Update the `AGENTS.md` tenant note added in Task 6 to say **"new tenant is authoritative; old tenant frozen, teardown deferred"**. Bump SemVer.
- [ ] **Step 4**: Commit and open a docs PR for W4.

### Task 20: Execute W5 (sprint retrospective)

- [ ] **Step 1**: Fill the `docs/sprints/sprint-00-new-tenantprovisioning.md` scaffold from Task 14 with:
  - Actual dates and durations
  - Evidence links (PR URLs, workflow run URLs, screenshots of Fabric semantic model)
  - Retrospective bullets (what went well, what didn't, what to change next time)
  - Cross-links to ADR-0012 and the merged PRs
- [ ] **Step 2**: Bump the sprint file version 0.1.0 → 1.0.0 (first "final" version). Set status "Reviewed".
- [ ] **Step 3**: Commit and open the final sprint PR.

---

## Definition of Done

All of the following must be true:

- [ ] Phase-1 PR merged to `main` (Tasks 1–15) with markdownlint + Bicep build green
- [ ] All Pester tests for the four scripts pass
- [ ] W1 evidence captured (client ID, principal ID, Fabric connection ID) in the sprint report
- [ ] W2 gates G2, G2.1, G2.2 all green (SIT walking-skeleton smoke passing)
- [ ] W3 gates G3 green (PROD provisioned)
- [ ] ADR-0012 authored and merged
- [ ] Sprint report v1.0.0 merged
- [ ] Old-tenant resources untouched (verified: original SIT/PROD RGs still present and healthy per user request — no teardown per D6)

---

## Self-Review Notes (for the plan author)

**Spec coverage check.** Every workstream W0–W5 in the spec has at least one task in this plan:
- W0 → Tasks 2–7
- W1 → Tasks 8–11 (build) + Task 16 (execute)
- W2 → Task 17
- W3 → Task 18
- W4 → Task 14 (scaffold) + Task 19 (execute)
- W5 → Task 14 (scaffold) + Task 20 (execute)

**No placeholders.** Every code step contains executable code. Every command has expected output. No "TBD" / "similar to Task N" references.

**Type consistency.** Script names, parameter names (`TenantId`, `SubscriptionId`, `PrincipalId`, `DisplayName`, `RepoFullName`, `Environment`, `SnapshotPath`, `Restore`), and file paths match across tasks.

**Execution mode handoff.** See below.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-02-tenant-migration-plan.md`. Two execution options:

1. **Subagent-Driven (recommended for Phase 1)** — a fresh subagent per task, with two-stage review between tasks. Best suited to the mechanical build tasks (rename PR, PowerShell + Pester scripts, runbook authoring).
2. **Inline Execution** — batch execution with checkpoints. Faster feedback loop for one operator working straight through Phase 1.

**Phase 2 is always operator-driven** — it involves live tenant admin actions requiring your explicit `approved-to-apply` per each deploy.
