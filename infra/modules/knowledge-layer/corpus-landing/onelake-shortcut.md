# OneLake Shortcut — Curavias Product Corpus Landing Zone

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-25 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | n/a |

## Purpose

Surface the WS-INF corpus landing container into the Fabric lakehouse Bronze
layer via a **OneLake shortcut**, so medallion notebooks (and any downstream
analytics over the PO Agent corpus) read the synthetic product documents without
copying bytes. Sprint 28 WS-INF (issue #377), grounding design **D2**.

> **Shortcuts are not Bicep-provisionable.** There is no ARM/Bicep resource type
> for a OneLake shortcut. It is created once per environment via the Fabric
> portal or the Fabric REST API (below) after the corpus storage account exists.
> This file is the operator procedure, not an infra module. The **primary**
> consumer of the corpus is the Azure AI Search knowledge source (see
> `../foundry-iq-knowledge-base/knowledge-base-rest.md`); this shortcut is the
> optional lakehouse view.

## Prerequisites

* WS-INF corpus landing deployed: storage account `stcorpus<suffix>` with the
  `landing` filesystem (see
  `infra/modules/knowledge-layer/corpus-landing/main.bicep`).
* A Fabric workspace + lakehouse (SIT workspace per the ADR-0034 evidence doc).
* The identity creating the shortcut holds **Storage Blob Data Reader** on the
  corpus storage account and **Contributor** on the Fabric workspace.
* All IDs below are placeholders — never commit real workspace/lakehouse IDs or
  connection IDs.

## Naming contract

| Element | Value |
| ------- | ----- |
| Shortcut path in lakehouse | `Files/landing/curavias-product-corpus/` |
| Target ADLS filesystem | `landing` |
| Target ADLS subpath | `curavias-product-corpus/` |
| Source folder convention | `curavias-product-corpus/<source>/<yyyy-mm-dd>/` |

where `<source>` is one of `prd`, `adr`, `design`, `runbook`.

## Option A — Fabric portal

1. Open the lakehouse, right-click **Files** -> **New shortcut**.
2. Choose **Azure Data Lake Storage Gen2**.
3. Set the DFS URL to the corpus-landing module output `dfsEndpoint`, e.g.
   `https://stcorpus<suffix>.dfs.core.windows.net/`.
4. Authenticate with **Organizational account** (or a workspace-identity
   connection); do not use an account key.
5. Set the sub path to `landing/curavias-product-corpus`.
6. Name the shortcut `curavias-product-corpus` so it lands at
   `Files/landing/curavias-product-corpus/`.

## Option B — Fabric REST API

`POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/shortcuts`

```json
{
  "path": "Files/landing",
  "name": "curavias-product-corpus",
  "target": {
    "adlsGen2": {
      "location": "https://stcorpus<suffix>.dfs.core.windows.net",
      "subpath": "/landing/curavias-product-corpus",
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
  check first with `GET .../shortcuts/Files%2Flanding/curavias-product-corpus`.

## Verify

1. In the lakehouse, confirm `Files/landing/curavias-product-corpus/` lists the
   `<source>/<yyyy-mm-dd>/` folders written by the corpus-refresh job.
2. Read one document from a notebook cell to confirm pass-through access:

   ```python
   df = spark.read.text(
       "Files/landing/curavias-product-corpus/prd/*/*.md"
   )
   df.limit(5).show()
   ```

## Rollback

Deleting the shortcut removes only the pointer, not the ADLS data. Portal:
right-click the shortcut -> **Delete**. REST:
`DELETE .../shortcuts/Files%2Flanding/curavias-product-corpus`.
