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


def test_resolve_repo_root_falls_back_to_dev_tree_layout():
    import app as app_module

    # No /app/repo/docs/BVA.md mirror in the dev checkout -> falls back to
    # the dev-tree formula (three parents above po-agent/), which must
    # resolve to a real repo root that actually has docs/BVA.md.
    repo_root = app_module._resolve_repo_root()
    assert (repo_root / "docs" / "BVA.md").is_file()


def test_resolve_repo_root_prefers_the_container_mirror_when_present(monkeypatch, tmp_path):
    import app as app_module

    fake_app_dir = tmp_path / "app"
    (fake_app_dir / "repo" / "docs").mkdir(parents=True)
    (fake_app_dir / "repo" / "docs" / "BVA.md").write_text("stub", encoding="utf-8")
    monkeypatch.setattr(app_module, "_APP_DIR", fake_app_dir)

    repo_root = app_module._resolve_repo_root()
    assert repo_root == fake_app_dir / "repo"
