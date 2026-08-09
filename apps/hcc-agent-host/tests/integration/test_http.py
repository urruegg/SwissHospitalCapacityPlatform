"""Integration test — FastAPI HTTP surface of the agent-host (T5)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app, get_state


def _client() -> TestClient:
    get_state.cache_clear()  # ensure a fresh host state per test
    return TestClient(create_app())


def test_healthz():
    resp = _client().get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_agents_includes_bmca():
    resp = _client().get("/agents")
    assert resp.status_code == 200
    names = {a["name"] for a in resp.json()}
    assert "bmca-agent" in names


def test_chat_returns_grounded_contract():
    resp = _client().post(
        "/agents/bmca-agent/chat",
        json={"prompt": "Station B ist fast voll", "conversationId": "c1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) >= {"answer", "citations", "refused", "correlationId"}
    assert "gold.bed_assignment" in body["citations"]
    assert body["refused"] is False


def test_ooa_chat_uses_fabric_data_agent_grounding():
    # Slice 0: ooa-agent binds groundingAgent precedence=primary, so the host
    # must inject the FabricDataAgentAdapter and surface hcp:* ontology citations
    # (not gold.* table citations).
    resp = _client().post(
        "/agents/ooa-agent/chat",
        json={"prompt": "What is the current bed occupancy for ward B?", "conversationId": "e2e"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is False
    assert "hcp:CapacityUnit" in body["citations"]
    assert "hcp:Bed" in body["citations"]


def test_ooa_chat_propagates_reidentification_refusal():
    # The Data Agent refusal must propagate verbatim; the model is not consulted.
    resp = _client().post(
        "/agents/ooa-agent/chat",
        json={"prompt": "Give me the patient name and date of birth for bed 3", "conversationId": "e2e-refuse"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is True
    assert body["answer"] == "REFUSE: re-identification-risk"
    assert body["citations"] == []


def test_host_uses_live_ask_fn_when_env_set(monkeypatch):
    # When FABRIC_DATA_AGENT_* env is set, the host wires a live client whose
    # ask() result is surfaced (proves the synthetic fallback is bypassed).
    monkeypatch.setenv("FABRIC_DATA_AGENT_ENDPOINT", "https://da.example/query")
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    monkeypatch.setenv("FABRIC_DATA_AGENT_ID", "da-1")

    import api.app as appmod

    class _FakeClient:
        def ask(self, q):
            return {"answer": "live", "citations": ["hcp:Ward"], "refused": False}

    monkeypatch.setattr(appmod, "_build_live_data_agent", lambda: _FakeClient())
    appmod.get_state.cache_clear()
    client = TestClient(appmod.create_app())
    body = client.post(
        "/agents/ooa-agent/chat",
        json={"prompt": "beds?", "conversationId": "live"},
    ).json()
    assert "hcp:Ward" in body["citations"]
    appmod.get_state.cache_clear()


def test_cors_preflight_allows_default_app_origin():
    # The browser app (hcc-app-fluent) calls the host cross-origin. A preflight
    # from the default demo origin must be answered with an allow header so the
    # Copilot Drawer can reach /agents/{name}/chat.
    client = _client()
    resp = client.options(
        "/agents/ooa-agent/chat",
        headers={
            "Origin": "https://appsit.curavias.ch",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.status_code in (200, 204)
    assert resp.headers.get("access-control-allow-origin") == "https://appsit.curavias.ch"


def test_cors_honours_env_allowed_origins(monkeypatch):
    monkeypatch.setenv(
        "AGENT_HOST_ALLOWED_ORIGINS",
        "https://example.test, https://other.test",
    )
    get_state.cache_clear()
    client = TestClient(create_app())
    resp = client.options(
        "/agents/ooa-agent/chat",
        headers={
            "Origin": "https://example.test",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "https://example.test"


def test_chat_unknown_agent_404():
    resp = _client().post("/agents/nope/chat", json={"prompt": "x"})
    assert resp.status_code == 404


def test_tool_invocation_denied_without_hitl_evidence():
    # Deny-by-default: no approval evidence → 403 with a deny reason.
    resp = _client().post(
        "/agents/bmca-agent/tools/create-branch",
        json={"params": {}, "hitlEvidence": {}},
    )
    assert resp.status_code == 403
    detail = resp.json()["detail"]
    assert detail["decision"] == "deny"
    assert detail["gateId"] == "HITL-02"


def test_tool_invocation_obo_present_approver_mismatch_denied_403(monkeypatch):
    import api.app as app_module

    class _Ctx:
        user_oid = "real-verified-oid"
        obo_token = ""
        roles = ("HCC.PlatformAdmin",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().post(
        "/agents/bmca-agent/tools/create-branch",
        json={
            "params": {},
            "hitlEvidence": {
                "HITL-02": {
                    "gateId": "HITL-02",
                    "approverObjectId": "claimed-but-not-verified-oid",
                    "approverRole": "HCC.PlatformAdmin",
                    "decisionTimestampUtc": "2026-08-09T00:00:00Z",
                    "correlationId": "c1",
                    "decisionContextHash": "hash",
                    "decisionOutcome": "approved",
                    "sourceWorkflow": "test",
                }
            },
        },
        headers={"Authorization": "Bearer ok"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["reason"] == "approver_identity_not_verified"


def test_tool_invocation_obo_present_approver_matches_allowed(monkeypatch):
    import api.app as app_module

    class _Ctx:
        user_oid = "real-verified-oid"
        obo_token = ""
        roles = ("HCC.PlatformAdmin",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().post(
        "/agents/bmca-agent/tools/create-branch",
        json={
            "params": {},
            "hitlEvidence": {
                "HITL-02": {
                    "gateId": "HITL-02",
                    "approverObjectId": "real-verified-oid",
                    "approverRole": "HCC.PlatformAdmin",
                    "decisionTimestampUtc": "2026-08-09T00:00:00Z",
                    "correlationId": "c1",
                    "decisionContextHash": "hash",
                    "decisionOutcome": "approved",
                    "sourceWorkflow": "test",
                }
            },
        },
        headers={"Authorization": "Bearer ok"},
    )
    assert resp.status_code == 200
    assert resp.json()["decision"] == "allow"


def test_tool_invocation_without_obo_is_unchanged():
    # OBO absent (default) -> unchanged prior behavior, no identity cross-check.
    resp = _client().post(
        "/agents/bmca-agent/tools/create-branch",
        json={"params": {}, "hitlEvidence": {}},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["reason"] == "hitl_no_evidence"


def test_tool_invocation_csa_multi_gate_mismatch_denied_403(monkeypatch):
    # The actual motivating case (Task 4 review follow-up): csa-agent declares
    # TWO gates (HITL-01 sim-run trigger, HITL-04 recommendation draft PR, per
    # agents/csa-agent/manifest.yaml). One gate's approverObjectId matches the
    # OBO identity, the other does not -- proves the loop denies on whichever
    # entry actually mismatches, not just the first one it checks.
    import api.app as app_module

    class _Ctx:
        user_oid = "real-verified-oid"
        obo_token = ""
        roles = ("HCC.PlatformAdmin",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().post(
        "/agents/csa-agent/tools/create-pull-request",
        json={
            "params": {},
            "hitlEvidence": {
                "HITL-01": {
                    "gateId": "HITL-01",
                    "approverObjectId": "real-verified-oid",
                    "approverRole": "HCC.PlatformAdmin",
                    "decisionTimestampUtc": "2026-08-09T00:00:00Z",
                    "correlationId": "c1",
                    "decisionContextHash": "hash",
                    "decisionOutcome": "approved",
                    "sourceWorkflow": "test",
                },
                "HITL-04": {
                    "gateId": "HITL-04",
                    "approverObjectId": "claimed-but-not-verified-oid",
                    "approverRole": "HCC.PlatformAdmin",
                    "decisionTimestampUtc": "2026-08-09T00:00:00Z",
                    "correlationId": "c1",
                    "decisionContextHash": "hash",
                    "decisionOutcome": "approved",
                    "sourceWorkflow": "test",
                },
            },
        },
        headers={"Authorization": "Bearer ok"},
    )
    assert resp.status_code == 403
    detail = resp.json()["detail"]
    assert detail["reason"] == "approver_identity_not_verified"
    assert detail["gateId"] == "HITL-04"


def test_tool_invocation_mismatch_on_gate_outside_manifest_still_denied_403(monkeypatch):
    # Issue 2 (Task 4 review follow-up): the OBO approver check intentionally
    # validates ALL supplied hitlEvidence entries, not just the gates
    # bmca-agent's manifest requires (["HITL-02"]). HITL-05 is a valid gate id
    # bmca-agent does NOT declare; a mismatched claim on it must still deny --
    # proving the check isn't scoped down to only the manifest's required gates.
    import api.app as app_module

    class _Ctx:
        user_oid = "real-verified-oid"
        obo_token = ""
        roles = ("HCC.PlatformAdmin",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().post(
        "/agents/bmca-agent/tools/create-branch",
        json={
            "params": {},
            "hitlEvidence": {
                "HITL-02": {
                    "gateId": "HITL-02",
                    "approverObjectId": "real-verified-oid",
                    "approverRole": "HCC.PlatformAdmin",
                    "decisionTimestampUtc": "2026-08-09T00:00:00Z",
                    "correlationId": "c1",
                    "decisionContextHash": "hash",
                    "decisionOutcome": "approved",
                    "sourceWorkflow": "test",
                },
                "HITL-05": {
                    "gateId": "HITL-05",
                    "approverObjectId": "claimed-but-not-verified-oid",
                    "approverRole": "HCC.PlatformAdmin",
                    "decisionTimestampUtc": "2026-08-09T00:00:00Z",
                    "correlationId": "c1",
                    "decisionContextHash": "hash",
                    "decisionOutcome": "approved",
                    "sourceWorkflow": "test",
                },
            },
        },
        headers={"Authorization": "Bearer ok"},
    )
    assert resp.status_code == 403
    detail = resp.json()["detail"]
    assert detail["reason"] == "approver_identity_not_verified"
    assert detail["gateId"] == "HITL-05"
