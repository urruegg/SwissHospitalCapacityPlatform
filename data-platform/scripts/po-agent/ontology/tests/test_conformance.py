"""WS-D Class D ontology: read-only + snapshot + schema conformance."""

import json
from pathlib import Path

import pytest

import data_agent

REPO_ROOT = Path(__file__).resolve().parents[5]
SCHEMA_PATH = (
    REPO_ROOT / "data" / "synthetic" / "schema" / "grounded-chunk-v1.schema.json"
)

_ROW = {
    "answer": "Bed occupancy concept grounded to the gold binding.",
    "conceptRef": "hcp:BedOccupancy",
    "goldBinding": "gold.dc_bed_occupancy_v1",
    "confidence": 0.9,
    "language": "en",
}


class _FakeDataAgent:
    def __init__(self, rows):
        self._rows = rows
        self.calls = []

    def ask(self, question):
        self.calls.append(("ask", question))
        return self._rows

    def __getattr__(self, name):
        raise AttributeError(f"read-only data agent: {name!r} not permitted")


class _BoomDataAgent:
    def ask(self, question):
        raise RuntimeError("data agent unreachable")

    def __getattr__(self, name):
        raise AttributeError(name)


def test_surface_is_read_only():
    agent = _FakeDataAgent([_ROW])
    data_agent.ontologyQuery("q", data_agent_client=agent, preview_enabled=True)
    assert agent.calls == [("ask", "q")]


def test_agent_failure_returns_empty():
    chunks = data_agent.ontologyQuery(
        "q", data_agent_client=_BoomDataAgent(), preview_enabled=True
    )
    assert chunks == []


def test_stale_row_degrades_to_snapshot():
    stale = dict(_ROW, stale=True)
    chunks = data_agent.ontologyQuery(
        "q", data_agent_client=_FakeDataAgent([stale]), preview_enabled=True
    )
    assert len(chunks) == 1
    assert chunks[0]["liveness"] == "snapshot"
    assert chunks[0]["status"] == "partial"
    # Snapshot still carries the concept + gold binding (Class D rule holds).
    assert chunks[0]["citation"]["conceptRef"] == "hcp:BedOccupancy"
    assert chunks[0]["citation"]["goldBinding"] == "gold.dc_bed_occupancy_v1"


def test_grounded_chunk_conforms_to_schema():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)

    live = data_agent.ontologyQuery(
        "q", data_agent_client=_FakeDataAgent([_ROW]), preview_enabled=True
    )[0]
    snap = data_agent.ontologyQuery(
        "q", data_agent_client=_FakeDataAgent([dict(_ROW, stale=True)]),
        preview_enabled=True,
    )[0]
    for chunk in (live, snap):
        errors = sorted(validator.iter_errors(chunk), key=str)
        assert not errors, [e.message for e in errors]
