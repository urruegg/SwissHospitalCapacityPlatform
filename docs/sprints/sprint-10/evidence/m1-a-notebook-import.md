# Sprint 10 M1-A — Notebook Import Evidence

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-08 |
| **Author** | Urs Rüegg |
| **Status** | PASS |
| **Previous Version** | n/a (initial) |

**Milestone:** M1 of the [Sprint 10 completion strategy](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md).
**Task:** M1-A — Slice of S10.2 (eventstream notebook import into `ws-ihzhhpf-sit-data`).
**Plan reference:** [M1 plan Task 1](../../../superpowers/plans/2026-07-08-sprint-10-m1-vertical-slice-plan.md#task-1--s102-slice-notebook-import-pr-m1-a).

## Outcome

**PASS.** All 3 eventstream notebooks imported (updated in-place — they were already present in the workspace from Sprint 09 T2.2 work) and verified via Fabric REST `GET /v1/workspaces/{ws}/notebooks`.

## Branch A/B classification

**Branch A** — the 3 notebooks already existed in the repo at `data-platform/notebooks/eventstream/`:

| File | Size on disk |
| ---- | ------------ |
| `01_bronze_eventstream.ipynb` | 14 455 bytes |
| `02_silver_eventstream.ipynb` | 25 608 bytes |
| `03_gold_eventstream.ipynb` | 10 651 bytes |

No authoring required. The M1 plan's Branch B (author minimal notebooks first) did not fire.

## Import evidence

Command run:

```powershell
python data-platform/scripts/import_notebooks.py `
  f3af9733-9503-4e92-98f9-a901d96f1c87 `
  "data-platform/notebooks/eventstream/*.ipynb" `
  --lakehouse-id 30594c20-46ba-40ea-91fa-4701b105e0b9 `
  --lakehouse-name lh_ihzhhpf_sit
```

Script output (2026-07-08 approx 09:38 UTC):

```text
Importing 3 notebook(s) to workspace f3af9733-9503-4e92-98f9-a901d96f1c87 (7 existing) ...
  updated 01_bronze_eventstream (id=5aaadd07-e39b-4ee6-aca3-a53a7ca39d27)
  updated 02_silver_eventstream (id=66f7fa07-378e-4238-ae44-7c14b8668c48)
  updated 03_gold_eventstream (id=be8e62cd-dc33-48ba-bca2-b267364c66fb)
Done.
```

`updated` (not `created`) — Sprint 09 T2.2 had already imported earlier scaffold versions of these notebooks. The M1-A import brought the workspace copies in sync with the current repo versions.

Dry-run run before the real import (steps preserved for audit):

```text
Importing 3 notebook(s) to workspace f3af9733-9503-4e92-98f9-a901d96f1c87 (0 existing) ...
[DRY-RUN] Would create 01_bronze_eventstream (19288 b64 chars)
[DRY-RUN] Would create 02_silver_eventstream (33932 b64 chars)
[DRY-RUN] Would create 03_gold_eventstream (14304 b64 chars)
Done.
```

The dry-run reported `(0 existing)` because it does not call the workspace-list endpoint; the real run correctly detected the 7 pre-existing notebooks.

## Notebook GUIDs (captured for downstream tasks)

| Notebook | GUID |
| -------- | ---- |
| `01_bronze_eventstream` | `5aaadd07-e39b-4ee6-aca3-a53a7ca39d27` |
| `02_silver_eventstream` | `66f7fa07-378e-4238-ae44-7c14b8668c48` |
| `03_gold_eventstream` | `be8e62cd-dc33-48ba-bca2-b267364c66fb` |

These GUIDs feed into M1-B Task 2 Step 4 (`run_notebooks.py f3af9733-... 01_bronze_eventstream 02_silver_eventstream 03_gold_eventstream`).

## Verification query

```powershell
$token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/notebooks" -Headers @{Authorization="Bearer $token"} `
  | Select-Object -ExpandProperty value `
  | Where-Object { $_.displayName -match 'eventstream' } `
  | Select-Object displayName, id, description
```

Result:

```text
displayName : 01_bronze_eventstream
id          : 5aaadd07-e39b-4ee6-aca3-a53a7ca39d27
description : Imported from data-platform/notebooks/eventstream/01_bronze_eventstream.ipynb

displayName : 02_silver_eventstream
id          : 66f7fa07-378e-4238-ae44-7c14b8668c48
description : Imported from data-platform/notebooks/eventstream/02_silver_eventstream.ipynb

displayName : 03_gold_eventstream
id          : be8e62cd-dc33-48ba-bca2-b267364c66fb
description : Imported from data-platform/notebooks/eventstream/03_gold_eventstream.ipynb

---Total notebooks in workspace: 7
```

## Sprint 10 M1 Task 1 exit criteria

- [x] All 3 eventstream notebooks visible via `GET /v1/workspaces/{ws}/notebooks`
- [x] Notebook GUIDs captured for M1-B (`run_notebooks.py` input)
- [x] Branch A/B classification recorded (Branch A — notebooks already in repo)
- [x] Evidence report v1.0.0 committed alongside the PR

## Rollback

If M1-B or downstream tasks reveal a notebook issue, revert this update by re-importing an earlier version from `git log data-platform/notebooks/eventstream/` and rerunning `import_notebooks.py`. Full delete only if we abandon the whole M1 vertical slice:

```powershell
$ids = @('5aaadd07-e39b-4ee6-aca3-a53a7ca39d27','66f7fa07-378e-4238-ae44-7c14b8668c48','be8e62cd-dc33-48ba-bca2-b267364c66fb')
foreach ($id in $ids) {
  Invoke-RestMethod -Method DELETE -Uri "https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/notebooks/$id" -Headers @{Authorization="Bearer $token"}
}
```

## References

- [Sprint 10 M1 plan Task 1](../../../superpowers/plans/2026-07-08-sprint-10-m1-vertical-slice-plan.md#task-1--s102-slice-notebook-import-pr-m1-a)
- [Sprint 10 completion strategy §3 M1](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md#m1--vertical-slice-e2e)
- [Sprint 10 charter S10.2 row](../../sprint-10-e2e-pipeline-and-dashboard-completion.md#5-deliverables-mapped-from-retrospective-5)
- [`data-platform/scripts/import_notebooks.py`](../../../../data-platform/scripts/import_notebooks.py)
- [Sprint 09 v2 T2.2](../../sprint-09-master-data-simulation-and-capacity-dashboard.md) — original notebook scaffold that this M1-A brought in sync
