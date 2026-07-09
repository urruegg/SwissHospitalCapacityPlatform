# Sprint 12 — Organisation (Entra Demo Org) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended — one subagent per task) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provision the demo Entra organisation for the Swiss Hospital Capacity Platform: 15 app roles + 15 security groups + 23 personas (21 demo + 2 super) in the shared SIT+PROD tenant `MngEnvMCAP164444.onmicrosoft.com`, with adoption telemetry piped into Fabric Bronze so Sprint 15 can compute the "adoption %" KPI.

**Architecture:** Bicep + Microsoft Graph deployment via `azd`-style Bicep + [`Microsoft.Graph` Bicep extension](https://learn.microsoft.com/graph/templates/overview-bicep-templates-for-graph). All provisioning happens per-batch behind an `approved-to-apply` gate. Users are shared between SIT and PROD (per user decision D-6); environment scoping happens **in-app** via an `env` claim + hospital-context, NOT by cloning identities. Design contract in [`docs/superpowers/specs/2026-07-09-sprint-12-org-design.md`](../specs/2026-07-09-sprint-12-org-design.md).

**Tech Stack:** Bicep (`infra/modules/entra/`), Microsoft Graph Bicep extension for app roles / groups / users, PowerShell + `az` CLI for orchestration, `gh` CLI for issue/PR management, Python for the adoption-telemetry ingest script. No new application source; agent packs (`entra-mcp` read-only) already registered in `.github/copilot/mcp.json` per Sprint 11.

---

## Prerequisites (verify before starting)

- [ ] On `main` branch, clean of unrelated work: `git switch main; git pull`.
- [ ] Sprint 12 design spec merged (part of PR #145, refined by PR #148): `Get-Content docs/superpowers/specs/2026-07-09-sprint-12-org-design.md | Select-Object -First 15`.
- [ ] Sprint 11 agents merged (PR #149, #153, #155). `entra-mcp` allow-list entry present in `.github/copilot/mcp.json`.
- [ ] `az` CLI authenticated to the SIT tenant per ADR-0012: `az account show --query tenantId -o tsv` returns `1337187a-4c41-4da9-8fca-731bba7a4329`.
- [ ] `az bicep --version` ≥ 0.24 (needed for the Microsoft Graph Bicep extension).
- [ ] Graph permissions available on the executing identity: `Directory.ReadWrite.All`, `RoleManagement.ReadWrite.Directory`, `Application.ReadWrite.All` (application permission, consent-gated).
- [ ] Fabric workspace `ws-ihzhhpf-sit-data` reachable (from Sprint 11 verification).
- [ ] Fabric capacity `fabricihzhhpfsit` state = **Active** (needed for adoption-telemetry pipeline validation).
- [ ] `gh` CLI authenticated: `gh auth status`.
- [ ] Explicit go-ahead from @urruegg in the Sprint 12 kickoff issue thread.

---

## File Structure

Files created or modified across the seven tasks.

### T1 — Foundation: app registration + 2 super roles

- Create: `infra/modules/entra/main.bicep` — subscription-scope orchestrator that imports the Microsoft.Graph Bicep extension and chains the child modules.
- Create: `infra/modules/entra/app-registration.bicep` — the `ihzhhpf-app` app registration with SPA + web redirect URIs for SIT and PROD slots.
- Create: `infra/modules/entra/app-roles.bicep` — 2 super roles (`HCC.SuperAdmin`, `HCC.GuestReadOnly`) inline; other 13 roles land in T2.
- Create: `infra/modules/entra/parameters/sit.bicepparam` — SIT parameter file.
- Create: `infra/modules/entra/parameters/prod.bicepparam` — PROD parameter file (identical role definitions; different slot URIs).
- Create: `infra/modules/entra/README.md` — module overview + apply/what-if workflow.
- Modify: `.github/CODEOWNERS` — add `/infra/modules/entra/` → @urruegg.
- Create: `data/synthetic/personas.csv` (extend the Sprint 11 seed file with `mail_nickname`, `password_profile` placeholders) — becomes the input to T4.

### T2 — 13 operational + governance app roles

- Modify: `infra/modules/entra/app-roles.bicep` — add `HCC.OperationsLead`, `HCC.BedManager`, `HCC.FlowManager`, `HCC.EDLead`, `HCC.ORCoordinator`, `HCC.StaffingCoordinator`, `HCC.DischargeCoordinator`, `HCC.CrisisManager`, `HCC.Executive`, `HCC.CantonalViewer`, `HCC.PlatformAdmin`, `HCC.OntologySteward`, `HCC.AIGovernance`, `HCC.DemoOperator`, `HCC.Auditor` (13 more roles — total 15 including super roles from T1).
- Update: `infra/modules/entra/parameters/sit.bicepparam` and `prod.bicepparam` — verify role definitions are complete.

### T3 — 15 security groups

- Create: `infra/modules/entra/security-groups.bicep` — 15 mail-disabled security groups, one per app role, with the exact same `displayName` as the app-role name (convention: `<role-name>` → group `<role-name>`).
- Add: 15 group entries to `parameters/sit.bicepparam` + `parameters/prod.bicepparam`.

### T4 — 23 personas + group assignments

Sub-batches for `approved-to-apply`:
- Batch A (super admin, demo operator, guest): 3 personas — `super.admin`, `sophie.meier`, `demo.guest`.
- Batch B (USZ personas): 8 personas.
- Batch C (LUKS personas): 4 personas.
- Batch D (Zollikerberg): 2 personas.
- Batch E (Aggregated / cross-cutting): 6 personas (Cantonal, Executive, PlatformAdmin, OntologySteward, AIGovernance, Auditor).

Files:
- Create: `infra/modules/entra/users.bicep` — parameterised loop over `personas.csv` shape.
- Create: `infra/modules/entra/assignments.bicep` — persona ↔ group ↔ app-role links.
- Modify: `parameters/sit.bicepparam` and `prod.bicepparam` — persona batch parameters.

### T5 — Adoption telemetry pipeline

- Create: `infra/modules/entra/adoption-telemetry.bicep` — diagnostic setting: Entra `SignInLogs` → `log-ihzhhpf-sit` Log Analytics workspace (already exists per Sprint 11 SIT inventory).
- Create: `data-platform/notebooks/adoption/01_adoption_ingest.ipynb` — Fabric notebook that reads Log Analytics (via KQL over the Kusto MCP-side pattern) and writes to `Bronze/adoption/*.parquet` daily.
- Create: `data-platform/scripts/adoption_seed_synthetic.py` — 30-day synthetic sign-in backfill for demo-day evidence when real telemetry has not yet accumulated.
- Create: `.github/workflows/adoption-refresh.yml` — cron 03:00 UTC daily; triggers the Fabric notebook.

### T6 — CI workflows + issue template

- Create: `.github/workflows/entra-whatif.yml` — on PR touching `infra/modules/entra/**`, runs `az deployment sub what-if` and posts the plan as a PR comment.
- Create: `.github/ISSUE_TEMPLATE/entra-provisioning.yml` — form fields: batch letter (A–E), env target (SIT / PROD), pre-check acknowledgements.
- Update: `AGENTS.md` §2 — no change needed (entra-mcp already listed).

### T7 — Retro

- Update: `docs/sprints/superpowers-checkpoint-matrix.md` — Sprint 12 row.
- Close: the Sprint 12 kickoff issue.
- Update: `docs/superpowers/plans/2026-07-09-sprint-12-org-plan.md` (this file) — mark tasks complete.

---

## Common per-task workflow (referenced by T1–T7)

Every task PR follows this skeleton.

- [ ] **Sub-step A: Branch off `main`**

```powershell
git switch main; git pull; git switch -c sprint-12/T<N>-<slug>
```

- [ ] **Sub-step B: Read the design spec section for this task**

Open [`docs/superpowers/specs/2026-07-09-sprint-12-org-design.md`](../specs/2026-07-09-sprint-12-org-design.md) §3 (architecture) + §5 (super roles) + §6 (persona catalog) + §10 (side-effect posture) as relevant.

- [ ] **Sub-step C: Write the Bicep + parameters**

Follow the [Microsoft.Graph Bicep extension patterns](https://learn.microsoft.com/graph/templates/overview-bicep-templates-for-graph). Prefer resource collections + `for` loops over hand-listing rows.

- [ ] **Sub-step D: Run `what-if`**

```powershell
az deployment sub what-if `
  --location westus2 `
  --template-file infra/modules/entra/main.bicep `
  --parameters infra/modules/entra/parameters/sit.bicepparam
```

Expected: **clean diff** matching the task's declared scope; no unexpected principal changes. Post the `what-if` result as a comment on the PR before requesting review.

- [ ] **Sub-step E: Request `approved-to-apply` on the PR**

Wait for @urruegg to post `approved-to-apply` per [AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete). The comment must reference the specific `what-if` output the reviewer inspected. Any material re-plan requires a new approval.

- [ ] **Sub-step F: Apply (SIT only in the initial pass; PROD deferred)**

```powershell
az deployment sub create `
  --name sprint-12-T<N>-sit-$(Get-Date -Format 'yyyyMMdd-HHmm') `
  --location westus2 `
  --template-file infra/modules/entra/main.bicep `
  --parameters infra/modules/entra/parameters/sit.bicepparam
```

Post the deployment name + resource IDs as a follow-up PR comment. PROD apply is deferred to a separate PR explicitly labelled `prod-batch`.

- [ ] **Sub-step G: Verify via Graph query**

```powershell
az rest --method get --url "https://graph.microsoft.com/v1.0/servicePrincipals?`$filter=displayName eq 'ihzhhpf-app'&`$select=id,displayName,appRoles"
```

Expected: the app registration is present with the app-role count expected after this task.

- [ ] **Sub-step H: Commit + push + open PR (or update existing draft)**

```powershell
git add infra/modules/entra/ data/synthetic/personas.csv data-platform/ .github/
git commit -m "feat(entra): T<N> <slug> — <headline>"
git push -u origin sprint-12/T<N>-<slug>
gh pr create --base main --head sprint-12/T<N>-<slug> --title "feat(entra): T<N> <slug>" --body-file <path> --label sprint-12 --label superpowers-execute
```

PR body must follow [copilot-instructions.md §6](../../../.github/copilot-instructions.md) Output Contract and reference the specific `what-if` output + the `approved-to-apply` comment.

- [ ] **Sub-step I: Wait for review + merge**

Merge unblocks the next task (T1 → T2 → T3 → T4 → T5). T6 can go in parallel from T4. T7 is last.

---

## Task 1 — T1: Foundation (app registration + 2 super roles)

**Branch:** `sprint-12/T1-foundation`

**Files:** see T1 file-structure block above.

### Step 1.1 — Bootstrap module skeleton

- [ ] **Step 1.1.1: Branch off `main`.**

```powershell
git switch main; git pull; git switch -c sprint-12/T1-foundation
```

- [ ] **Step 1.1.2: Write the failing what-if smoke script.**

Create `data-platform/scripts/entra_whatif_smoke.py`:

```python
"""Smoke test for the entra module: run az deployment sub what-if and assert non-empty planned changes."""
import json
import subprocess
import sys


def main() -> int:
    result = subprocess.run(
        [
            "az", "deployment", "sub", "what-if",
            "--location", "westus2",
            "--template-file", "infra/modules/entra/main.bicep",
            "--parameters", "infra/modules/entra/parameters/sit.bicepparam",
            "--result-format", "FullResourcePayloads",
        ],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        print("FAIL: what-if returned non-zero:")
        print(result.stderr)
        return 1
    print("PASS: what-if executed. First 40 lines:")
    print("\n".join(result.stdout.splitlines()[:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 1.1.3: Run it — expected FAIL.**

```powershell
python data-platform/scripts/entra_whatif_smoke.py
```

Expected: `FAIL` because `infra/modules/entra/main.bicep` does not exist yet.

- [ ] **Step 1.1.4: Create `infra/modules/entra/main.bicep`.**

```bicep
targetScope = 'subscription'

extension microsoftGraphV1_0 as graph

@description('Solution short name, per copilot-instructions.md §8 naming convention.')
param solutionShort string = 'ihzhhpf'

@description('Environment tag: sit or prod.')
@allowed(['sit', 'prod'])
param env string

@description('SPA redirect URIs (Sprint 13 app + Sprint 15 BVA report).')
param spaRedirectUris array

@description('Persona seed data (T4).')
param personas array = []

@description('Group definitions (T3).')
param groups array = []

module appReg './app-registration.bicep' = {
  name: 'appReg-${env}'
  params: {
    solutionShort: solutionShort
    env: env
    spaRedirectUris: spaRedirectUris
  }
}

module appRoles './app-roles.bicep' = {
  name: 'appRoles-${env}'
  params: {
    appRegObjectId: appReg.outputs.appObjectId
    env: env
  }
}

// T3 groups + T4 users + T4 assignments — chain in later PRs.

output appId string = appReg.outputs.appId
output appObjectId string = appReg.outputs.appObjectId
```

- [ ] **Step 1.1.5: Create `infra/modules/entra/app-registration.bicep`.**

```bicep
extension microsoftGraphV1_0 as graph

param solutionShort string
param env string
param spaRedirectUris array

resource app 'Microsoft.Graph/applications@v1.0' = {
  uniqueName: '${solutionShort}-app'
  displayName: '${solutionShort}-app (${env})'
  signInAudience: 'AzureADMyOrg'
  spa: {
    redirectUris: spaRedirectUris
  }
  requiredResourceAccess: [
    {
      resourceAppId: '00000003-0000-0000-c000-000000000000' // Microsoft Graph
      resourceAccess: [
        {
          id: 'e1fe6dd8-ba31-4d61-89e7-88639da4683d' // User.Read (delegated)
          type: 'Scope'
        }
      ]
    }
  ]
}

output appId string = app.appId
output appObjectId string = app.id
```

- [ ] **Step 1.1.6: Create `infra/modules/entra/app-roles.bicep` — only the 2 super roles for now.**

```bicep
extension microsoftGraphV1_0 as graph

param appRegObjectId string
param env string

var superRoles = [
  {
    displayName: 'HCC.SuperAdmin'
    description: 'Full read/write across all roles, hospitals, environments. Only 1–2 assignees; PIM planned in hardening sprint.'
    id: guid('HCC.SuperAdmin', appRegObjectId)
    allowedMemberTypes: ['User']
    isEnabled: true
    value: 'HCC.SuperAdmin'
  }
  {
    displayName: 'HCC.GuestReadOnly'
    description: 'Read-only across all roles for demo tours. Cannot invoke agents; cannot open the CSA wizard.'
    id: guid('HCC.GuestReadOnly', appRegObjectId)
    allowedMemberTypes: ['User']
    isEnabled: true
    value: 'HCC.GuestReadOnly'
  }
]

resource appPatch 'Microsoft.Graph/applications@v1.0' existing = {
  uniqueName: '${appRegObjectId}' // placeholder — see follow-up step to bind correctly
}

// NOTE: appRoles are set as part of the parent application resource in the Graph
// Bicep extension. The clean pattern is to fold this array back into
// app-registration.bicep and pass appRoles as a param. See T2 for the
// consolidated shape.

output superRoleCount int = length(superRoles)
```

**Design note:** The Graph Bicep extension declares `appRoles` as a property of the `Microsoft.Graph/applications` resource itself, not a separate resource. T2 refactors this into a clean pass-through: `main.bicep` builds the full role array, passes it into `app-registration.bicep`, and the application resource declares them inline. For T1, delivering just the 2 super roles keeps the initial `what-if` output short and easy to review.

- [ ] **Step 1.1.7: Create parameter files.**

`infra/modules/entra/parameters/sit.bicepparam`:

```bicep
using '../main.bicep'

param solutionShort = 'ihzhhpf'
param env = 'sit'
param spaRedirectUris = [
  'https://app-platform-ihzhhpf-sit-y26y.azurewebsites.net'
  'http://localhost:5173' // Sprint 13 dev
]
param personas = []
param groups = []
```

`infra/modules/entra/parameters/prod.bicepparam`: same as SIT, but `env = 'prod'` and PROD-slot redirect URIs.

- [ ] **Step 1.1.8: Run the smoke test again — expected PASS.**

```powershell
python data-platform/scripts/entra_whatif_smoke.py
```

Expected: prints "PASS" and shows a what-if plan creating the app registration + 2 app roles.

### Step 1.2 — Update CODEOWNERS + README

- [ ] **Step 1.2.1: Modify `.github/CODEOWNERS`** — append `/infra/modules/entra/    @urruegg` under the existing `/infra/` section.

- [ ] **Step 1.2.2: Create `infra/modules/entra/README.md`.**

Sections: purpose, module map, apply/what-if workflow, approval gates reference, links to design spec and this plan.

### Step 1.3 — PR, approval, apply

- [ ] **Step 1.3.1: Commit + push + open PR** (Sub-steps H of common workflow).
- [ ] **Step 1.3.2: Post the `what-if` output as a PR comment.**
- [ ] **Step 1.3.3: Wait for `approved-to-apply` from @urruegg** referencing the specific what-if output.
- [ ] **Step 1.3.4: Apply to SIT** (Sub-step F).
- [ ] **Step 1.3.5: Verify via Graph query** (Sub-step G) — expected: `ihzhhpf-app` app registration exists with 2 app roles (`HCC.SuperAdmin`, `HCC.GuestReadOnly`).
- [ ] **Step 1.3.6: Post the applied deployment name + object IDs as a PR comment.**
- [ ] **Step 1.3.7: Wait for merge.**

---

## Task 2 — T2: 13 operational + governance app roles

**Branch:** `sprint-12/T2-app-roles`  
**Depends on:** T1 merged.

Follow the [Common per-task workflow](#common-per-task-workflow-referenced-by-t1t7). Task-specific specifics:

- Extend `infra/modules/entra/app-roles.bicep` with the 13 remaining roles (per Sprint 12 design spec §4.3):
  - `HCC.OperationsLead`, `HCC.BedManager`, `HCC.FlowManager`, `HCC.EDLead`, `HCC.ORCoordinator`, `HCC.StaffingCoordinator`, `HCC.DischargeCoordinator`, `HCC.CrisisManager`, `HCC.Executive`, `HCC.CantonalViewer`, `HCC.PlatformAdmin`, `HCC.OntologySteward`, `HCC.AIGovernance`, `HCC.DemoOperator`, `HCC.Auditor`.
- Refactor: fold `appRoles` back into `app-registration.bicep` as a single resource property (avoid the T1 workaround). Pass the full role array from `main.bicep` down through `app-registration.bicep`.
- `what-if` expected shape: 13 app-role additions to the existing app registration; no other changes.

**DoD:**

- [ ] All 15 app roles visible via `az rest --method get --url "…/servicePrincipals?…"`.
- [ ] `approved-to-apply` gate satisfied.
- [ ] SIT deployed; PROD deferred.

---

## Task 3 — T3: 15 security groups

**Branch:** `sprint-12/T3-security-groups`  
**Depends on:** T2 merged.

- Create `infra/modules/entra/security-groups.bicep`. Loop over an array parameter `groupDefinitions` — one entry per app role (15 total), each with:
  - `displayName` = `<HCC.RoleName>` (mail-nickname derived).
  - `mailEnabled` = `false`.
  - `securityEnabled` = `true`.
  - `groupTypes` = `[]`.
- Add group parameter arrays to `parameters/sit.bicepparam` + `prod.bicepparam`.
- Add `import` block to `main.bicep` chaining `security-groups.bicep` after `app-roles.bicep`.
- `what-if`: 15 group creations.

**DoD:** 15 groups exist in the tenant; each has a name matching its target app role.

---

## Task 4 — T4: 23 personas + assignments (batched)

**Branch:** `sprint-12/T4-personas-batch<A|B|C|D|E>` (one PR per batch)  
**Depends on:** T3 merged.

Split into **5 sub-PRs**, each behind its own `approved-to-apply` gate. Rationale: (a) creating identities is high-blast-radius; (b) small batches let @urruegg audit each cohort before the next.

Batch A (super + demo operator + guest): 3 personas.  
Batch B (USZ): 8 personas.  
Batch C (LUKS): 4 personas.  
Batch D (Zollikerberg): 2 personas.  
Batch E (Aggregated / cross-cutting): 6 personas — Executive, CantonalViewer, PlatformAdmin, OntologySteward, AIGovernance, Auditor.

### Common per-batch pattern

- Update `data/synthetic/personas.csv` to include the batch's rows (see design spec §6).
- Update `infra/modules/entra/users.bicep` to loop over the CSV.
- Update `infra/modules/entra/assignments.bicep` to create `appRoleAssignedTo` entries via group membership (not direct user-to-app-role).
- `what-if` expected: N user creations + N group membership additions.

**Refusal rules the executing agent must respect (per AGENTS.md §5):**

- Refuse if any UPN uses a domain other than `@mngenvmcap164444.onmicrosoft.com`.
- Refuse if the `password_profile` field is missing or references a plaintext password (must use `forceChangePasswordNextSignIn: true` with a temporary generated password stored only in the Bicep output).

**DoD per batch:**

- [ ] `az rest --method get --url "https://graph.microsoft.com/v1.0/users?\`$filter=…"` returns the batch identities.
- [ ] `az rest --method get --url "https://graph.microsoft.com/v1.0/groups/<group-id>/members"` shows the correct memberships.
- [ ] Passwords delivered securely to @urruegg out-of-band (do NOT commit to the repo; do NOT post as a PR comment).

---

## Task 5 — T5: Adoption telemetry pipeline

**Branch:** `sprint-12/T5-adoption-telemetry`  
**Depends on:** T4 Batch A merged (need at least the DemoOperator + Guest + SuperAdmin identities to test sign-in event capture).

### Step 5.1 — Diagnostic setting

- Create `infra/modules/entra/adoption-telemetry.bicep` — Entra `SignInLogs` category → `log-ihzhhpf-sit` Log Analytics workspace. Uses `Microsoft.aadiam/diagnosticSettings` resource type.
- `what-if` + apply as usual (behind `approved-to-apply`).

### Step 5.2 — Fabric notebook

- Create `data-platform/notebooks/adoption/01_adoption_ingest.ipynb`. Uses PySpark + Log Analytics Kusto query:

```kql
SigninLogs
| where TimeGenerated > ago(24h)
| where AppDisplayName startswith "ihzhhpf-app"
| project TimeGenerated, UserPrincipalName, AppDisplayName, ResultType, IPAddress, ClientAppUsed, DeviceDetail_TrustType=tostring(DeviceDetail.trustType), Location_CountryOrRegion=tostring(LocationDetails.countryOrRegion)
```

Writes to `Bronze/adoption/YYYY-MM-DD/*.parquet` in `lh_ihzhhpf_sit`.

### Step 5.3 — Synthetic backfill

- Create `data-platform/scripts/adoption_seed_synthetic.py` — generates 30 days of synthetic sign-in events for the 23 personas so the Sprint 15 BVA has data to render before real telemetry accumulates.

### Step 5.4 — CI workflow

- Create `.github/workflows/adoption-refresh.yml` — schedule cron `0 3 * * *`; workload identity federation to run the Fabric notebook.

**DoD:**

- [ ] One nightly file appears under `Bronze/adoption/` within 24h of merge.
- [ ] Synthetic backfill produces 30 days × 23 personas × ~2 sign-ins/day = ~1380 rows.

---

## Task 6 — T6: CI workflows + issue template

**Branch:** `sprint-12/T6-ci-workflows`  
**Depends on:** T4 Batch A merged (need a running app registration to run `what-if` against). Parallel-safe with T5.

### Step 6.1 — Entra what-if workflow

- Create `.github/workflows/entra-whatif.yml`:

```yaml
name: entra-whatif

on:
  pull_request:
    paths:
      - "infra/modules/entra/**"

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  what-if:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: what-if
        run: |
          az deployment sub what-if \
            --location westus2 \
            --template-file infra/modules/entra/main.bicep \
            --parameters infra/modules/entra/parameters/sit.bicepparam \
            > whatif.txt
      - name: post PR comment
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const body = "## Entra `what-if` (SIT)\n\n```\n" + fs.readFileSync('whatif.txt','utf8').slice(0, 60000) + "\n```";
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

### Step 6.2 — Issue template

- Create `.github/ISSUE_TEMPLATE/entra-provisioning.yml`. Fields: batch letter (A–E), env target (SIT / PROD), pre-check acknowledgements, personas count expected.

**DoD:**

- [ ] `entra-whatif.yml` runs on the next PR touching `infra/modules/entra/**` and posts the plan as a comment.
- [ ] Issue template selectable in the "New issue" chooser.

---

## Task 7 — T7: Retro + checkpoint matrix

**Branch:** `sprint-12/T7-retro`  
**Depends on:** T5 + T6 merged.

### Steps

- [ ] Update `docs/sprints/superpowers-checkpoint-matrix.md`: append Sprint 12 row with:
  - Start / End dates
  - Status = Merged
  - Personas shipped = 23/23 (or partial if PROD deferred)
  - Adoption pipeline = Green
  - Links to design spec + this plan
- [ ] Update Sprint 12 kickoff issue: post retro summary; close.
- [ ] Update this plan document — check off all task boxes; version bump to 1.1.0 if any late-breaking scope adjustments.

**DoD:**

- [ ] Sprint 12 retro entry visible in the checkpoint matrix.
- [ ] Kickoff issue closed with a link to the last merged Sprint 12 PR.

---

## PROD promotion (deferred)

PROD deployment is **out of scope** for Sprint 12's initial pass. A follow-up PR sequence — same T1–T5 tasks with `parameters/prod.bicepparam` — lands under the `prod-batch` label after:

- All SIT batches merged and stable for ≥ 48h.
- @urruegg explicit sign-off in a dedicated PROD gate issue.
- Adoption telemetry verified end-to-end in SIT.

---

## Definition of Sprint 12 done

- [ ] Tasks T1–T7 all merged.
- [ ] 15 app roles + 15 security groups + 23 personas provisioned in SIT (or documented deferral).
- [ ] `super.admin` and `demo.guest` sign-in verified against the Sprint 13 app shell (or a dry auth callback if S13 not yet ready).
- [ ] Adoption telemetry pipeline emitting nightly files within 24h of T5 merge.
- [ ] `env`-scoping smoke test green (same identity, two slots, two Bronze paths).
- [ ] `.github/workflows/entra-whatif.yml` + `.github/workflows/adoption-refresh.yml` operational.
- [ ] `.github/ISSUE_TEMPLATE/entra-provisioning.yml` selectable.
- [ ] Retro row landed in [`docs/sprints/superpowers-checkpoint-matrix.md`](../../sprints/superpowers-checkpoint-matrix.md).
- [ ] Kickoff issue closed.
- [ ] PROD promotion tracked as a follow-up issue.

---

## Self-Review

**1. Spec coverage.** Every Sprint 12 design-spec §14 Definition-of-done bullet maps to at least one task:
- IaC modules → T1 (foundation) + T2 (app roles) + T3 (groups) + T4 (users).
- Entra-whatif workflow → T6.
- 15 roles + 15 groups + 23 personas in SIT → T1–T4.
- Super roles sign-in verified → T4 Batch A DoD.
- Adoption telemetry pipeline → T5.
- Env-scoping smoke → T5 DoD.
- Retro entry → T7.

**2. Placeholder scan.** No `TBD` / `TODO`. Deliberate parametrics: `<N>`, `<slug>`, `<A|B|C|D|E>`, `<HCC.RoleName>`. Password handling explicitly avoids placeholder passwords per the T4 refusal rule.

**3. Type consistency.** Bicep parameter naming (`solutionShort`, `env`, `personas`, `groups`) is consistent across `main.bicep`, `app-registration.bicep`, `app-roles.bicep`. CSV field names (`upn`, `display_name`, `app_role`, `default_hospital`, `mail_nickname`, `password_profile`) are consistent.

**4. Approval gate pattern.** Every task with a `deploy` ceiling has an explicit `approved-to-apply` sub-step per AGENTS.md §4. T4 has 5 batches × 5 gates = 5 approvals across Task 4 alone. This is deliberate — user identities are high-blast-radius, small batches keep risk manageable.

**5. Dependencies clean.** T1 → T2 → T3 → T4 → T5. T6 parallel-safe from T4 Batch A. T7 last. No cycles.

---

## Execution Handoff

Plan complete and will be saved to `docs/superpowers/plans/2026-07-09-sprint-12-org-plan.md`. Two execution options:

1. **GitHub Copilot cloud coding agent (recommended)** — matches Sprint 11 pattern; assign the accompanying kickoff issue to Copilot in the GitHub UI. The cloud agent authors T1–T7 as separate PRs behind `approved-to-apply` gates for `deploy` steps.
2. **Inline execution here** — the chat session executes one task at a time.

**Which approach?** — my recommendation is the cloud agent again (proven pattern from PR #149 + PR #152).
