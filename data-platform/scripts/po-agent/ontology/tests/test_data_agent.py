"""WS-D Class D ontology: data-agent query-surface tests.

TDD step 1 (RED): every ``ontologyQuery()`` result must carry
``citation.conceptRef`` AND ``citation.goldBinding`` (Class D
grounding rule). Results missing either binding are dropped
(grounded refusal), the surface is read-only, and the Preview
per-capacity gate (#270) is feature-flagged.
"""

from pathlib import Path

import data_agent

REPO_ROOT = Path(__file__).resolve().parents[5]


class _FakeDataAgent:
    """Read-only fake of the da_hospital_capacity Fabric Data Agent."""

    def __init__(self, rows):
        self._rows = rows
        self.calls = []

    def ask(self, question):
        self.calls.append(("ask", question))
        return self._rows

    def __getattr__(self, name):
        raise AttributeError(f"read-only data agent: {name!r} not permitted")


_GROUNDED_ROW = {
    "answer": "Medicine A 72h forecast occupancy is grounded on hcp:OccupancyForecast.",
    "conceptRef": "hcp:OccupancyForecast",
    "goldBinding": "gold.dc_occupancy_forecast_v1",
    "confidence": 0.88,
    "language": "en",
}


def test_every_result_has_concept_and_gold_binding():
    agent = _FakeDataAgent([_GROUNDED_ROW])
    chunks = data_agent.ontologyQuery(
        "What is the Medicine A 72h forecast occupancy?",
        data_agent_client=agent,
        preview_enabled=True,
    )
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk["classId"] == "D"
    assert chunk["citation"]["conceptRef"] == "hcp:OccupancyForecast"
    assert chunk["citation"]["goldBinding"] == "gold.dc_occupancy_forecast_v1"


def test_result_missing_gold_binding_is_dropped():
    bad = dict(_GROUNDED_ROW)
    bad.pop("goldBinding")
    agent = _FakeDataAgent([_GROUNDED_ROW, bad])
    chunks = data_agent.ontologyQuery(
        "q", data_agent_client=agent, preview_enabled=True
    )
    # Only the fully-grounded row survives.
    assert len(chunks) == 1
    assert all(c["citation"].get("goldBinding") for c in chunks)


def test_preview_gate_disabled_returns_empty():
    agent = _FakeDataAgent([_GROUNDED_ROW])
    chunks = data_agent.ontologyQuery(
        "q", data_agent_client=agent, preview_enabled=False
    )
    assert chunks == []
