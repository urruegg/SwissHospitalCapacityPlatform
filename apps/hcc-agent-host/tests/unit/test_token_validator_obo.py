"""#424 M5 — unit tests for the on-behalf-of exchange (`acquire_obo_token`).

The exchange is dependency-injected via ``credential_factory`` so the flow is
verified without a live Entra tenant (azure-identity is a runtime-only extra).
"""

from __future__ import annotations

import pytest

from auth.token_validator import TokenValidationError, acquire_obo_token


class _FakeToken:
    def __init__(self, token: str) -> None:
        self.token = token


class _FakeCredential:
    def __init__(self, **kwargs: str) -> None:
        self.kwargs = kwargs

    def get_token(self, scope: str) -> _FakeToken:
        # Prove the requested scope reaches the credential.
        return _FakeToken(f"obo-for::{scope}")


def _configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OBO_TENANT_ID", "tenant-abc")
    monkeypatch.setenv("OBO_CLIENT_ID", "client-abc")
    monkeypatch.setenv("OBO_CLIENT_SECRET", "shhh")


def test_acquire_obo_token_exchanges_via_injected_factory(monkeypatch):
    _configured(monkeypatch)
    captured: dict[str, str] = {}

    def factory(**kwargs: str) -> _FakeCredential:
        captured.update(kwargs)
        return _FakeCredential(**kwargs)

    token = acquire_obo_token(
        "user-assertion-jwt",
        "https://api.fabric.microsoft.com/.default",
        credential_factory=factory,
    )

    assert token == "obo-for::https://api.fabric.microsoft.com/.default"
    # Config + the user assertion are threaded into the credential.
    assert captured["tenant_id"] == "tenant-abc"
    assert captured["client_id"] == "client-abc"
    assert captured["client_secret"] == "shhh"
    assert captured["user_assertion"] == "user-assertion-jwt"


def test_acquire_obo_token_requires_user_assertion(monkeypatch):
    _configured(monkeypatch)
    with pytest.raises(TokenValidationError):
        acquire_obo_token("", "scope", credential_factory=lambda **k: _FakeCredential())


def test_acquire_obo_token_requires_config(monkeypatch):
    # No OBO_* env → must raise rather than build a partial credential.
    monkeypatch.delenv("OBO_TENANT_ID", raising=False)
    monkeypatch.delenv("OBO_CLIENT_ID", raising=False)
    monkeypatch.delenv("OBO_CLIENT_SECRET", raising=False)
    with pytest.raises(TokenValidationError):
        acquire_obo_token("assertion", "scope", credential_factory=lambda **k: _FakeCredential())


def test_acquire_obo_token_default_factory_needs_runtime(monkeypatch):
    # Without the azure-identity runtime extra, the default factory must raise a
    # clear error, never a fabricated token.
    _configured(monkeypatch)
    with pytest.raises(Exception):
        acquire_obo_token("assertion", "scope")
