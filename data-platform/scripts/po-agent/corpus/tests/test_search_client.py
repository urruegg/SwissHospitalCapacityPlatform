"""Sprint 41 WS-RET Task RET.1: Class A `query_corpus` mapping + schema conformance.

The plan's sample flattened `sourceRef` at the chunk top level (and omitted
`asOf`/`liveness`). Reading `corpus/publish.py`'s `to_grounded_chunk` and the
frozen contract schema (`data/synthetic/schema/grounded-chunk-v1.schema.json`,
`additionalProperties: false` at both the top level and inside `citation`)
shows the real shape nests `sourceRef`/`anchor` under `citation` and requires
`asOf`/`liveness` too - this test uses the corrected shape and additionally
validates the schema directly so a future regression is caught here, not only
downstream in the citation layer.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from search_client import query_corpus

REPO_ROOT = Path(__file__).resolve().parents[5]
SCHEMA_PATH = REPO_ROOT / "data" / "synthetic" / "schema" / "grounded-chunk-v1.schema.json"

jsonschema = pytest.importorskip("jsonschema")


class _FakeSearchClient:
    """Fake mirroring the real Azure AI Search index fields (the index
    mirrors the GroundedChunk contract 1:1, per
    infra/modules/knowledge-layer/foundry-iq-knowledge-base/knowledge-base-rest.md).
    """

    def __init__(self, hits):
        self._hits = hits
        self.calls = []

    def search(self, search_text, top=5):
        self.calls.append((search_text, top))
        return self._hits


def test_query_corpus_maps_search_hits_to_grounded_chunks():
    hits = [
        {
            "text": "The MVP targets patient-flow optimisation.",
            "citation": {"sourceRef": "docs/PRD.md@abc1234", "anchor": "vision"},
            "asOf": "2026-07-25T00:00:00Z",
            "status": "verified",
            "confidence": 0.9,
            "language": "en",
        }
    ]
    client = _FakeSearchClient(hits)
    chunks = query_corpus("strategic value", client=client)

    assert chunks[0]["classId"] == "A"
    assert chunks[0]["citation"]["sourceRef"] == "docs/PRD.md@abc1234"
    assert chunks[0]["citation"]["anchor"] == "vision"
    assert chunks[0]["liveness"] == "live"
    assert client.calls == [("strategic value", 5)]


def test_query_corpus_drops_hits_missing_source_ref():
    hits = [{"text": "no citation at all", "confidence": 0.9}]
    assert query_corpus("x", client=_FakeSearchClient(hits)) == []


def test_query_corpus_output_conforms_to_grounded_chunk_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)
    hits = [
        {
            "text": "Cited answer.",
            "citation": {"sourceRef": "docs/ARCHITECTURE.md@deadbee"},
            "asOf": "2026-07-25T00:00:00Z",
            "confidence": 0.8,
            "status": "verified",
            "language": "en",
        }
    ]
    chunks = query_corpus("x", client=_FakeSearchClient(hits))
    errors = sorted(validator.iter_errors(chunks[0]), key=str)
    assert not errors, [e.message for e in errors]
