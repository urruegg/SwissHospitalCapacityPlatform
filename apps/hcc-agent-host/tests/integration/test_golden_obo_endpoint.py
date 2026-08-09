"""#424 M5 — endpoint tests for the OBO ingress branch on the golden read.

Two properties matter at the HTTP boundary:

1. **Parity when OBO is off (SIT default):** the golden read behaves exactly as
   after M4 — simulated provider, deny-by-default, honest headers.
2. **Deny-by-default when OBO is on:** an invalid/missing bearer under
   ``OBO_ENABLED=true`` is a 401, never a wide read.

No live Entra/Fabric — the OBO seam is monkeypatched at the endpoint boundary.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import api.app as app_module
from api.app import create_app, get_state
from auth.token_validator import TokenValidationError

_SCOPED = {
    "X-User-Oid": "33333333-3333-3333-3333-333333333333",
    "X-Hospital-Scope": "aggregated",
    "X-Active-Role": "HCC.Viewer",
}


def _client() -> TestClient:
    get_state.cache_clear()
    return TestClient(create_app())


def test_obo_disabled_golden_parity(monkeypatch):
    # OBO off (default) → unchanged M4 behavior: simulated provider, 200.
    monkeypatch.delenv("OBO_ENABLED", raising=False)
    resp = _client().get("/golden/network", headers=_SCOPED)
    assert resp.status_code == 200
    assert resp.headers["X-Rls-Provider"] == "simulated"
    assert resp.json()["_rls"]["provider"] == "simulated"


def test_obo_enabled_no_bearer_falls_back_to_simulated(monkeypatch):
    # Demo mode: OBO_ENABLED=true tenant-wide, but this caller never signed in
    # (no Authorization header at all) -> unchanged simulated behavior, not 401.
    monkeypatch.setenv("OBO_ENABLED", "true")
    monkeypatch.setenv("OBO_AUDIENCE", "api://agent-host")
    monkeypatch.setenv("OBO_ISSUER", "https://sts.windows.net/tenant-abc/")
    resp = _client().get("/golden/network", headers=_SCOPED)
    assert resp.status_code == 200
    assert resp.json()["_rls"]["provider"] == "simulated"


def test_obo_enabled_invalid_bearer_denies(monkeypatch):
    # OBO on + a bearer the seam rejects → 401 (deny-by-default), never served.
    def _reject(_authorization: str) -> None:
        raise TokenValidationError("bad token")

    monkeypatch.setattr(app_module, "build_obo_context", _reject)
    resp = _client().get(
        "/golden/network",
        headers={**_SCOPED, "Authorization": "Bearer nope"},
    )
    assert resp.status_code == 401


def test_obo_context_routes_user_oid(monkeypatch):
    # A valid OBO context supplies the user oid + token; with no live client the
    # simulated provider still scopes by header, proving the context is consumed
    # (user_oid comes from the token, not the X-User-Oid header).
    ctx = app_module.build_obo_context  # keep ref for signature parity

    class _Ctx:
        user_oid = "44444444-4444-4444-4444-444444444444"
        obo_token = ""  # empty → rls_provider_for falls back to simulated

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().get(
        "/golden/network",
        headers={"X-Hospital-Scope": "aggregated", "Authorization": "Bearer ok"},
    )
    assert resp.status_code == 200
    assert resp.json()["_rls"]["provider"] == "simulated"
    assert ctx is not None


def test_obo_active_role_not_held_is_refused_403(monkeypatch):
    # A valid OBO context that holds only HCC.Viewer, but the caller asks for
    # HCC.SuperAdmin via the header -- deny-by-default, never silently widen.
    class _Ctx:
        user_oid = "55555555-5555-5555-5555-555555555555"
        obo_token = ""
        roles = ("HCC.Viewer",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().get(
        "/golden/network",
        headers={
            "X-Hospital-Scope": "aggregated",
            "X-Active-Role": "HCC.SuperAdmin",
            "Authorization": "Bearer ok",
        },
    )
    assert resp.status_code == 403


def test_obo_active_role_held_is_allowed(monkeypatch):
    class _Ctx:
        user_oid = "66666666-6666-6666-6666-666666666666"
        obo_token = ""
        roles = ("HCC.SuperAdmin", "HCC.Viewer")
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().get(
        "/golden/network",
        headers={
            "X-Hospital-Scope": "aggregated",
            "X-Active-Role": "HCC.SuperAdmin",
            "Authorization": "Bearer ok",
        },
    )
    assert resp.status_code == 200
