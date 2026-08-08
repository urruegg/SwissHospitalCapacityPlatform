"""Sprint 41 WS-SVC Task SVC.1: FastAPI wrapper contract tests.

Adapted from the plan sample: the fake tool chunks below use the real
``GroundedChunk`` nested ``citation.sourceRef`` shape (see
``orchestrator._is_cited``), not a flat ``sourceRef`` field, since
``orchestrator.answer()`` only recognises the nested form.
"""

from fastapi.testclient import TestClient

from app import app, get_tools

client = TestClient(app)


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_answer_maps_orchestrator_output_to_grounded_reco(monkeypatch):
    def fake_tools():
        return {
            "A": lambda q: [
                {
                    "classId": "A",
                    "text": "The MVP targets patient-flow optimisation.",
                    "citation": {"sourceRef": "docs/PRD.md#vision"},
                    "confidence": 0.9,
                    "status": "verified",
                    "language": "en",
                }
            ]
        }

    monkeypatch.setattr("app.get_tools", fake_tools)
    resp = client.post(
        "/answer",
        json={
            "question": "What is the strategic value case?",
            "caller": {"persona": "CEO", "tier": "internal"},
            "language": "en",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["provenance"] == "live"
    assert body["citations"], "must carry at least one citation"
    assert body["refused"] is False


def test_answer_refuses_without_grounded_chunks(monkeypatch):
    monkeypatch.setattr("app.get_tools", lambda: {"A": lambda q: []})
    resp = client.post(
        "/answer",
        json={
            "question": "Anything ungrounded",
            "caller": {"persona": "CFO", "tier": "internal"},
            "language": "en",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["refused"] is True
