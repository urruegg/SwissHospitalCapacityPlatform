import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from create_search_index import build_index_definition, put_index


class _FakeResponse:
    def __init__(self, status: int):
        self.status = status

    def raise_for_status(self):
        pass

    def json(self):
        return {}


def test_build_index_definition_mirrors_grounded_chunk_fields():
    definition = build_index_definition("idx-curavias-corpus-sit")
    field_names = {f["name"] for f in definition["fields"]}
    assert {"classId", "text", "citation", "asOf", "liveness", "status", "confidence", "language"} <= field_names
    key_fields = [f for f in definition["fields"] if f.get("key")]
    assert len(key_fields) == 1
    citation_field = next(f for f in definition["fields"] if f["name"] == "citation")
    assert citation_field["type"] == "Edm.ComplexType"
    citation_subfields = {f["name"] for f in citation_field["fields"]}
    assert {"sourceRef", "anchor"} <= citation_subfields


def test_put_index_calls_expected_url():
    calls = {}

    def fake_request(method, url, headers=None, json=None, timeout=None):
        calls["method"] = method
        calls["url"] = url
        calls["json"] = json
        return _FakeResponse(201)

    put_index(
        endpoint="https://srch-ihzhhpf-sit.search.windows.net",
        index_name="idx-curavias-corpus-sit",
        token_provider=lambda: "fake-token",
        http_request=fake_request,
    )
    assert calls["method"] == "PUT"
    assert calls["url"] == (
        "https://srch-ihzhhpf-sit.search.windows.net/indexes/idx-curavias-corpus-sit"
        "?api-version=2024-05-01-preview"
    )
