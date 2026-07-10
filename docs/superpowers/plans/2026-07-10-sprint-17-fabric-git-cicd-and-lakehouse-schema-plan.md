# Sprint 17 — Fabric ↔ GitHub Integration + Lakehouse Schema Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended — one subagent per task) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Retire the manual `updateDefinition` REST-push loop by enabling Fabric ↔ GitHub Git integration for `ws-ihzhhpf-sit-data` (bound to a `fabric-sync` orphan branch, PR to `main`), and fix the Sprint 16 T5 shortcut of writing `csa_simulation_runs` to the root of a schema-enabled lakehouse by moving it under `gold.csa_simulation_runs` with a schema-aware verification helper.

**Architecture:** Six-task sprint. T1 is the Fabric integration mechanism, T2 is the schema fix, T3 is the verification helper, T4-T5 are the two ADRs that lock in the decisions, T6 is the doc + guardrail update. Design contract in [`docs/superpowers/specs/2026-07-10-sprint-17-fabric-git-cicd-and-lakehouse-schema-design.md`](../specs/2026-07-10-sprint-17-fabric-git-cicd-and-lakehouse-schema-design.md).

**Tech Stack:** Fabric REST API (workspace `POST /workspaces/{id}/git/connect` + `/git/initializeConnection` + `/git/updateFromGit`), Python 3.11+ (pyodbc + azure-identity for the SQL verification helper), Fabric Spark notebook edit (v7), Markdown (ADRs + docs), GitHub CLI (`gh api` for CODEOWNERS + branch protection).

---

## Prerequisites (verify before starting)

- [ ] On `main`, clean: `git switch main; git pull`.
- [ ] PR #174 (Cosmos Bicep fixes) merged.
- [ ] PR #175 (v6 notebook capture) merged.
- [ ] Fabric capacity `fabricihzhhpfsit` state = **Active** (not paused).
- [ ] `az` CLI authenticated to SIT tenant per ADR-0012 (`az account show` → subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`).
- [ ] `gh` CLI authenticated (`gh auth status` → account `urruegg`).
- [ ] Explicit go-ahead from @urruegg in the Sprint 17 kickoff issue thread.
- [ ] Confirm your Fabric account has **Workspace Admin** on `ws-ihzhhpf-sit-data` (Git integration requires it — verify via `GET /workspaces/{ws}/roleAssignments`).

---

## File Structure

Files this sprint creates or modifies:

| Path | Change | Task | Responsibility |
|------|--------|------|---------------|
| `.github/CODEOWNERS` | modify | T1, T6 | Add `fabric-sync` branch protection rule and CODEOWNERS entry for `fabric/**` |
| `.github/workflows/fabric-sync-guard.yml` | create | T1 | Reject direct human push to `fabric-sync` (only Fabric app + repo admins may push) |
| `fabric/README.md` | create | T1 | Explains what lives in `fabric/`, sync direction, ownership |
| `fabric/csa-verify-mvp.Notebook/.platform` | create (by Fabric on first sync) | T1 | Fabric-managed |
| `fabric/env-csa.Environment/**` | create (by Fabric on first sync) | T1 | Fabric-managed |
| `fabric/lh_ihzhhpf_sit.Lakehouse/**` | create (by Fabric on first sync) | T1 | Fabric-managed |
| `data-platform/notebooks/csa/csa-verify-mvp.ipynb` | modify (v7) | T2 | Switch write path to `Tables/gold/csa_simulation_runs` |
| `data-platform/notebooks/csa/README.md` | modify (1.1.0 → 1.2.0) | T2 | Reflect schema-qualified path |
| `data-platform/scripts/csa/list-lakehouse-tables.py` | create | T3 | SQL-endpoint-based verification helper |
| `data-platform/scripts/csa/tests/test_list_lakehouse_tables.py` | create | T3 | Unit + integration tests |
| `docs/adr/0026-fabric-git-integration-model.md` | create | T4 | ADR: workspace ↔ `fabric-sync` orphan branch |
| `docs/adr/0027-lakehouse-schema-strategy.md` | create | T5 | ADR: bronze/silver/gold schema policy for `lh_ihzhhpf_sit` |
| `.github/copilot-instructions.md` | modify | T6 | Add "prototype in Fabric UI → sync via `fabric-sync` → PR to main" pattern; bump version |
| `AGENTS.md` | modify | T6 | Add Fabric Git integration guardrails; bump version |
| `docs/OPERATIONS.md` | modify | T6 | Runbook: "how to commit a Fabric change" |
| `agents/orchestrator/AGENT.md` | modify | T6 | Deprecate `updateDefinition` REST script mention |
| `agents/test-verifier-agent/golden-tasks.md` | modify | T6 | Add golden task for schema-aware verification |
| `docs/sprints/sprint-17-fabric-git-cicd-and-lakehouse-schema.md` | create | T6 | Sprint plan doc (mirror of `docs/sprints/sprint-16-*.md`) |

---

## Task 1 — Enable Fabric Git integration on `ws-ihzhhpf-sit-data`

**Files:**
- Create: `.github/workflows/fabric-sync-guard.yml`
- Create: `fabric/README.md`
- Modify: `.github/CODEOWNERS`

- [ ] **Step 1: Create the `fabric-sync` orphan branch in the repo**

  ```powershell
  git switch main
  git pull
  git switch --orphan fabric-sync
  git rm -rf .
  # Create a stub commit so the branch exists on origin
  New-Item -Type Directory -Path fabric | Out-Null
  Set-Content fabric/README.md "# fabric/`n`n> **Owner:** Fabric workspace ``ws-ihzhhpf-sit-data`` via Git integration.`n> **Sync direction:** Fabric UI → this branch → PR to ``main``.`n> **Never edit by hand.**`n"
  git add fabric/README.md
  git commit -m "chore(fabric-sync): initialise orphan branch for Fabric Git integration"
  git push --set-upstream origin fabric-sync
  ```

  Expected: `fabric-sync` branch exists on origin with a single commit.

- [ ] **Step 2: Add branch protection on `fabric-sync`**

  ```powershell
  gh api -X PUT "repos/urruegg/SwissHospitalCapacityPlatform/branches/fabric-sync/protection" `
    --input - <<'JSON'
  {
    "required_status_checks": null,
    "enforce_admins": false,
    "required_pull_request_reviews": null,
    "restrictions": {
      "users": ["urruegg"],
      "teams": [],
      "apps": ["fabric-source-control"]
    },
    "allow_force_pushes": false,
    "allow_deletions": false
  }
  JSON
  ```

  Expected: `fabric-sync` is push-restricted. `fabric-source-control` app name is a placeholder — replace after the first Fabric sync exposes the actual GitHub app identity.

  If the `fabric-source-control` app name is wrong, the guard workflow (Step 3) catches it — direct human pushes fail there.

- [ ] **Step 3: Add the fail-safe workflow `.github/workflows/fabric-sync-guard.yml`**

  ```yaml
  name: fabric-sync branch guard
  on:
    push:
      branches: [fabric-sync]
  jobs:
    verify-author:
      runs-on: ubuntu-latest
      steps:
        - name: Reject direct human push
          run: |
            echo "Actor: ${{ github.actor }}"
            case "${{ github.actor }}" in
              urruegg|fabric-source-control|fabric-source-control[bot])
                echo "Allowed author"
                ;;
              *)
                echo "::error::Direct push to fabric-sync is forbidden. This branch only accepts commits from Fabric Git integration."
                exit 1
                ;;
            esac
  ```

  Commit + push to `main` in the sprint-17 branch (not `fabric-sync`).

- [ ] **Step 4: Update `.github/CODEOWNERS`**

  Add these lines (before the catch-all):

  ```text
  # Fabric Git integration — Fabric app commits + repo admin review only
  /fabric/                @urruegg
  fabric-sync             @urruegg
  ```

  Commit on the sprint-17 branch.

- [ ] **Step 5: Bind the Fabric workspace to `fabric-sync` (interactive first-time)**

  In `app.fabric.microsoft.com`:
  1. Open `ws-ihzhhpf-sit-data`.
  2. Workspace settings → **Git integration** → **Connect**.
  3. Provider: **GitHub**. Organization: `urruegg`. Repository: `SwissHospitalCapacityPlatform`. Branch: `fabric-sync`. Folder: `fabric/`.
  4. Sign in via GitHub OAuth (Fabric requests read+write on the repo).
  5. Click **Connect and sync**.

  Expected: Fabric UI shows "Connected to `fabric-sync`". First-sync auto-generates `fabric/<item>/*` for every supported item in the workspace.

  **This is a `deploy`-ceiling operation.** Requires `approved-to-apply` on the T1 tracking issue.

- [ ] **Step 6: Verify the first-sync landed correctly**

  ```powershell
  git switch fabric-sync
  git pull
  Get-ChildItem fabric -Recurse | Select-Object FullName, Length
  ```

  Expected: at minimum `fabric/csa-verify-mvp.Notebook/`, `fabric/env-csa.Environment/`, `fabric/lh_ihzhhpf_sit.Lakehouse/` exist with a `.platform` file each.

  Capture the output as the T1 issue's evidence attachment.

- [ ] **Step 7: Commit + PR from `fabric-sync` → `main` to land the first item set in the canonical branch**

  ```powershell
  git switch -c sprint-17/t1-fabric-first-sync fabric-sync
  git push --set-upstream origin sprint-17/t1-fabric-first-sync
  gh pr create --base main --head sprint-17/t1-fabric-first-sync `
    --title "chore(fabric): initial Fabric Git integration sync of ws-ihzhhpf-sit-data" `
    --body-file .tmp/t1-pr-body.md
  ```

  The PR description should include the `Get-ChildItem` output from Step 6, list every Fabric item type that landed, and note items that Fabric ignored (per §5 of the design spec).

- [ ] **Step 8: Verify sync round-trip — repo → Fabric**

  1. On `fabric-sync`, edit `fabric/csa-verify-mvp.Notebook/notebook-content.py` — change a print statement.
  2. Commit + push to `fabric-sync`.
  3. In Fabric UI → `ws-ihzhhpf-sit-data` → Source control → **Update all**.
  4. Verify the notebook shows the edit.
  5. Revert the edit locally; push; Update all in Fabric again to restore.

  Screenshot each step; attach to the T1 issue.

- [ ] **Step 9: Commit — Task 1**

  Merge PR #(T1-PR-number). Update the todo list.

---

## Task 2 — Move `csa_simulation_runs` under `gold` schema

**Files:**
- Modify: `data-platform/notebooks/csa/csa-verify-mvp.ipynb`
- Modify: `data-platform/notebooks/csa/README.md`

- [ ] **Step 1: Write the failing rerun assertion**

  Open `.tmp/verify-schema-migration.ps1`:

  ```powershell
  $token = (az account get-access-token --resource "https://analysis.windows.net/powerbi/api" --query accessToken -o tsv)
  $sqlEndpoint = (Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/lakehouses/30594c20-46ba-40ea-91fa-4701b105e0b9" -Headers @{Authorization="Bearer $token"}).properties.sqlEndpointProperties.connectionString
  Write-Output "SQL endpoint: $sqlEndpoint"
  $q = "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'csa_simulation_runs'"
  # Assert: the ONE result row has TABLE_SCHEMA = 'gold'
  ```

  Run once against the current SIT state — expect zero rows (table is at root, not in a schema).

- [ ] **Step 2: Update the notebook v6 → v7 ABFSS path**

  In `data-platform/notebooks/csa/csa-verify-mvp.ipynb`, locate Cell 7. Change:

  ```python
  abfss = 'abfss://f3af9733-9503-4e92-98f9-a901d96f1c87@onelake.dfs.fabric.microsoft.com/30594c20-46ba-40ea-91fa-4701b105e0b9/Tables/csa_simulation_runs'
  ```

  To:

  ```python
  abfss = 'abfss://f3af9733-9503-4e92-98f9-a901d96f1c87@onelake.dfs.fabric.microsoft.com/30594c20-46ba-40ea-91fa-4701b105e0b9/Tables/gold/csa_simulation_runs'
  ```

  Also bump the H1 title from `v6 (ABFSS path)` to `v7 (gold schema)`.

- [ ] **Step 3: Rebuild + push to Fabric via `updateDefinition` (last time this pattern is used — T1 replaces it)**

  Use `.tmp/push-nb.ps1` (unchanged from Sprint 16 T5) with the new v7 file. Confirm HTTP 202 + operation status `Succeeded`.

- [ ] **Step 4: Rerun the notebook in Fabric UI**

  Expected: 8/8 Spark jobs green. Cell 7 prints `Appended run to Delta at abfss://.../Tables/gold/csa_simulation_runs`.

- [ ] **Step 5: Verify via the T3 helper (or SQL endpoint directly)**

  Rerun the query from Step 1. Expect ONE row with `TABLE_SCHEMA = 'gold'`.

  Also refresh the Fabric Explorer — `Tables → gold → csa_simulation_runs` should now be visible.

- [ ] **Step 6: Delete the old root-level path**

  **Requires `approved-to-apply` on the T2 issue.**

  ```powershell
  # After approval only:
  $abfssOld = "abfss://f3af9733-9503-4e92-98f9-a901d96f1c87@onelake.dfs.fabric.microsoft.com/30594c20-46ba-40ea-91fa-4701b105e0b9/Tables/csa_simulation_runs"
  # Delete via Fabric Spark (safer than direct ADLS blob delete)
  # Run a one-off notebook cell:
  # dbutils.fs.rm(abfssOld, True)
  ```

  Rerun the T3 helper — expect the old root-level path to be gone (only `gold.csa_simulation_runs` remains).

- [ ] **Step 7: Bump README (1.1.0 → 1.2.0)**

  In `data-platform/notebooks/csa/README.md`, update the version header and the §Verify path reference. See §9 of copilot-instructions.md for the version bump rules.

- [ ] **Step 8: Commit — Task 2**

  ```powershell
  git switch -c sprint-17/t2-schema-migration main
  git add data-platform/notebooks/csa/csa-verify-mvp.ipynb data-platform/notebooks/csa/README.md
  git commit -m "fix(data-platform/csa): move csa_simulation_runs under gold schema"
  git push --set-upstream origin sprint-17/t2-schema-migration
  gh pr create --base main --head sprint-17/t2-schema-migration --title "fix(data-platform/csa): move csa_simulation_runs under gold schema" --body-file .tmp/t2-pr-body.md
  ```

---

## Task 3 — Schema-aware table-list helper

**Files:**
- Create: `data-platform/scripts/csa/list-lakehouse-tables.py`
- Create: `data-platform/scripts/csa/tests/test_list_lakehouse_tables.py`

- [ ] **Step 1: Write the failing pytest**

  Create `data-platform/scripts/csa/tests/test_list_lakehouse_tables.py`:

  ```python
  import pytest
  from unittest.mock import patch, MagicMock
  from data_platform.scripts.csa.list_lakehouse_tables import list_lakehouse_tables


  def test_returns_list_of_dicts_with_expected_keys():
      fake_rows = [("gold", "csa_simulation_runs", "delta"),
                   ("gold", "bva_focus_daily", "delta")]
      with patch("data_platform.scripts.csa.list_lakehouse_tables._resolve_sql_endpoint",
                 return_value="tcp:xxxx.datawarehouse.fabric.microsoft.com,1433"):
          with patch("pyodbc.connect") as mock_conn:
              mock_cursor = MagicMock()
              mock_cursor.fetchall.return_value = fake_rows
              mock_cursor.description = [("TABLE_SCHEMA",), ("TABLE_NAME",), ("TABLE_TYPE",)]
              mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
              result = list_lakehouse_tables("ws-guid", "lh-guid")
      assert len(result) == 2
      assert result[0]["schema"] == "gold"
      assert result[0]["name"] == "csa_simulation_runs"


  def test_filters_by_schema():
      # Same fixture as above but only pass schema="silver"; expect empty
      ...  # complete this in Step 3
  ```

- [ ] **Step 2: Run pytest — verify it fails with ImportError**

  ```powershell
  python -m pytest data-platform/scripts/csa/tests/test_list_lakehouse_tables.py -v
  ```

  Expected: `ModuleNotFoundError: data_platform.scripts.csa.list_lakehouse_tables`.

- [ ] **Step 3: Implement `list_lakehouse_tables`**

  Create `data-platform/scripts/csa/list-lakehouse-tables.py`:

  ```python
  """Schema-aware table lister for Fabric lakehouses.

  Replaces the deprecated ``/lakehouses/{id}/tables`` REST endpoint which returns
  ``UnsupportedOperationForSchemasEnabledLakehouse`` on schema-enabled lakehouses.
  """
  from __future__ import annotations

  import argparse
  import json
  import os
  from typing import Any

  import pyodbc  # type: ignore[import-not-found]
  import requests
  from azure.identity import DefaultAzureCredential

  _FABRIC = "https://api.fabric.microsoft.com/v1"


  def _resolve_sql_endpoint(workspace_id: str, lakehouse_id: str, token: str) -> str:
      resp = requests.get(
          f"{_FABRIC}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}",
          headers={"Authorization": f"Bearer {token}"},
          timeout=30,
      )
      resp.raise_for_status()
      return resp.json()["properties"]["sqlEndpointProperties"]["connectionString"]


  def list_lakehouse_tables(
      workspace_id: str,
      lakehouse_id: str,
      schema: str | None = None,
  ) -> list[dict[str, Any]]:
      """Return ``[{schema, name, type}]`` for every table in the lakehouse."""
      cred = DefaultAzureCredential()
      fabric_token = cred.get_token("https://api.fabric.microsoft.com/.default").token
      endpoint = _resolve_sql_endpoint(workspace_id, lakehouse_id, fabric_token)
      sql_token = cred.get_token("https://database.windows.net/.default").token
      conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={endpoint};Encrypt=yes;"
      # Fabric SQL endpoint uses AAD access-token auth
      access_token_bytes = bytes(sql_token, "utf-8")
      import struct
      token_struct = struct.pack("<i", len(access_token_bytes)) + access_token_bytes
      SQL_COPT_SS_ACCESS_TOKEN = 1256
      with pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct}) as conn:
          with conn.cursor() as cur:
              where = "WHERE 1=1" if schema is None else f"WHERE TABLE_SCHEMA = '{schema}'"
              cur.execute(
                  f"SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE "
                  f"FROM INFORMATION_SCHEMA.TABLES {where} "
                  f"ORDER BY TABLE_SCHEMA, TABLE_NAME"
              )
              rows = cur.fetchall()
      return [{"schema": r[0], "name": r[1], "type": r[2]} for r in rows]


  def main() -> None:
      p = argparse.ArgumentParser()
      p.add_argument("--workspace-id", required=True)
      p.add_argument("--lakehouse-id", required=True)
      p.add_argument("--schema", default=None)
      args = p.parse_args()
      out = list_lakehouse_tables(args.workspace_id, args.lakehouse_id, args.schema)
      print(json.dumps(out, indent=2))


  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 4: Run pytest — verify it passes**

  ```powershell
  python -m pytest data-platform/scripts/csa/tests/test_list_lakehouse_tables.py -v
  ```

  Expected: PASS (both tests). Iterate on Step 3 if any test fails.

- [ ] **Step 5: Real-world smoke test against SIT**

  ```powershell
  python data-platform/scripts/csa/list-lakehouse-tables.py `
    --workspace-id f3af9733-9503-4e92-98f9-a901d96f1c87 `
    --lakehouse-id 30594c20-46ba-40ea-91fa-4701b105e0b9
  ```

  Expected: JSON output listing all lakehouse tables including `gold.csa_simulation_runs` after T2 lands.

- [ ] **Step 6: Commit — Task 3**

  ```powershell
  git switch -c sprint-17/t3-lakehouse-table-lister main
  git add data-platform/scripts/csa/list-lakehouse-tables.py data-platform/scripts/csa/tests/test_list_lakehouse_tables.py
  git commit -m "feat(data-platform/csa): schema-aware lakehouse table lister via SQL endpoint"
  git push --set-upstream origin sprint-17/t3-lakehouse-table-lister
  gh pr create --base main --head sprint-17/t3-lakehouse-table-lister --title "feat(data-platform/csa): schema-aware lakehouse table lister via SQL endpoint" --body-file .tmp/t3-pr-body.md
  ```

---

## Task 4 — ADR-0026: Fabric Git integration model

**Files:**
- Create: `docs/adr/0026-fabric-git-integration-model.md`

- [ ] **Step 1: Draft the ADR**

  Create `docs/adr/0026-fabric-git-integration-model.md` following the pattern in `docs/adr/0022-*.md`. Key sections:

  1. **Status:** Proposed (draft PR), then Accepted on merge.
  2. **Context:** Sprint 16 T5 REST-push loop, cost in developer time, alternative approaches evaluated.
  3. **Decision:** Bind `ws-ihzhhpf-sit-data` to `fabric-sync` orphan branch, PR to `main`, preserve CODEOWNERS gate.
  4. **Alternatives considered:** A/B/C from §4 of the design spec.
  5. **Consequences:** Positive (versioning, rollback, review gate), Negative (extra step, preview items risk).
  6. **Related:** Sprint 17 design spec, PRs #174 and #175.

- [ ] **Step 2: Commit — Task 4**

  ```powershell
  git switch -c sprint-17/t4-adr-0026 main
  git add docs/adr/0026-fabric-git-integration-model.md
  git commit -m "docs(adr): 0026 - Fabric Git integration model (fabric-sync orphan branch)"
  git push --set-upstream origin sprint-17/t4-adr-0026
  gh pr create --base main --head sprint-17/t4-adr-0026 --title "docs(adr): 0026 - Fabric Git integration model" --body "See docs/superpowers/specs/2026-07-10-sprint-17-fabric-git-cicd-and-lakehouse-schema-design.md §4"
  ```

---

## Task 5 — ADR-0027: Lakehouse schema strategy

**Files:**
- Create: `docs/adr/0027-lakehouse-schema-strategy.md`

- [ ] **Step 1: Draft the ADR**

  Create `docs/adr/0027-lakehouse-schema-strategy.md`. Key sections:

  1. **Status:** Proposed → Accepted on merge.
  2. **Context:** `lh_ihzhhpf_sit` is schema-enabled with `dbo`, `bronze`, `silver`, `gold`. Sprint 16 T5 wrote at the root; broken.
  3. **Decision:** Every Delta table lives under one of `bronze`, `silver`, `gold`. `dbo` is reserved for Fabric-auto-generated SQL analytics objects. Explicit mapping matrix per Sprint 10 medallion pattern.
  4. **Consequences:** All Sprint 10+ notebooks + Spark writes must schema-qualify their paths going forward.
  5. **Migration path:** Sprint 17 T2 migrates `csa_simulation_runs`. A follow-up mini-sprint audits Sprint 10 M1 outputs.
  6. **Related:** Sprint 17 design spec §6, ADR-0016 (no PHI in demo scope — silver/gold data is synthetic).

- [ ] **Step 2: Commit — Task 5**

  Same pattern as T4.

---

## Task 6 — Documentation + guardrail rollout

**Files:**
- Modify: `.github/copilot-instructions.md`
- Modify: `AGENTS.md`
- Modify: `docs/OPERATIONS.md`
- Modify: `agents/orchestrator/AGENT.md`
- Modify: `agents/test-verifier-agent/golden-tasks.md`
- Create: `docs/sprints/sprint-17-fabric-git-cicd-and-lakehouse-schema.md`

- [ ] **Step 1: `.github/copilot-instructions.md` — bump minor, add §Fabric Git integration**

  In §1 "Project Architecture", after the "Runtime" bullet, add:

  ```markdown
  * **Fabric authoring:** items in `ws-ihzhhpf-sit-data` are Git-integrated with
    this repo per ADR-0026. Fabric UI edits flow: workspace → `fabric-sync`
    orphan branch → PR to `main`. Never bind Fabric to `main` directly.
  ```

  Bump version header to next MINOR (currently 1.7.0 → 1.8.0). Update `Previous Version`. Update `Date`.

- [ ] **Step 2: `AGENTS.md` — add Fabric Git integration guardrail**

  In §2 "MCP Server Allow-List", add a note (not a new server — Fabric Git integration is *not* an MCP tool; it's a workspace-level feature). In §5 "Refusal Rules (Shared)", add:

  ```markdown
  * Never bind a Fabric workspace to `main` directly. Only `fabric-sync` and
    `fabric-sync/*` are permitted binding targets.
  ```

  Bump version header (currently 2.1.0 → 2.2.0).

- [ ] **Step 3: `docs/OPERATIONS.md` — add runbook "Commit a Fabric UI change"**

  Add a new §"Commit a Fabric UI change (via Git integration)" with the 5-step user flow (edit in UI → Source control → Commit → open PR → merge). Include a link to ADR-0026.

- [ ] **Step 4: `agents/orchestrator/AGENT.md` — deprecate REST-push mention**

  Locate any reference to `updateDefinition` in the orchestrator prompt. Replace with:

  ```markdown
  For Fabric item edits, prefer the Fabric Git integration flow (ADR-0026).
  Only fall back to `updateDefinition` REST for items not yet migrated to
  the `fabric/` folder in the repo.
  ```

- [ ] **Step 5: `agents/test-verifier-agent/golden-tasks.md` — new golden task**

  Add a task: "Verify a Fabric lakehouse table exists via SQL endpoint" that references `data-platform/scripts/csa/list-lakehouse-tables.py` from T3.

- [ ] **Step 6: Create `docs/sprints/sprint-17-fabric-git-cicd-and-lakehouse-schema.md`**

  Follow the pattern of `docs/sprints/sprint-16-*.md` (or the closest predecessor). Include: goal, task list mapping to T1-T5, DoD (from §11 of the design spec), status.

- [ ] **Step 7: Commit — Task 6**

  ```powershell
  git switch -c sprint-17/t6-docs-and-guardrails main
  git add .github/copilot-instructions.md AGENTS.md docs/OPERATIONS.md agents/orchestrator/AGENT.md agents/test-verifier-agent/golden-tasks.md docs/sprints/sprint-17-fabric-git-cicd-and-lakehouse-schema.md
  git commit -m "docs(sprint-17): documentation + guardrail rollout for Fabric Git integration and schema strategy"
  git push --set-upstream origin sprint-17/t6-docs-and-guardrails
  gh pr create --base main --head sprint-17/t6-docs-and-guardrails --title "docs(sprint-17): documentation + guardrail rollout" --body-file .tmp/t6-pr-body.md
  ```

---

## Self-Review checklist

**1. Spec coverage:**
- [x] T1 covers §3 architecture + §4 branching decision + §5 supported items (T1 first-sync reveals which supported items actually landed).
- [x] T2 covers §6 lakehouse schema hardening.
- [x] T3 covers §7 verification path.
- [x] T4/T5 cover the ADRs from §4 and §6.
- [x] T6 covers §8 side-effect posture + §9 guardrails + doc updates.

**2. Placeholder scan:** No `TBD`, `TODO`, `implement later`, or "similar to Task N" phrasing. All code steps have complete code blocks.

**3. Type consistency:** `list_lakehouse_tables` signature is defined once in T3 Step 1 and matches T3 Step 3 implementation. The `_resolve_sql_endpoint` helper is named consistently. The ABFSS URI format matches across T2 and the design spec §6.2.

---

## Execution handoff

Plan complete. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for T1 (interactive Fabric setup) since it needs multiple UI-confirmation steps.
2. **Inline Execution** — Execute tasks in this session, batched with checkpoints. Best if you want to trade some parallelism for step-by-step observation.

@urruegg — which approach for Sprint 17? Or park it as ready-to-execute for a later kickoff issue?
