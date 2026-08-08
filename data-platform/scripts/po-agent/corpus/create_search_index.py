#!/usr/bin/env python3
"""Sprint 42 ST-3: create the Class A corpus search index (RBAC token, no keys).

Turns Step 1 of
``infra/modules/knowledge-layer/foundry-iq-knowledge-base/knowledge-base-rest.md``
into an idempotent script (a PUT with the same name updates in place) instead
of a manually-run curl command. Field schema mirrors the Class A subset of the
frozen GroundedChunk contract (``data/synthetic/schema/grounded-chunk-v1.schema.json``),
including a nested ``citation`` complex field (``sourceRef``/``anchor``),
matching what ``search_client.py``'s ``query_corpus`` already reads back
unchanged (``hit.get("citation") or {}``) — no changes needed to that
already-tested file.

Scope decision (explicit, not silent): this index is keyword-only for
Sprint 42. The runbook's vector/semantic fields (``text_vector``,
``vectorSearch``, ``semantic`` config) and the frozen contract's
``citation.conceptRef``/``citation.goldBinding`` (Class D only) are
deliberately deferred to a future sprint — vector search requires an
embedding model plus a re-ingestion pipeline that this sprint doesn't build,
even though the provisioned AI Search service already has
``semanticSearch: 'standard'`` enabled. ``query_corpus``'s current plain-text
search is compatible with this narrower, keyword-only schema.
"""
from __future__ import annotations

import os
from typing import Any

_API_VERSION = "2024-05-01-preview"
_SEARCH_SCOPE = "https://search.azure.com/.default"


def build_index_definition(index_name: str) -> dict[str, Any]:
    return {
        "name": index_name,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "classId", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "text", "type": "Edm.String", "searchable": True},
            {
                "name": "citation",
                "type": "Edm.ComplexType",
                "fields": [
                    {"name": "sourceRef", "type": "Edm.String", "filterable": True, "retrievable": True},
                    {"name": "anchor", "type": "Edm.String", "retrievable": True},
                ],
            },
            {"name": "asOf", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True},
            {"name": "liveness", "type": "Edm.String", "filterable": True},
            {"name": "status", "type": "Edm.String", "filterable": True},
            {"name": "confidence", "type": "Edm.Double", "filterable": True, "sortable": True},
            {"name": "language", "type": "Edm.String", "filterable": True, "facetable": True},
        ],
    }


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential().get_token(_SEARCH_SCOPE).token


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def put_index(
    endpoint: str,
    index_name: str,
    token_provider=_default_token_provider,
    http_request=_default_http_request,
    timeout: int = 30,
) -> None:
    """Create (or update, idempotent) the corpus search index."""
    url = f"{endpoint.rstrip('/')}/indexes/{index_name}?api-version={_API_VERSION}"
    headers = {
        "Authorization": f"Bearer {token_provider()}",
        "Content-Type": "application/json",
    }
    resp = http_request("PUT", url, headers=headers, json=build_index_definition(index_name), timeout=timeout)
    resp.raise_for_status()


def main() -> int:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    index_name = os.environ["AZURE_SEARCH_INDEX"]
    put_index(endpoint, index_name)
    print(f"create_search_index: PUT {index_name} on {endpoint} — ok")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
