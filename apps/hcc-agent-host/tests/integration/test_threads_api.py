"""Integration test — #424 M3 Foundry thread mint + thread-scoped chat.

``POST /agents/{name}/threads`` mints a stable ``(userOid x agent)`` thread
(deny-by-default without ``X-User-Oid``); ``POST /agents/{name}/chat`` accepts a
``threadId`` so turns thread server-side. Native provider (provenance ``native``)
is the SIT default; the Foundry provider is dormant until M5. Synthetic, no PHI.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app, get_state

_IDENTITY = {
    "X-User-Oid": "11111111-1111-1111-1111-111111111111",
    "X-Active-Role": "HCC.BedManager",
}


def _client() -> TestClient:
    get_state.cache_clear()
    return TestClient(create_app())


def test_mint_thread_returns_native_provenance():
    resp = _client().post("/agents/bmca-agent/threads", headers=_IDENTITY)
    assert resp.status_code == 200
    body = resp.json()
    assert body["threadId"].startswith("thr-")
    assert body["provenance"] == "native"


def test_mint_thread_is_idempotent_per_user_and_agent():
    client = _client()
    first = client.post("/agents/bmca-agent/threads", headers=_IDENTITY).json()
    second = client.post("/agents/bmca-agent/threads", headers=_IDENTITY).json()
    assert first["threadId"] == second["threadId"]


def test_mint_thread_distinct_per_agent():
    client = _client()
    bmca = client.post("/agents/bmca-agent/threads", headers=_IDENTITY).json()
    ooa = client.post("/agents/ooa-agent/threads", headers=_IDENTITY).json()
    assert bmca["threadId"] != ooa["threadId"]


def test_mint_thread_refuses_without_user_oid():
    resp = _client().post("/agents/bmca-agent/threads", headers={"X-Active-Role": "HCC.Viewer"})
    assert resp.status_code == 401


def test_mint_thread_unknown_agent_404():
    resp = _client().post("/agents/not-an-agent/threads", headers=_IDENTITY)
    assert resp.status_code == 404


def test_chat_accepts_thread_id_and_threads_history():
    client = _client()
    thread = client.post("/agents/bmca-agent/threads", headers=_IDENTITY).json()
    tid = thread["threadId"]
    r1 = client.post(
        "/agents/bmca-agent/chat",
        json={"prompt": "Station B ist fast voll", "threadId": tid},
        headers=_IDENTITY,
    )
    r2 = client.post(
        "/agents/bmca-agent/chat",
        json={"prompt": "Und jetzt?", "threadId": tid},
        headers=_IDENTITY,
    )
    assert r1.status_code == 200 and r2.status_code == 200
    state = get_state()
    turns = [
        c for c in state.orchestrator.persistence.read_all("conversations")
        if c.get("conversationId") == tid and c.get("userPrompt") is not None
    ]
    assert len(turns) == 2  # both turns persisted under the one thread


def test_chat_without_thread_id_still_works():
    # Back-compat: the legacy conversationId default path is unchanged.
    resp = _client().post(
        "/agents/bmca-agent/chat",
        json={"prompt": "Station B ist fast voll", "conversationId": "c1"},
    )
    assert resp.status_code == 200
    assert resp.json()["refused"] is False


def test_threads_cors_preflight_allows_identity_headers():
    resp = _client().options(
        "/agents/bmca-agent/threads",
        headers={
            "Origin": "https://appsit.curavias.ch",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "x-user-oid,x-active-role",
        },
    )
    assert resp.status_code in (200, 204)
    allowed = (resp.headers.get("access-control-allow-headers") or "").lower()
    assert "x-user-oid" in allowed
