# OneLake Shortcut — Curavias Org/Skills Landing Zone

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | n/a |

## Purpose

Surface the WS-A1 ADLS Gen2 landing container into the Fabric lakehouse Bronze
layer via a **OneLake shortcut**, so the medallion notebooks read the synthetic
org/skills extracts without copying bytes. Sprint 23 WS-A2 (issue #255),
grounding design **D5**.

> **Shortcuts are not Bicep-provisionable.** There is no ARM/Bicep resource type
> for a OneLake shortcut. It is created once per environment via the Fabric
> portal or the Fabric REST API (below) after the WS-A1 storage account exists.
> This file is the operator procedure, not an infra module.

## Prerequisites

* WS-A1 deployed: storage account `stmasterdata<suffix>` with the `landing`
  filesystem (see `infra/modules/data-foundation/masterdata-landing/main.bicep`).
* A Fabric workspace + lakehouse (SIT workspace per the ADR-0034 evidence doc).
* The identity creating the shortcut holds **Storage Blob Data Reader** (or
  Contributor) on the landing storage account and **Contributor** on the Fabric
  workspace.
* All IDs below are placeholders — never commit real workspace/lakehouse IDs or
  connection IDs.

## Naming contract

| Element | Value |
| ------- | ----- |
| Shortcut path in lakehouse | `Files/landing/curavias-org-skills/` |
| Target ADLS filesystem | `landing` |
| Target ADLS subpath | `curavias-org-skills/` |
| Source folder convention | `curavias-org-skills/<source>/<yyyy-mm-dd>/` |

where `<source>` is one of `successfactors`, `lms`, `skills-manager`, `work-id`.

## Option A — Fabric portal

1. Open the lakehouse, right-click **Files** -> **New shortcut**.
2. Choose **Azure Data Lake Storage Gen2**.
3. Set the DFS URL to the WS-A1 module output `dfsEndpoint`, e.g.
   `https://stmasterdata<suffix>.dfs.core.windows.net/`.
4. Authenticate with **Organizational account** (or a workspace-identity
   connection); do not use an account key.
5. Set the sub path to `landing/curavias-org-skills`.
6. Name the shortcut `curavias-org-skills` so it lands at
   `Files/landing/curavias-org-skills/`.

## Option B — Fabric REST API

`POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/shortcuts`

```json
{
  "path": "Files/landing",
  "name": "curavias-org-skills",
  "target": {
    "adlsGen2": {
      "location": "https://stmasterdata<suffix>.dfs.core.windows.net",
      "subpath": "/landing/curavias-org-skills",
      "connectionId": "<connection-guid>"
    }
  }
}
```

* `{workspaceId}` / `{lakehouseId}` — from the target lakehouse (placeholders).
* `{connection-guid}` — a pre-created Fabric **connection** to the ADLS account
  using organizational-account or workspace-identity auth (never a key).
* Response `201 Created` returns the shortcut metadata. Re-`POST` with the same
  `path`+`name` returns `409 Conflict` — the operation is not idempotent, so
  check first with `GET .../shortcuts/Files%2Flanding/curavias-org-skills`.

## Verify

1. In the lakehouse, confirm `Files/landing/curavias-org-skills/` lists the
   `<source>/<yyyy-mm-dd>/` folders written by the upload runbook
   (`docs/runbooks/curavias-org-skills-upload.md`).
2. Read one CSV from a notebook cell to confirm pass-through access:

   ```python
   df = spark.read.option("header", True).csv(
       "Files/landing/curavias-org-skills/successfactors/*/dim_employee.csv"
   )
   df.limit(5).show()
   ```

## Rollback

Deleting the shortcut removes only the pointer, not the ADLS data. Portal:
right-click the shortcut -> **Delete**. REST:
`DELETE .../shortcuts/Files%2Flanding/curavias-org-skills`.
