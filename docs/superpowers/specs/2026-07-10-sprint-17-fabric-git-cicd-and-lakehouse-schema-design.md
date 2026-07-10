# Sprint 17 — Fabric ↔ GitHub Integration + Lakehouse Schema Hardening — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-10 |
| **Author** | Urs Rüeegg |
| **Status** | Draft for review |
| **Previous Version** | n/a (new — Sprint 17 kickoff) |
| **Anchor triggers** | Sprint 16 T5 SIT go-live retro (2026-07-10); [PR #174 residual risks](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/174); [PR #175 follow-ups](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/175) |
| **Runtime posture** | GitHub Copilot coding agent + Fabric Git integration (workspace-level sync per [Learn](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration)); no change to per-agent runtime posture (ADR-0008 unchanged) |
| **Best-practice references** | [Overview of Fabric Git integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration); [Fabric Git integration process](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-process); [Manage Git branches](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/manage-branches); [Source-code format](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format); [Network security for CI/CD](https://learn.microsoft.com/en-us/fabric/cicd/cicd-security) |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Scope](#2-scope)
3. [Architecture and workflow](#3-architecture-and-workflow)
4. [Fabric Git integration decision (workspace ↔ branch)](#4-fabric-git-integration-decision-workspace--branch)
5. [Supported vs. unsupported Fabric items](#5-supported-vs-unsupported-fabric-items)
6. [Lakehouse schema hardening (`gold.csa_simulation_runs`)](#6-lakehouse-schema-hardening-goldcsa_simulation_runs)
7. [Verification path for schema-enabled lakehouses](#7-verification-path-for-schema-enabled-lakehouses)
8. [Side-effect posture and approval gates](#8-side-effect-posture-and-approval-gates)
9. [Guardrails and risk model](#9-guardrails-and-risk-model)
10. [Dependencies](#10-dependencies)
11. [Definition of done](#11-definition-of-done)

---

## 1. Goal and desired end state

Two related but independent hardening items surfaced during the Sprint 16 T5 SIT go-live (2026-07-10):

1. **Fabric ↔ GitHub Git integration** — replace the current manual `updateDefinition` REST-pushes for Fabric items (notebook v3 → v4 → v5 → v6 loop cost several hours) with the Microsoft-supported workspace-level Git sync. This lets us version-control **Notebooks, Environments (env-csa), Lakehouse metadata, Semantic models, Reports, Eventstreams, Pipelines, Mirrored databases** directly from Fabric UI edits without hand-rolled REST scripts.
2. **Lakehouse schema hardening** — the Sprint 16 verification wrote `csa_simulation_runs` to `Tables/` at the root of `lh_ihzhhpf_sit`. But `lh_ihzhhpf_sit` is a **schema-enabled** lakehouse with existing schemas `dbo`, `bronze`, `silver`, `gold`. The root-level write is a shortcut that breaks the layered pattern and makes the table invisible to the SQL analytics endpoint under any expected schema. Move it under `gold.csa_simulation_runs` (where all downstream analytics tables live) and update the notebook + docs accordingly.

**Desired end state:**

* `ws-ihzhhpf-sit-data` is Git-integrated with this repo. A **`fabric-sync` orphan branch** (not `main`) receives Fabric commits. Every Fabric → repo change flows through a normal PR to `main` for CODEOWNERS review — the existing PR gate is preserved (§9 guardrails).
* Repo folder `fabric/` holds the Fabric item definitions. Manual `updateDefinition` REST scripts are retired for the sync'd items.
* `csa_simulation_runs` is a proper Delta table under `gold.csa_simulation_runs`. The v6 verification notebook and any downstream BI consumer reference the schema-qualified path.
* `csa-verify-mvp` rerun on 2026-07-10+ writes to the schema-qualified table and passes 8/8 Spark jobs.
* Table-list verification for schema-enabled lakehouses uses the SQL analytics endpoint (the deprecated `/lakehouses/{id}/tables` REST endpoint returns `UnsupportedOperationForSchemasEnabledLakehouse` and is unusable).
* One ADR (0026) records the Fabric Git integration model, one ADR (0027) records the schema strategy for `lh_ihzhhpf_sit`.

---

## 2. Scope

### 2.1 In-scope MVP

* **T1** — Fabric Git integration on `ws-ihzhhpf-sit-data`, bound to a `fabric-sync` orphan branch in this repo, with a repo-side folder `fabric/`. First-pass commit + reconcile.
* **T2** — Move `csa_simulation_runs` under `gold.csa_simulation_runs`. Update `csa-verify-mvp.ipynb` (v7) and the README (§Verify).
* **T3** — Table-list verification helper (`data-platform/scripts/csa/list-lakehouse-tables.py`) that queries the SQL analytics endpoint for schema-enabled lakehouses. Replaces the failing REST call used in `.tmp/check-lh-tables.ps1`.
* **T4** — ADR-0026 (Fabric Git integration model).
* **T5** — ADR-0027 (lakehouse schema strategy).
* **T6** — Update `.github/copilot-instructions.md`, `AGENTS.md`, and `docs/OPERATIONS.md` with the new "prototype in Fabric UI → auto-sync to `fabric-sync` branch → PR to main" workflow.

### 2.2 Out-of-scope / deferred

* Per-developer feature workspaces (`ws-ihzhhpf-sit-data-<dev>`). Deferred — single-developer demo scope; revisit if a second developer joins.
* Full deployment pipeline (Fabric CI/CD Deployment Pipelines). Deferred — we already have `main` as the single environment; Deployment Pipelines matter when we add `test` / `prod` workspaces.
* Migration of Sprint 10 Eventstream, Sprint 15 BVA Direct Lake report, and other Fabric items to Git integration. Optional in this sprint — T1 enables the mechanism; individual item migration can be phased.
* Full lakehouse schema audit (`bronze` / `silver` / `gold` boundary rules across all Sprint 10-14 tables). This sprint only fixes `csa_simulation_runs`. Broader schema policy is an ADR follow-up item.
* Real PHI in simulations (synthetic only, per ADR-0016).

---

## 3. Architecture and workflow

### 3.1 Before (Sprint 16 pattern)

```text
   Developer                                            ws-ihzhhpf-sit-data
   ─────────                                            ─────────────────────
   Edit .ipynb in .tmp/          ──────────────►        Cell content updated
   Push via updateDefinition                            (via REST)
   REST script                                          
   Rebuild + push v2, v3, v4...                         Same notebook re-edited
                                                         each iteration
                                                         
   ────► git commit .ipynb into data-platform/notebooks/ (manual, easy to miss)
```

**Problems:** manual REST scripts, easy to forget the git capture step, no rollback beyond git history of the tmp file, no versioning of environments/lakehouses/semantic models at all.

### 3.2 After (Sprint 17 T1 pattern)

```text
   Developer                    Fabric workspace                   Repo (main)
   ─────────                    ────────────────                   ───────────
                                                                   
   Edit .ipynb in Fabric UI     ws-ihzhhpf-sit-data                
                                bound to `fabric-sync` branch      
                                                                   
   Click "Commit changes"       Auto-writes to `fabric-sync`        
   in Fabric Source Control  ──►  branch as fabric/<item>/*.json    
                                and *.py (per source-code-format)   
                                                                   
                                                                    Open PR:
                                                                    fabric-sync
                                                                    → main
                                                                    (CODEOWNERS
                                                                    review)
                                                                                     
                                                                    Merge
                                                                                     
                                                                    fabric/... in main
```

Key properties:

* **Fabric never writes directly to `main`.** The `fabric-sync` orphan branch is the only branch Fabric can commit to. `main` is only updated via reviewed PRs. This preserves every guardrail already in copilot-instructions.md §6 (PR Output Contract) and §7 (Code Review Checklist).
* **Bidirectional sync.** Repo → Fabric works too: after merging a PR into `main`, we can cherry-pick or rebase changes onto `fabric-sync`, and Fabric's "Update all" pulls them into the workspace.
* **Item-level granularity.** Fabric commits one item at a time (Notebook, Environment, Lakehouse metadata, ...) so PRs stay small and reviewable.

### 3.3 Folder layout in repo

Per Fabric [source-code format](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format), Fabric writes a subfolder per item with a stable naming convention:

```text
fabric/
├── csa-verify-mvp.Notebook/
│   ├── .platform
│   └── notebook-content.py
├── env-csa.Environment/
│   ├── .platform
│   └── Setting/
│       └── environment.yml
├── lh_ihzhhpf_sit.Lakehouse/
│   ├── .platform
│   └── shortcuts.metadata.json      (schemas + shortcut definitions; not data)
├── ...
└── README.md                         (repo-side: what lives here and why)
```

`data-platform/notebooks/csa/csa-verify-mvp.ipynb` (Sprint 16 T5 capture, PR #175) **stays** as the human-readable canonical artefact for the git-history-of-record. `fabric/csa-verify-mvp.Notebook/` is the Fabric-managed twin. When they drift, `fabric/` is the source of truth for what Fabric actually runs; `data-platform/notebooks/csa/*.ipynb` is the periodically re-captured human-readable snapshot. This distinction is documented in §11 of the plan and in `fabric/README.md`.

### 3.4 What Fabric Git integration does *not* do

* **Data is not synced.** Only item **definitions** (notebook cells, environment config, semantic model YAML, lakehouse schema list). Row-level data stays in OneLake and is not committed.
* **Secrets are not synced.** Fabric strips connection secrets when serializing to Git. Any per-workspace secrets (workspace identity credentials, mirrored-database connection strings) must be re-supplied on the target workspace during "Update all".
* **Unsupported items are ignored.** See §5 for the current list. They stay in the workspace but never appear in `fabric-sync`.

---

## 4. Fabric Git integration decision (workspace ↔ branch)

Two viable models. This section records the choice and the alternatives considered.

| Model | Pros | Cons | Verdict |
|-------|------|------|---------|
| **A. Bind `ws-ihzhhpf-sit-data` to `main`** | Simplest. Every Fabric commit lands directly on the canonical branch. | Bypasses CODEOWNERS review. Fabric UI edits become auto-merged commits with no PR gate. Breaks copilot-instructions.md §6 + §7. | ❌ Rejected |
| **B. Bind `ws-ihzhhpf-sit-data` to a `fabric-sync` orphan branch, PR to `main`** | Preserves CODEOWNERS + PR review gate. Fabric commits are proposals, not merges. Rollback = revert PR. Compatible with existing `.github/CODEOWNERS`. | Extra step (open the PR). Requires disciplined cadence to avoid a stale `fabric-sync`. | ✅ **Chosen** |
| **C. Per-developer feature workspace `ws-ihzhhpf-sit-data-<dev>` bound to feature branch** | Full isolation between developers. Standard Fabric CI/CD pattern. | Costs another F2 capacity. Overkill for our single-dev demo scope. | 🕓 Deferred to a later sprint |

**Chosen model B** is aligned with Microsoft's [Manage Git branches](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/manage-branches) guidance for teams that want a review gate before code hits their protected branch.

**`fabric-sync` branch rules (defined here, enforced in `.github/CODEOWNERS` update in T6):**

* Never rebased or force-pushed.
* Only Fabric writes to it directly. Repo-side changes come in via merge (or by re-syncing from `main`).
* Reserved-name pattern: only branches literally named `fabric-sync` and `fabric-sync/*` are allowed to receive Fabric commits.
* PRs from `fabric-sync` → `main` follow the same PR Output Contract (§6 of copilot-instructions.md).

---

## 5. Supported vs. unsupported Fabric items

Per the [Fabric Git integration Learn overview](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration#supported-items) (updated 2026-06-15), the following items in `ws-ihzhhpf-sit-data` support Git integration:

| Item type | Status | Relevance to us |
|-----------|--------|-----------------|
| **Notebook** | ✅ GA | `csa-verify-mvp`, `csa-simulate` and any future Fabric notebooks. Retire `updateDefinition` REST scripts. |
| **Environment** | ✅ GA | `env-csa` (azure-cosmos + azure-identity). Versioned per commit. |
| **Lakehouse (definition)** | ✅ GA | `lh_ihzhhpf_sit` schema list + shortcut definitions (not data). |
| **Semantic model** | 🅿️ Preview | Sprint 15 BVA model + any Direct Lake models. Preview-flag documented in ADR-0026. |
| **Report** | 🅿️ Preview | Sprint 15 BVA report + Sprint 14 evidence report. |
| **Eventstream** | ✅ GA | Sprint 10 M1 Eventstream (if any). |
| **KQL database / Queryset** | ✅ GA | Not currently used. |
| **Pipeline / Copy Job / Dataflow gen2** | ✅ GA | Not currently used. |
| **Mirrored database** | ✅ GA | Not currently used (Sprint 16 mirroring deferred). |
| **Warehouse** | 🅿️ Preview | Not used. |
| **ML experiments / models** | 🅿️ Preview | Not used. |
| **Data Agents** | 🅿️ Preview | Currently unused (per ADR-0008 our agents live in Container Apps). |

**Not supported (silently ignored by Fabric Git integration):** the Fabric F2 **capacity** itself (Bicep-managed), workspace-level RBAC assignments (kept in `infra/`), and Managed Private Endpoints (Bicep-managed via `infra/modules/network/`).

**Result:** Fabric Git integration and our existing Bicep-managed infra are complementary — Bicep owns capacity/network/RBAC; Fabric Git owns item definitions. No conflict.

---

## 6. Lakehouse schema hardening (`gold.csa_simulation_runs`)

### 6.1 Current state (Sprint 16 T5)

* `csa-verify-mvp.ipynb` v6 writes to `abfss://.../30594c20-46ba-40ea-91fa-4701b105e0b9/Tables/csa_simulation_runs`.
* `lh_ihzhhpf_sit` is a **schema-enabled** lakehouse with existing schemas `dbo`, `bronze`, `silver`, `gold`.
* Writing to `Tables/<name>` (no schema prefix) lands the Delta files at the lakehouse root — outside any known schema. The table shows up in the OneLake Files view but not under `Tables/dbo`, `Tables/bronze`, `Tables/silver`, or `Tables/gold` in the Fabric Explorer.
* The Fabric REST call `GET /lakehouses/{id}/tables` returns `UnsupportedOperationForSchemasEnabledLakehouse` on schema-enabled lakehouses (verified 2026-07-10 in `.tmp/check-lh-tables.ps1`).

### 6.2 Target state

* Table moves to `abfss://.../30594c20-46ba-40ea-91fa-4701b105e0b9/Tables/gold/csa_simulation_runs`.
* Notebook writes via the schema-qualified path (still ABFSS URI — the session-independence rationale from PR #175 §Design notes is preserved).
* The table is discoverable under `Tables → gold → csa_simulation_runs` in the Fabric Explorer and via the SQL analytics endpoint as `gold.csa_simulation_runs`.
* `data-platform/notebooks/csa/README.md` §Verify updated to reflect the new path.
* Old root-level write is **removed** (blown-away — demo scope, no downstream consumer yet). If a consumer emerges before T2 lands, a shortcut from `gold/csa_simulation_runs` → old path is added instead.

### 6.3 Why `gold`, not `silver` or `bronze`

Consistent with the medallion architecture skill (`.github/skills/e2e-medallion-architecture/`):

* `bronze` = raw ingested data (would be Cosmos change-feed rows without transformation).
* `silver` = cleaned + conformed (would be Cosmos rows joined to capacity master data, PHI-gated).
* `gold` = analytics-ready denormalized tables for BI + reporting.

`csa_simulation_runs` is a simulation *output* consumed by BI (Power BI Direct Lake) and downstream agents. It is analytics-ready by construction — gold is the correct layer.

---

## 7. Verification path for schema-enabled lakehouses

Sprint 16 verification used a REST call that no longer works on our lakehouse type. Replace with a helper that queries the SQL analytics endpoint.

**Script:** `data-platform/scripts/csa/list-lakehouse-tables.py`

**Contract:**

```python
def list_lakehouse_tables(
    workspace_id: str,
    lakehouse_id: str,
    schema: str | None = None,
) -> list[dict]:
    """Return {schema, name, format} for every table in the lakehouse.
    Uses the Fabric SQL analytics endpoint. Works for both schema-enabled
    and schema-less lakehouses. When `schema` is provided, filters to
    that schema only."""
```

**Implementation approach:**

1. Resolve the SQL endpoint URL for the lakehouse via the Fabric REST API (`GET /workspaces/{ws}/lakehouses/{lh}` → `properties.sqlEndpointProperties.connectionString`).
2. Connect via `pyodbc` + ActiveDirectoryDefault auth (or `azure.identity` for MSAL-token-based conn strings).
3. Query `INFORMATION_SCHEMA.TABLES` — this is a standard SQL surface and works on schema-enabled lakehouses.
4. Return a plain list of dicts.

**Consumer:** the Sprint 17 T2 verification step, and any future troubleshooting where "does this table actually exist" needs a definitive answer.

---

## 8. Side-effect posture and approval gates

Per AGENTS.md §3-§4, all Sprint 17 actions are `write`-ceiling **except**:

| Action | Ceiling | Approval |
|--------|---------|----------|
| Enable Fabric Git integration on `ws-ihzhhpf-sit-data` (first-time bind) | `deploy` | Explicit `approved-to-apply` on the T1 issue |
| Delete the root-level `csa_simulation_runs` folder (post-migration) | `delete` | Explicit `approved-to-apply` on the T2 issue |
| Any `az` / `Fabric REST` mutation | Same as agent's ceiling per AGENTS.md §3 | Same as AGENTS.md §4 |

The `fabric-sync` branch itself is created via `git` (write-ceiling, no cloud state). No approval gate needed to create the branch.

---

## 9. Guardrails and risk model

| Risk | Mitigation |
|------|------------|
| **Fabric UI edit lands on `main` without review** | Bind workspace to `fabric-sync` branch, never `main` (§4). Enforce in `.github/CODEOWNERS` — `fabric-sync` protected against direct push except from Fabric's service principal. |
| **Fabric commit contains a secret** | Fabric [strips secrets](https://learn.microsoft.com/en-us/fabric/cicd/cicd-security#secrets-and-connection-strings) at serialization time. Additionally, our GitHub secret-scan CI runs on all branches (including `fabric-sync`). Any secret found blocks the merge. |
| **`fabric-sync` drifts stale — Fabric shows "outdated"** | Every sprint, the last agent action is `Update all` from `main` back to `fabric-sync`, keeping them at parity. Add a nightly reminder issue via GitHub Actions in T6. |
| **Migrating `csa_simulation_runs` breaks a downstream consumer** | Demo scope: no downstream consumer exists yet. Confirm via `Get-Content .github/dependabot.yml` and BI report `.pbip` scan before deleting. If a consumer surfaces mid-sprint, add a schema shortcut instead of deleting the root path. |
| **Preview items (Semantic model, Report) misbehave in Git sync** | Documented in ADR-0026. If they cause churn, exclude via workspace-level Fabric Git config OR keep them out of the sync. Preview status is transparent in `fabric/` subfolder README. |
| **Fabric workspace identity does not have write access to `fabric-sync`** | Verified in T1 first-commit test. If missing, add a GitHub Personal Access Token or Fabric OAuth connection per Learn [Git provider setup](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started). |

---

## 10. Dependencies

* **Merged before starting T1:** PR #174 (Cosmos Bicep fixes), PR #175 (v6 notebook capture).
* **T1 → T2:** T2 depends on the `fabric-sync` mechanism only if we choose to sync the notebook via Fabric Git rather than the current `.ipynb` update. Concretely: T2 can run in parallel with T1 by using the existing manual push flow; the T1 mechanism is retrofitted after.
* **T4 (ADR-0026) blocks T6 doc updates** — the ADR fixes the terminology used in copilot-instructions.md and OPERATIONS.md.
* **T5 (ADR-0027) blocks T2 merge** — ADR lands first, then the migration PR references it.

---

## 11. Definition of done

* [ ] Fabric workspace `ws-ihzhhpf-sit-data` is Git-integrated with this repo, bound to branch `fabric-sync`, folder `fabric/`.
* [ ] First `Commit changes` from Fabric produces the expected `fabric/<item>/*` folder set. Snapshot in PR description.
* [ ] `fabric-sync` branch has CODEOWNERS + branch protection preventing direct human push (only Fabric's app + repo admins can commit).
* [ ] `data-platform/notebooks/csa/csa-verify-mvp.ipynb` v7 writes to `Tables/gold/csa_simulation_runs`. Rerun in SIT produces 8/8 green Spark jobs.
* [ ] Old root-level `Tables/csa_simulation_runs` path is empty (removed) after explicit `approved-to-apply`.
* [ ] `data-platform/scripts/csa/list-lakehouse-tables.py` exists, has ≥ 1 pytest, and works against `lh_ihzhhpf_sit`.
* [ ] ADR-0026 (Fabric Git integration) merged, Status: **Accepted**.
* [ ] ADR-0027 (Lakehouse schema strategy) merged, Status: **Accepted**.
* [ ] `.github/copilot-instructions.md`, `AGENTS.md`, `docs/OPERATIONS.md`, and `data-platform/notebooks/csa/README.md` updated with the new workflow. All version headers bumped per §9 of copilot-instructions.md.
* [ ] Sprint 17 golden-tasks under `agents/<name>/golden-tasks.md` for any agent whose runbook references the old `updateDefinition` flow are updated (`orchestrator`, `test-verifier-agent` at minimum — verified in T6).
* [ ] Sprint 17 retro closed with lessons-learned added to `docs/superpowers/plans/2026-07-10-sprint-17-fabric-git-cicd-and-lakehouse-schema-plan.md`.
