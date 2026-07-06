# Sprint 10 Kickoff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transition Sprint 10 from a merged charter into an executable state by landing 3 kickoff PRs, executing the D1 working-tree revert, and creating 15 GitHub issues.

**Architecture:** 3 sequential PRs to `main`, each scoped to one concern (PRD drift correction, gitignore hygiene, tooling commit), followed by an issue-batch and a local-tree revert. Each PR is small (< 10 files) and reviewable in < 10 minutes. Full architecture in [`docs/superpowers/specs/2026-07-06-sprint-10-kickoff-design.md`](../specs/2026-07-06-sprint-10-kickoff-design.md).

**Tech Stack:** Markdown edits, `.gitignore`, existing Python + PowerShell scripts (no new logic), `gh` CLI for issue creation, `git` for revert.

---

## Prerequisites (verify before starting)

- [ ] On `main` branch, clean of any post-PR-#102 commits: `git switch main && git pull`.
- [ ] Design spec + ADR merged (this planning PR): `git log --oneline | grep -E '(kickoff-design|adr.*0018)'`.
- [ ] `gh` CLI authenticated: `gh auth status`.
- [ ] `az` CLI authenticated to the SIT tenant: `az account show --query name` → `ME-MngEnvMCAP164444-urruegg-1`.
- [ ] `npx markdownlint-cli2` available (already used in this session).

---

## File Structure

Files created or modified across the 3 PRs:

#### PR #1 — PRD drift correction

- Modify: `docs/PRD.md` (add FR-VIZ + NFR-GOV sections, bump 1.4.0 → 1.5.0, update §7 traceability matrix)
- Modify: `docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md` (append §7.7 ADR-0018 provenance blockquote)
- Reference: `docs/adr/0018-add-fr-viz-and-nfr-gov-ids.md` (already merged in this planning PR)

#### PR #2 — `.gitignore` hygiene

- Modify: `.gitignore` (add `**/*.egg-info/`, `**/*.pbi/cache.abf` if missing)

#### PR #3 — Sprint 10 tooling commit

- Add: `apps/sim-capacity/src/producer_sim.py`
- Add: `data-platform/scripts/import_notebooks.py`
- Add: `data-platform/scripts/run_notebooks.py`
- Add: `data-platform/scripts/upload_to_onelake.py`
- Add: `data-platform/scripts/deploy_fabric_data_agent.py`

#### Local-tree ops (no PR)

- Revert: `data-platform/reports/capacity-dashboard.Report/definition.pbir`
- Revert: `data-platform/reports/capacity-dashboard.Report/definition/pages/pages.json`
- Revert: `data-platform/reports/capacity-dashboard.Report/definition/report.json`
- Restore: `data-platform/reports/capacity-dashboard.Report/definition/pages/page1-capacity/page.json`
- Restore: `data-platform/reports/capacity-dashboard.Report/definition/pages/page2-or/page.json`
- Delete: `data-platform/reports/capacity-dashboard.Report/.pbi/`
- Delete: `data-platform/reports/capacity-dashboard.Report/.platform`
- Delete: `data-platform/reports/capacity-dashboard.Report/StaticResources/`
- Delete: `data-platform/reports/capacity-dashboard.Report/definition/pages/ad8d9cbb00d05e04d371/`
- Delete: `data-platform/reports/capacity-dashboard.Report/definition/version.json`

#### GitHub-only (no repo files)

- Create: 15 issues (`S10.1..S10.12` + `S10.13` + `S10.14` + tracker `[S10]`)
- Create: Sprint 10 milestone

---

## Task 1 — PR #1: PRD v1.5.0 additions + design-spec footer

**Branch:** `sprint-10/prd-drift-fix`

**Files:**

- Modify: `docs/PRD.md`
- Modify: `docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`

- [ ] **Step 1: Branch off `main`**

```powershell
git switch main; git pull; git switch -c sprint-10/prd-drift-fix
```

- [ ] **Step 2: Update PRD.md header (v1.4.0 → v1.5.0)**

Change the version-header table:

```markdown
| **Version** | 1.5.0 |
| **Date** | 2026-07-06 |
| **Previous Version** | 1.4.0 (added FR-VIZ-* + NFR-GOV-* per ADR-0018) |
```

- [ ] **Step 3: Append new FR section "I) Visualization And Dashboards (Sprint 09 T5)"**

Insert immediately after the existing FR "H) Semantic Ontology" section, before the "## Non-Functional Requirements" heading:

```markdown
### I) Visualization And Dashboards (Sprint 09 T5)

Sprint 09 T5 deltas formalised per [ADR-0018](adr/0018-add-fr-viz-and-nfr-gov-ids.md).
Referenced from [Sprint 09 v2 design spec §7.7](superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#77-traceability).

| ID | Requirement |
| -- | ----------- |
| `FR-VIZ-001` | The platform shall provide an operational **bed-capacity dashboard page** exposing current occupancy, forecast pressure windows, and data-quality signals, aligned with `FR-CX-005`. |
| `FR-VIZ-002` | The platform shall provide an operational **OR-steering dashboard page** exposing case-level utilisation, first-case on-time performance, cancellation, and idle-slot metrics, aligned with `FR-CX-005`. |
```

- [ ] **Step 4: Append new NFR section "I) Governance and Audit (Sprint 09 T5)"**

Insert at the end of the NFR sections (after "H) Semantic Ontology (Sprint 9)"):

```markdown
### I) Governance And Audit (Sprint 09 T5)

Sprint 09 T5 deltas formalised per [ADR-0018](adr/0018-add-fr-viz-and-nfr-gov-ids.md).

| ID | Requirement |
| -- | ----------- |
| `NFR-GOV-001` | The platform shall record change-management traceability for semantic-model, dashboard, and agent artefacts (aligns with `FR-GOV-001`). |
| `NFR-GOV-002` | The platform shall support audit-review workflows for governance evidence artefacts (aligns with `FR-GOV-004`). |
| `NFR-GOV-003` | The dashboard consumption path shall enforce role-scoped filtering that prevents PHI-tagged column exposure to any non-owner role (extends [ADR-0016](adr/0016-no-phi-in-mvp-demo-scope.md) gate 4). |
| `NFR-GOV-004` | Semantic-model and dashboard artefacts shall be round-trippable to source-controlled TMDL/PBIP such that any deployed state can be replayed from repository content alone. |
| `NFR-GOV-005` | Governance evidence artefacts shall be co-located with the sprint or ADR that produced them under `docs/sprints/*/evidence/` or `docs/adr/*.md`. |
| `NFR-GOV-006` | Every dashboard visual shall carry per-visual traceability back to its underlying semantic-model measure and its ontology-grounded source (`hcp:*` entities), aligned with `FR-CX-006` and `FR-ONT-004`. |
```

- [ ] **Step 5: Update PRD §7 traceability matrix**

Add a new row for the sprint-10 charter mapping to the new IDs. Find the traceability table and add:

```markdown
| [`docs/sprints/sprint-10-e2e-pipeline-and-dashboard-completion.md`](sprints/sprint-10-e2e-pipeline-and-dashboard-completion.md) | `FR-VIZ-001..002`, `NFR-GOV-001..006`, `FR-CX-005`, `FR-DATA-005`, `FR-DATA-008`, `FR-GOV-001`, `FR-GOV-004`, `FR-ONT-004`, `FR-ONT-006` |
```

- [ ] **Step 6: Append provenance blockquote to design-spec §7.7**

Locate line 678 area (T5 Dashboard row) and immediately below the traceability table append:

```markdown
> **Provenance for `FR-VIZ-*` and `NFR-GOV-*` IDs.** These IDs were originally referenced here without corresponding PRD entries. They were formalised in `docs/PRD.md` v1.5.0 per [ADR-0018](../../adr/0018-add-fr-viz-and-nfr-gov-ids.md). See ADR for semantic content and rationale.
```

Design-spec version is **not bumped** — this is a minor prose clarification, not a semantic change.

- [ ] **Step 7: Lint locally**

```powershell
npx --yes markdownlint-cli2 "docs/PRD.md" "docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md"
```

Expected: `Summary: 0 error(s)`. If errors, fix and re-run.

- [ ] **Step 8: Commit**

```powershell
git add docs/PRD.md docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md
git commit -m "docs(prd): bump 1.4.0 -> 1.5.0 - add FR-VIZ-* + NFR-GOV-* per ADR-0018`n`nCloses Sprint 09 v2 design-spec drift surfaced during PR #101 review.`nAppends FR section I (Visualization And Dashboards) and NFR section I`n(Governance and Audit). Design-spec section 7.7 gets a provenance footer.`n`nRefs FR-VIZ-001, FR-VIZ-002, NFR-GOV-001..006, ADR-0018"
```

- [ ] **Step 9: Push + open PR**

```powershell
git push -u origin sprint-10/prd-drift-fix
gh pr create --base main --title "docs(prd): v1.5.0 - add FR-VIZ-* + NFR-GOV-* (ADR-0018)" --body-file <path-to-pr-body>
```

PR body must include per copilot-instructions §6:

- Requirements Implemented: `FR-VIZ-001`, `FR-VIZ-002`, `NFR-GOV-001..006` (**introduced**), ADR-0018 reference
- Documentation Updated checkbox: PRD.md + design-spec
- Version bump note per §9

- [ ] **Step 10: Wait for CI green, merge**

```powershell
gh pr checks <PR#>  # wait until all 4 checks green
gh pr merge <PR#> --merge --delete-branch
```

- [ ] **Step 11: Return to `main`**

```powershell
git switch main; git pull
```

---

## Task 2 — PR #2: `.gitignore` hygiene

**Branch:** `sprint-10/gitignore-hygiene`

**Files:**

- Modify: `.gitignore`

- [ ] **Step 1: Branch off `main`**

```powershell
git switch -c sprint-10/gitignore-hygiene
```

- [ ] **Step 2: Read current `.gitignore` for existing patterns**

```powershell
Get-Content .gitignore | Select-String -Pattern 'egg-info|pbi|StaticResources'
```

If `**/*.egg-info/` already present, skip Step 3 for that pattern.

- [ ] **Step 3: Append missing patterns**

Add (at end of file, with a section header comment):

```gitignore
# Python setuptools build artefacts (added Sprint 10 kickoff)
**/*.egg-info/

# Power BI Desktop local caches (per-item .pbip .gitignore already exists;
# add root-level backstop for editor-generated files that leak outside them)
**/.pbi/cache.abf
```

- [ ] **Step 4: Verify current dirty state is filtered**

```powershell
git status --short | Select-String -Pattern 'egg-info|cache.abf'
```

Expected: no matches (patterns now filter them).

- [ ] **Step 5: Commit + push**

```powershell
git add .gitignore
git commit -m "chore(gitignore): exclude Python egg-info + PBIP cache artefacts`n`nPre-Sprint-10 hygiene; ensures apps/sim-capacity/src/sim_capacity.egg-info/`nand PBIP local caches don't accidentally get committed with Sprint 10 tooling."
git push -u origin sprint-10/gitignore-hygiene
```

- [ ] **Step 6: Open PR, wait CI, merge**

```powershell
gh pr create --base main --title "chore(gitignore): exclude Python egg-info + PBIP cache artefacts" --body "Pre-Sprint-10 hygiene. See docs/superpowers/specs/2026-07-06-sprint-10-kickoff-design.md sect 4.3 for rationale."
gh pr checks <PR#>
gh pr merge <PR#> --merge --delete-branch
git switch main; git pull
```

---

## Task 3 — PR #3: Sprint 10 tooling commit

**Branch:** `sprint-10/tooling-commit`

**Files:**

- Add: `apps/sim-capacity/src/producer_sim.py`
- Add: `data-platform/scripts/import_notebooks.py`
- Add: `data-platform/scripts/run_notebooks.py`
- Add: `data-platform/scripts/upload_to_onelake.py`
- Add: `data-platform/scripts/deploy_fabric_data_agent.py`

- [ ] **Step 1: Branch off `main`**

```powershell
git switch -c sprint-10/tooling-commit
```

- [ ] **Step 2: Verify no secrets in each of the 5 scripts**

```powershell
foreach ($f in @('apps/sim-capacity/src/producer_sim.py', 'data-platform/scripts/import_notebooks.py', 'data-platform/scripts/run_notebooks.py', 'data-platform/scripts/upload_to_onelake.py', 'data-platform/scripts/deploy_fabric_data_agent.py')) {
    Write-Host "--- $f ---"
    Select-String -Path $f -Pattern '(sk-|password|secret|api_key|Bearer\s+[A-Za-z0-9]{20,}|"AccountKey=)' | ForEach-Object { Write-Host "SUSPECT: $($_.LineNumber): $($_.Line)" }
}
```

Expected: no output (no secrets). If any match, STOP and rotate before committing.

- [ ] **Step 3: Verify each script parses (no syntax errors)**

```powershell
foreach ($f in @('apps/sim-capacity/src/producer_sim.py', 'data-platform/scripts/import_notebooks.py', 'data-platform/scripts/run_notebooks.py', 'data-platform/scripts/upload_to_onelake.py', 'data-platform/scripts/deploy_fabric_data_agent.py')) {
    python -c "import ast; ast.parse(open(r'$f').read())" 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: $f"; break }
}
Write-Host 'all parse'
```

- [ ] **Step 4: Stage + commit**

```powershell
git add apps/sim-capacity/src/producer_sim.py data-platform/scripts/import_notebooks.py data-platform/scripts/run_notebooks.py data-platform/scripts/upload_to_onelake.py data-platform/scripts/deploy_fabric_data_agent.py
git commit -m "feat(sprint-10): commit T1/T2/T4 tooling (streaming producer + Fabric REST helpers)`n`nCommits the 5 pre-existing untracked scripts that Sprint 10 execution needs:`n- apps/sim-capacity/src/producer_sim.py - streaming producer (T1)`n- data-platform/scripts/import_notebooks.py - Fabric notebook import (T1/T2)`n- data-platform/scripts/run_notebooks.py - Fabric notebook run trigger (T1/T2)`n- data-platform/scripts/upload_to_onelake.py - OneLake Files/ upload (T3.7)`n- data-platform/scripts/deploy_fabric_data_agent.py - Fabric Data Agent deploy (T4/S10.10)`n`nRefs FR-DATA-005, FR-DATA-008, NFR-GOV-004 (round-trippability)."
```

- [ ] **Step 5: Push + open PR + wait CI + merge**

```powershell
git push -u origin sprint-10/tooling-commit
gh pr create --base main --title "feat(sprint-10): commit T1/T2/T4 tooling (5 scripts)" --body "..."
gh pr checks <PR#>
gh pr merge <PR#> --merge --delete-branch
git switch main; git pull
```

---

## Task 4 — D1 working-tree revert (local operation, no PR)

**Nature:** Destructive local operation. Executes only after all 3 PRs merged.

**Files affected:** See File Structure "Local-tree ops" above.

- [ ] **Step 1: Verify current state**

```powershell
git status --short | Select-String -Pattern 'capacity-dashboard.Report'
```

Confirm the modified + deleted + new files match §4.3 D1 list in the design spec.

- [ ] **Step 2: Revert modified Report files**

```powershell
git checkout -- data-platform/reports/capacity-dashboard.Report/definition.pbir
git checkout -- data-platform/reports/capacity-dashboard.Report/definition/pages/pages.json
git checkout -- data-platform/reports/capacity-dashboard.Report/definition/report.json
```

- [ ] **Step 3: Restore deleted page skeletons**

```powershell
git checkout -- data-platform/reports/capacity-dashboard.Report/definition/pages/page1-capacity/page.json
git checkout -- data-platform/reports/capacity-dashboard.Report/definition/pages/page2-or/page.json
```

- [ ] **Step 4: Delete new untracked Report scaffold — one path at a time**

⚠ Each command deletes untracked local content. If in doubt, back up first.

```powershell
Remove-Item -Recurse -Force data-platform/reports/capacity-dashboard.Report/.pbi
Remove-Item -Force data-platform/reports/capacity-dashboard.Report/.platform
Remove-Item -Recurse -Force data-platform/reports/capacity-dashboard.Report/StaticResources
Remove-Item -Recurse -Force data-platform/reports/capacity-dashboard.Report/definition/pages/ad8d9cbb00d05e04d371
Remove-Item -Force data-platform/reports/capacity-dashboard.Report/definition/version.json
```

- [ ] **Step 5: Verify clean**

```powershell
git status --short | Select-String -Pattern 'capacity-dashboard.Report'
```

Expected: no output. Everything Report-related now matches `main`.

- [ ] **Step 6: Do NOT touch `.pbip`** — kept for S10.13 investigation issue.

---

## Task 5 — GitHub issue batch (15 issues)

**Nature:** GitHub-only, no repo files. Executed after all 3 PRs merged and D1 revert clean.

- [ ] **Step 1: Create Sprint 10 milestone**

```powershell
gh api repos/urruegg/SwissHospitalCapacityPlatform/milestones -F title='Sprint 10' -F description='E2E Pipeline + Dashboard Completion (charter: docs/sprints/sprint-10-e2e-pipeline-and-dashboard-completion.md)' -F state=open
```

Capture the returned milestone `number` for the loop below.

- [ ] **Step 2: Create labels if missing**

```powershell
gh label create sprint-10 --color 0e8a16 --description 'Sprint 10 - E2E Pipeline + Dashboard Completion' 2>$null
gh label create tracker --color b60205 --description 'Sprint tracker issue' 2>$null
gh label create needs-design --color fbca04 --description 'Requires design spec before implementation' 2>$null
foreach ($t in 1..6) { gh label create "track-$t" --color 5319e7 --description "Sprint track T$t" 2>$null }
```

- [ ] **Step 3: Create tracker issue**

```powershell
gh issue create --title "[S10] Sprint 10 - E2E Pipeline + Dashboard Completion (tracker)" --label sprint-10,tracker --milestone 'Sprint 10' --body-file <path-to-tracker-body>
```

Tracker body must include: links to all 12 deliverable issues (populate after Step 4), charter link, DoD checklist mirrored from charter §6.

- [ ] **Step 4: Loop-create 12 deliverable issues (S10.1..S10.12)**

Use a script that reads sprint-10 charter §5 and constructs each issue body. Manual `gh issue create` for each is also acceptable — 12 issues is small enough. Bodies must include the sections listed in design §4.1.

Example for S10.1:

```powershell
gh issue create --title "[S10.1] T1: Fabric Eventstream Bicep + post-deploy portal wiring" `
    --label sprint-10,track-1,needs-design `
    --milestone 'Sprint 10' `
    --body @"
**Deliverable ID:** S10.1 (track T1 Eventstream + facts)

**Charter reference:** [Sprint 10 charter section 5, row S10.1](../blob/main/docs/sprints/sprint-10-e2e-pipeline-and-dashboard-completion.md#5-deliverables-mapped-from-retrospective-5)

**Retrospective source:** [Sprint 09 retrospective section 5, item 1](../blob/main/docs/sprints/sprint-09/retrospective.md#5-follow-ups-sprint-10)

**Acceptance criteria:**
- Fabric Eventstream provisioned via Bicep in ``infra/modules/data-platform/fabric-eventstream/``
- Post-deploy portal step executed against SIT (``configure-eventstream.ps1`` prerequisites satisfied)
- Eventstream ingestion connection to Fabric-managed Event Hub verified with a smoke event

**Dependencies:** none (T1 entry point)

**Design-doc scope:** brief spec required per design section 8

**Requirements advanced:** ``FR-DATA-001``, ``FR-DATA-003``, ``FR-DATA-005``, ``NFR-PERF-001``, ``NFR-GOV-004``
"@
```

Repeat for S10.2..S10.12 using charter §5 rows.

- [ ] **Step 5: Create S10.13 investigation issue**

```powershell
gh issue create --title "[S10.13] Investigate .pbip semanticModel artifact removal (Fabric-shift vs regression)" `
    --label sprint-10,track-5 `
    --milestone 'Sprint 10' `
    --body @"
Investigation: capacity-dashboard.pbip currently references only the ``report`` artifact; the ``semanticModel`` reference was removed during 2026-07-06 Fabric web-modeling activity.

**Hypotheses** (per design section 4.4):
- **A (Fabric-shift):** deliberate, aligned with NFR-GOV-004 (cloud is source of truth)
- **B (Regression):** Fabric web-modeling bug; needs upstream report

**Procedure:**
1. Open the .pbip in Power BI Desktop; observe artifact navigator
2. Try to re-add the semanticModel reference; round-trip via a small model edit
3. Compare to a freshly Desktop-authored PBIP baseline
4. Report findings; recommend fix or accept

**Outcome:** either raise upstream Fabric bug or update repo convention (potentially update NFR-GOV-004 wording to reflect Fabric-web-modeling behaviour).
"@
```

- [ ] **Step 6: Create S10.14 notebook-diff review issue**

```powershell
gh issue create --title "[S10.14] Review 4 modified reference notebooks (01_bronze .. 04_load_or_samples) - commit or revert" `
    --label sprint-10,track-1 `
    --milestone 'Sprint 10' `
    --body @"
The 4 reference notebooks under ``data-platform/notebooks/reference/`` have 216 lines of uncommitted diff (pre-existing dirty state from before Sprint 09 close). These were **not** authored in the 2026-07-06 Sprint 09 close session and their scope + correctness are unverified.

**Task:**
1. Review each notebook diff (``git diff data-platform/notebooks/reference/<file>``)
2. Determine if the changes represent complete Sprint 09/10 work or in-progress edits
3. If complete: commit with a Conventional Commit describing the change
4. If in-progress or uncertain: revert (``git checkout``) and flag original owner

**Files:**
- 01_bronze_master_data.ipynb (24 lines diff)
- 02_silver_master_data.ipynb (56 lines diff)
- 03_gold_master_data.ipynb (34 lines diff)
- 04_load_or_samples.ipynb (102 lines diff)
"@
```

- [ ] **Step 7: Update tracker body with deliverable-issue links**

```powershell
gh issue edit <tracker-issue-#> --body-file <updated-tracker-body>
```

Include the 12 + 2 issue numbers in the tracker's checklist.

- [ ] **Step 8: Verify final state**

```powershell
gh issue list --label sprint-10 --state open
```

Expected: **15 open issues** (tracker + 12 deliverables + 2 investigations).

---

## Task 6 — Kickoff completion checklist

- [ ] All 3 PRs merged to `main` (PRD, gitignore, tooling)
- [ ] D1 working-tree revert executed; `git status` shows no `capacity-dashboard.Report` entries
- [ ] `data-platform/reports/capacity-dashboard.pbip` still shows in `git status` (untouched; deferred to S10.13)
- [ ] `apps/sim-capacity/src/sim_capacity.egg-info/` no longer shows in `git status` (filtered by new gitignore)
- [ ] 15 Sprint 10 issues open on GitHub with `sprint-10` label
- [ ] Sprint 10 milestone exists and is linked to all 15 issues
- [ ] Sprint 10 charter §9 sprint-close checklist item "Full CI pipeline green" ready to be re-verified per PR
- [ ] User acknowledges kickoff complete → Sprint 10 T1 kick-off can begin (start with S10.1 issue)

---

## Rollback per PR

- **PR #1 revert:** `gh pr revert <PR#>` — reverts PRD to 1.4.0; ADR-0018 marked Superseded; design-spec footer removed
- **PR #2 revert:** `gh pr revert <PR#>` — restores previous `.gitignore`; egg-info reappears in `git status`
- **PR #3 revert:** `gh pr revert <PR#>` — 5 tooling scripts uncommitted; return to untracked state
- **D1 revert of the revert:** `git reflog` to restore the pre-revert working-tree state; deleted untracked files must be re-generated (Desktop re-open)
- **Issue batch reversal:** `gh issue delete <issue#>` per issue; milestone deletable via GitHub UI

---

## Estimation

- Task 1 (PR #1): 15–20 min including CI wait
- Task 2 (PR #2): 5–10 min
- Task 3 (PR #3): 10–15 min
- Task 4 (D1 revert): 3–5 min
- Task 5 (issue batch): 15–20 min (scripted); manual if hand-authored bodies: 30–45 min

**Total kickoff:** single focused session, ~60–90 min end-to-end.
