"""Sprint 41 WS-RET Task RET.1: real Azure AI Search client for Class A corpus queries.

Verified against the real code before writing (per the task's diligence
requirement): `corpus/publish.py`'s `to_grounded_chunk` and the frozen
`data/synthetic/schema/grounded-chunk-v1.schema.json` (``additionalProperties:
false``) show the GroundedChunk shape nests ``sourceRef``/``anchor`` under
``citation`` and always requires ``asOf``/``liveness`` - the plan's sample
(flat ``sourceRef``, no ``asOf``/``liveness``) would fail schema conformance.
The Azure AI Search index mirrors this contract field-for-field (see
``infra/modules/knowledge-layer/foundry-iq-knowledge-base/knowledge-base-rest.md``),
so ``query_corpus`` maps a search hit almost 1:1 onto the eight allowed
GroundedChunk fields, dropping anything else the SDK/REST layer attaches
(e.g. ``@search.score``) and dropping any hit missing a non-empty
``citation.sourceRef`` (grounded refusal for that row, never a fabricated
citation - FR-POA-002).

``azure-search-documents`` is not an installed dependency in this environment
(verified: ``ModuleNotFoundError: No module named 'azure.search'``), so the
production client is a raw REST call against the pinned data-plane
api-version (``2024-05-01-preview``, per the knowledge-base-rest.md naming
contract) using ``DefaultAzureCredential`` (the index has
``disableLocalAuth: true`` - RBAC only, no admin/query keys). This mirrors
the injectable-transport pattern ``ontology/data_agent.py``'s
``_RawFabricDataAgentClient`` already established for this repo.
"""
from __future__ import annotations

import os
from typing import Any, Protocol

_API_VERSION = "2024-05-01-preview"
_SEARCH_SCOPE = "https://search.azure.com/.default"


class SearchClientProtocol(Protocol):
    def search(self, search_text: str, top: int = 5) -> Any: ...


def query_corpus(question: str, client: SearchClientProtocol, top: int = 5) -> list[dict[str, Any]]:
    """Query the corpus index and map hits onto the frozen GroundedChunk shape (classId A)."""

    hits = client.search(question, top=top)
    chunks: list[dict[str, Any]] = []
    for hit in hits or []:
        citation_raw = hit.get("citation") or {}
        source_ref = str(citation_raw.get("sourceRef") or "").strip()
        if not source_ref:
            continue  # ungrounded row: dropped, never fabricated (FR-POA-002)
        citation: dict[str, str] = {"sourceRef": source_ref}
        anchor = citation_raw.get("anchor")
        if anchor:
            citation["anchor"] = str(anchor)
        chunks.append(
            {
                "classId": "A",
                "text": str(hit.get("text", "")),
                "citation": citation,
                "asOf": str(hit.get("asOf", "")),
                "liveness": "live",
                "status": str(hit.get("status", "verified")),
                "confidence": float(hit.get("confidence", 0.7)),
                "language": str(hit.get("language", "en")),
            }
        )
    return chunks


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential().get_token(_SEARCH_SCOPE).token


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


class _RawSearchIndexClient:
    """Real Azure AI Search data-plane REST client (RBAC token, no keys).

    Reimplements (does not import) the same injectable ``token_provider`` /
    ``http_request`` seam ``ontology/data_agent.py``'s
    ``_RawFabricDataAgentClient`` already established for this repo.
    """

    def __init__(
        self,
        endpoint: str,
        index_name: str,
        token_provider: Any,
        http_request: Any = None,
        timeout: int = 10,
        api_version: str = _API_VERSION,
    ) -> None:
        self._endpoint = (endpoint or "").rstrip("/")
        self._index_name = index_name
        self._token_provider = token_provider
        self._http_request = http_request or _default_http_request
        self._timeout = timeout
        self._api_version = api_version

    def search(self, search_text: str, top: int = 5) -> list[dict[str, Any]]:
        url = f"{self._endpoint}/indexes/{self._index_name}/docs/search?api-version={self._api_version}"
        headers = {
            "Authorization": f"Bearer {self._token_provider()}",
            "Content-Type": "application/json",
        }
        resp = self._http_request(
            "POST", url, headers=headers, json={"search": search_text, "top": top}, timeout=self._timeout
        )
        resp.raise_for_status()
        return list(resp.json().get("value", []))


def build_production_client() -> Any:
    """Build the real Class A corpus search client (RBAC token, no keys).

    Reads ``AZURE_SEARCH_ENDPOINT`` (e.g.
    ``https://srch-ihzhhpf-sit.search.windows.net``) and
    ``AZURE_SEARCH_INDEX`` (e.g. ``idx-curavias-corpus-sit``) - naming
    contract in
    ``infra/modules/knowledge-layer/foundry-iq-knowledge-base/knowledge-base-rest.md``.
    """
    return _RawSearchIndexClient(
        endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT", ""),
        index_name=os.environ.get("AZURE_SEARCH_INDEX", ""),
        token_provider=_default_token_provider,
    )
