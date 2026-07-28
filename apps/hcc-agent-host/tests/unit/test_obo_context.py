"""#424 M5 — unit tests for the OBO ingress seam (`build_obo_context`).

`build_obo_context` turns the caller's ``Authorization: Bearer`` header into an
``OboContext`` when OBO is enabled, and returns ``None`` (unchanged
simulated/native path) when it is not. Decode + exchange are injected so no live
Entra is needed. Deny-by-default: enabled + missing/invalid token raises.
"""

from __future__ import annotations

import pytest

from auth.obo_context import OboContext, build_obo_context, obo_enabled
from auth.token_validator import TokenValidationError

_CLAIMS = {
    "aud": "api://agent-host",
    "iss": "https://sts.windows.net/tenant-abc/",
    "exp": 9_999_999_999,
    "oid": "user-oid-123",
    "hospital": "hospital-usz",
}


def _enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OBO_ENABLED", "true")
    monkeypatch.setenv("OBO_AUDIENCE", "api://agent-host")
    monkeypatch.setenv("OBO_ISSUER", "https://sts.windows.net/tenant-abc/")


def test_obo_disabled_returns_none(monkeypatch):
    monkeypatch.delenv("OBO_ENABLED", raising=False)
    assert obo_enabled() is False
    assert build_obo_context("Bearer abc") is None


def test_obo_enabled_builds_context(monkeypatch):
    _enabled(monkeypatch)
    seen: dict[str, str] = {}

    def decode(token: str) -> dict:
        seen["token"] = token
        return dict(_CLAIMS)

    def exchange(assertion: str, scope: str) -> str:
        seen["assertion"] = assertion
        seen["scope"] = scope
        return "obo-token-xyz"

    ctx = build_obo_context("Bearer raw-jwt", decode=decode, exchange=exchange)

    assert isinstance(ctx, OboContext)
    assert ctx.user_oid == "user-oid-123"
    assert ctx.obo_token == "obo-token-xyz"
    # The raw bearer (minus the scheme) is what gets decoded + exchanged.
    assert seen["token"] == "raw-jwt"
    assert seen["assertion"] == "raw-jwt"


def test_obo_enabled_missing_bearer_denies(monkeypatch):
    _enabled(monkeypatch)
    with pytest.raises(TokenValidationError):
        build_obo_context("", decode=lambda t: dict(_CLAIMS), exchange=lambda a, s: "x")


def test_obo_enabled_empty_after_scheme_denies(monkeypatch):
    _enabled(monkeypatch)
    with pytest.raises(TokenValidationError):
        build_obo_context("Bearer   ", decode=lambda t: dict(_CLAIMS), exchange=lambda a, s: "x")


def test_obo_enabled_bad_audience_denies(monkeypatch):
    _enabled(monkeypatch)
    bad = dict(_CLAIMS, aud="api://someone-else")
    with pytest.raises(TokenValidationError):
        build_obo_context("Bearer raw", decode=lambda t: bad, exchange=lambda a, s: "x")


def test_obo_accepts_bare_token_without_scheme(monkeypatch):
    _enabled(monkeypatch)
    ctx = build_obo_context(
        "raw-jwt-no-scheme",
        decode=lambda t: dict(_CLAIMS),
        exchange=lambda a, s: "obo-token-xyz",
    )
    assert ctx is not None
    assert ctx.obo_token == "obo-token-xyz"
