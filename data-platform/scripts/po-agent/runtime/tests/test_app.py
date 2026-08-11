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


# ---------------------------------------------------------------------------
# Sprint 44 follow-up: hospital-delta what-if (bva_fanout wiring)
# ---------------------------------------------------------------------------

def _hospital_delta() -> dict:
    return {
        "hospitalName": "Hopital de Fribourg",
        "archetype": "acute",
        "beds": 200,
        "occupancyTarget": 0.85,
        "onboardingScope": "full",
    }


def test_answer_accepts_hospital_delta_without_breaking_existing_callers(monkeypatch):
    """Backward compatibility: existing callers (no hospitalDelta) are unaffected."""
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


def test_answer_with_hospital_delta_financial_question_cites_real_bva_numbers(monkeypatch):
    monkeypatch.setattr("app.get_tools", lambda: {})
    resp = client.post(
        "/answer",
        json={
            "question": "What is the ROI and payback in CHF?",
            "caller": {"persona": "CFO", "tier": "internal"},
            "language": "en",
            "hospitalDelta": _hospital_delta(),
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is False
    assert "Hopital de Fribourg" in body["read"]
    assert "ROI" in body["read"]
    assert any("docs/BVA.md ROM baseline" in c and "archetype:acute" in c for c in body["citations"])


def test_answer_with_hospital_delta_onboarding_question_no_verdict_degrades_honestly(monkeypatch):
    """Never fabricates a poVerdict: no verdict supplied -> transparent partial."""
    monkeypatch.setattr("app.get_tools", lambda: {})
    resp = client.post(
        "/answer",
        json={
            "question": "Should we onboard this hospital based on product fit and the BVA?",
            "caller": {"persona": "CFO", "tier": "internal"},
            "language": "en",
            "hospitalDelta": _hospital_delta(),
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is True
    assert "go" not in body["read"].lower().split()
    assert "no-go" not in body["read"].lower()


def test_answer_with_hospital_delta_onboarding_question_and_supplied_verdict_composes(monkeypatch):
    monkeypatch.setattr("app.get_tools", lambda: {})
    resp = client.post(
        "/answer",
        json={
            "question": "Should we onboard this hospital based on product fit and the BVA?",
            "caller": {"persona": "CFO", "tier": "internal"},
            "language": "en",
            "hospitalDelta": _hospital_delta(),
            "poVerdict": {
                "verdict": "go",
                "rationale": "roadmap-aligned acute onboarding candidate",
                "citations": ["docs/PRD.md#fr-bva-003"],
                "chunks": [
                    {
                        "classId": "A",
                        "text": "The hospital is a roadmap-aligned acute onboarding candidate.",
                        "citation": {"sourceRef": "docs/PRD.md#fr-bva-003"},
                        "asOf": "2026-07-28T00:00:00Z",
                        "liveness": "snapshot",
                        "status": "verified",
                        "confidence": 0.9,
                        "language": "en",
                    }
                ],
            },
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is False
    assert "Verdict: go" in body["read"]
    assert "docs/PRD.md#fr-bva-003" in body["citations"]


def test_answer_with_invalid_hospital_delta_degrades_instead_of_crashing(monkeypatch):
    monkeypatch.setattr("app.get_tools", lambda: {})
    bad_delta = _hospital_delta()
    bad_delta["archetype"] = "not-a-real-archetype"
    resp = client.post(
        "/answer",
        json={
            "question": "What is the ROI in CHF?",
            "caller": {"persona": "CFO", "tier": "internal"},
            "language": "en",
            "hospitalDelta": bad_delta,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["refused"] is True
