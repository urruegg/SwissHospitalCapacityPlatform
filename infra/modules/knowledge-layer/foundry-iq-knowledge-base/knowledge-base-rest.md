# Foundry IQ Knowledge Base — Curavias Product Owner Agent (domain #1)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-25 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | n/a |

## Purpose

Create the **Foundry IQ knowledge source + knowledge base** that the Curavias
Product Owner Agent (Foundry IQ **domain #1**, ADR-0043) retrieves over for its
Class A corpus answers. This is the shared Knowledge Layer substrate: additional
domains attach as new knowledge sources against the same Azure AI Search service.
Sprint 28 WS-INF (issue #377), grounding design **D2**.

> **The knowledge base is not Bicep-provisionable.** There is no ARM/Bicep
> resource type for a Foundry IQ knowledge source or knowledge base. They are
> created over the GA Azure AI Search service
> (`infra/modules/knowledge-layer/ai-search/main.bicep`) via the Search
> data-plane REST API and the Foundry IQ portal, after the Search service and the
> corpus landing storage exist. This file is the operator procedure, not an infra
> module; the companion `main.bicep` only records the naming + version contract.

## Prerequisites

* WS-INF AI Search deployed: service `srch-ihzhhpf-<env>` with `disableLocalAuth:
  true` (see `../ai-search/main.bicep`). RBAC-only — no admin/query keys exist.
* WS-INF corpus landing deployed: ADLS Gen2 `stcorpus<suffix>` with the `landing`
  filesystem and the `curavias-product-corpus/` folder convention (see
  `../corpus-landing/main.bicep`).
* The identity creating the knowledge source holds **Search Service Contributor**
  plus **Search Index Data Contributor** on the Search service, and the Search
  service system-assigned MI holds **Storage Blob Data Reader** on the corpus
  storage (granted by the corpus-landing module when `searchPrincipalId` is
  passed).
* Pinned data-plane api-version: **`2024-05-01-preview`** (from the ai-search
  module output `pinnedSearchRestApiVersion`). Do not drift from this value
  without a reviewed PR — some agentic-retrieval surfaces are Preview (design R2).
* All IDs below are placeholders — never commit real service/tenant/index IDs.

## Naming contract

| Element | Value |
| ------- | ----- |
| Search service | `srch-ihzhhpf-<env>` |
| Search index | `idx-curavias-corpus-<env>` |
| Knowledge source | `ks-curavias-corpus-<env>` |
| Knowledge base | `kb-curavias-po-<env>` |
| Corpus source path | `landing/curavias-product-corpus/<source>/<yyyy-mm-dd>/` |

where `<env>` is `sit` or `prod` and `<source>` is one of `prd`, `adr`,
`design`, `runbook`.

## Step 1 — Create the search index (data plane, RBAC token)

Authenticate with an Entra token for `https://search.azure.com` (no api key):

```bash
TOKEN=$(az account get-access-token --resource https://search.azure.com --query accessToken -o tsv)
```

`PUT https://srch-ihzhhpf-<env>.search.windows.net/indexes/idx-curavias-corpus-<env>?api-version=2024-05-01-preview`

Body defines a hybrid vector + keyword index whose fields mirror the frozen
`GroundedChunk` contract (`docs/superpowers/specs/2026-07-25-sprint-28-po-agent-contracts.md`):
`classId`, `text` (searchable), a `text_vector` (vector), and the `citation`
sub-fields (`sourceRef`, `anchor`, `conceptRef`, `goldBinding`), plus `asOf`,
`liveness`, `status`, `language`. Include a `vectorSearch` profile and a
`semantic` configuration so hybrid + semantic ranking is available.

## Step 2 — Create the knowledge source over the corpus

`PUT .../knowledgeSources/ks-curavias-corpus-<env>?api-version=2024-05-01-preview`

Point the knowledge source at the corpus landing storage using the Search
service **managed identity** (never a key):

```json
{
  "name": "ks-curavias-corpus-<env>",
  "kind": "azureBlob",
  "azureBlobParameters": {
    "connectionString": "ResourceId=/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/stcorpus<suffix>;",
    "containerName": "landing",
    "folderPath": "curavias-product-corpus",
    "identity": { "kind": "systemAssigned" }
  }
}
```

## Step 3 — Create the knowledge base (domain #1)

`PUT .../knowledgeBases/kb-curavias-po-<env>?api-version=2024-05-01-preview`

Bind the knowledge base to `ks-curavias-corpus-<env>` and the index
`idx-curavias-corpus-<env>`. This is the object the PO Agent domain #1 references
for Class A retrieval. Additional Foundry IQ domains attach further knowledge
sources to the **same** knowledge base / Search service — that is the shared
Knowledge Layer.

## Verify

1. `GET .../knowledgeBases/kb-curavias-po-<env>?api-version=2024-05-01-preview`
   returns `200` with the bound knowledge source.
2. Run a retrieval probe and confirm each returned chunk carries a `citation`
   with a non-empty `sourceRef` (the Class A grounding invariant, FR-POA-002).

## Rollback

`DELETE` the knowledge base, then the knowledge source, then the index (reverse
order). None of these delete the corpus bytes in ADLS. Deleting the Search
service itself is a separate `az deployment`/portal action gated by
`approved-to-apply`.
