#!/usr/bin/env python3
"""Sprint 42 ST-3: the Container Apps Job entrypoint (replaces the placeholder
`mcr.microsoft.com/dotnet/samples:aspnetapp` image `caj-po-refresh-*` runs).

Wires the already-tested pipeline: `snapshot.snapshot_tree()` -> per-doc
`chunk_tag.chunk_document()` -> `publish.publish()` (PHI gate + GroundedChunk
mapping, already handles ordering/confidence) -> upload into the real search
index via a raw REST client (mirrors `search_client.py`'s injectable-transport
pattern and `create_search_index.py`'s document schema).

Document ids (Task 5 review finding): `citation.sourceRef` is `doc-path@commit`
and `commit` changes on every run (it's the freshness stamp for citations), so
using the full sourceRef as the index document id would make every daily
refresh insert brand-new documents instead of upserting the previous day's
version — the index would grow forever instead of tracking the corpus.
`document_id()` derives a stable id from the doc path (stripped of the
commit) + anchor instead, so a re-run overwrites the same row. When a chunk
has no anchor, falls back to a hash of its own text so multiple anchorless
chunks from the same doc don't collide into one id.

Note: `snapshot.snapshot_tree()` returns doc dicts keyed ``path`` (not
``source_path``) with no top-level ``date`` (the doc-level date, if any, is
extracted per-chunk from the text by `chunk_tag.chunk_document`). Class A
Task 6's fixtures use ``source_path``/``date`` keys directly, so
`build_grounded_chunks` accepts either key name to work with both the unit
fixtures and the real snapshot output.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

import chunk_tag
import publish
import snapshot

_API_VERSION = "2024-05-01-preview"
_SEARCH_SCOPE = "https://search.azure.com/.default"


def build_grounded_chunks(docs: list[dict], commit: str) -> list[dict]:
    """snapshot docs -> tagged chunks (all docs) -> published GroundedChunks."""
    tagged: list[dict] = []
    for doc in docs:
        source_path = doc.get("source_path", doc.get("path"))
        doc_chunks = chunk_tag.chunk_document(source_path, doc["text"], commit)
        for chunk in doc_chunks:
            chunk.setdefault("date", doc.get("date"))
        tagged.extend(doc_chunks)
    return publish.publish(tagged)


def document_id(citation: dict, text: str) -> str:
    """Stable index document id: doc path (commit-stripped) + anchor, falling
    back to a text hash when there's no anchor. See module docstring."""
    source_ref = citation["sourceRef"]
    doc_path = source_ref.rsplit("@", 1)[0] if "@" in source_ref else source_ref
    anchor = citation.get("anchor") or hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    raw_id = f"{doc_path}#{anchor}"
    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:32]


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential().get_token(_SEARCH_SCOPE).token


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def upload_chunks(
    endpoint: str,
    index_name: str,
    chunks: list[dict],
    token_provider=_default_token_provider,
    http_request=_default_http_request,
    timeout: int = 60,
) -> int:
    """Upload GroundedChunks into the index (nested citation.sourceRef/anchor
    shape, matching create_search_index.py's build_index_definition schema
    and search_client.py's query_corpus read-back)."""
    if not chunks:
        return 0
    documents = []
    for chunk in chunks:
        documents.append(
            {
                "@search.action": "mergeOrUpload",
                "id": document_id(chunk["citation"], chunk["text"]),
                "classId": chunk["classId"],
                "text": chunk["text"],
                "citation": {
                    "sourceRef": chunk["citation"]["sourceRef"],
                    "anchor": chunk["citation"].get("anchor", ""),
                },
                "asOf": chunk["asOf"],
                "liveness": chunk["liveness"],
                "status": chunk["status"],
                "confidence": chunk["confidence"],
                "language": chunk["language"],
            }
        )
    url = f"{endpoint.rstrip('/')}/indexes/{index_name}/docs/index?api-version={_API_VERSION}"
    headers = {"Authorization": f"Bearer {token_provider()}", "Content-Type": "application/json"}
    resp = http_request("POST", url, headers=headers, json={"value": documents}, timeout=timeout)
    resp.raise_for_status()
    return len(documents)


def main() -> int:
    repo_root = Path(os.environ.get("CORPUS_REPO_ROOT", "/app/repo"))
    commit = snapshot.get_commit(repo_root)
    docs = snapshot.snapshot_tree(repo_root, commit)
    chunks = build_grounded_chunks(docs, commit)

    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    index_name = os.environ["AZURE_SEARCH_INDEX"]
    count = upload_chunks(endpoint, index_name, chunks)
    print(f"refresh_job: uploaded {count} GroundedChunks (from {len(docs)} source docs) to {index_name}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
