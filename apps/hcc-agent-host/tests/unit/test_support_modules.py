"""Unit tests for redaction, token validation, cache, persistence, tools (T5)."""

from __future__ import annotations

import time

import pytest

from orchestrator.redaction import redact, contains_sensitive
from auth.token_validator import (
    TokenValidationError,
    validate_claims,
)
from cache.redis_client import RedisCache
from persistence.cosmos_client import CosmosPersistence
from tools.fabric_adapter import FabricAdapter
from tools.github_adapter import GithubAdapter
from tools.base import ceiling_exceeds


# ---- redaction -----------------------------------------------------------

def test_redact_masks_ahv_and_jwt():
    text = "patient 756.1234.5678.90 token ******"
    out = redact(text)
    assert "756.1234.5678.90" not in out
    assert "eyJhbGci" not in out
    assert "[redacted]" in out


def test_contains_sensitive_detects_pat():
    assert contains_sensitive("ghp_abcdefghijklmnopqrstuvwxyz0123")
    assert not contains_sensitive("Auslastung Station B liegt bei 92%.")


# ---- token validation ----------------------------------------------------

def _claims(**over) -> dict:
    base = {
        "aud": "api://ihzhhpf-app",
        "iss": "https://login.microsoftonline.com/tenant/v2.0",
        "exp": time.time() + 3600,
        "oid": "user-oid",
        "roles": ["HCC.PlatformAdmin"],
        "hospital": "USZ",
        "env": "sit",
    }
    base.update(over)
    return base


def test_validate_claims_ok():
    caller = validate_claims(
        _claims(),
        expected_audience="api://ihzhhpf-app",
        expected_issuer="https://login.microsoftonline.com/tenant/v2.0",
    )
    assert caller.oid == "user-oid"
    assert "HCC.PlatformAdmin" in caller.roles
    assert caller.env == "sit"


def test_validate_claims_rejects_bad_audience():
    with pytest.raises(TokenValidationError):
        validate_claims(
            _claims(aud="api://someone-else"),
            expected_audience="api://ihzhhpf-app",
            expected_issuer="https://login.microsoftonline.com/tenant/v2.0",
        )


def test_validate_claims_rejects_expired():
    with pytest.raises(TokenValidationError):
        validate_claims(
            _claims(exp=time.time() - 10),
            expected_audience="api://ihzhhpf-app",
            expected_issuer="https://login.microsoftonline.com/tenant/v2.0",
        )


# ---- cache ---------------------------------------------------------------

def test_cache_grounding_roundtrip_and_ttl():
    cache = RedisCache()
    cache.cache_grounding("gold.bed_assignment", [{"ward": "B"}], ttl_seconds=300)
    assert cache.get_grounding("gold.bed_assignment") == [{"ward": "B"}]
    assert cache.get_grounding("missing") is None


# ---- persistence ---------------------------------------------------------

def test_persistence_requires_partition_key():
    store = CosmosPersistence()
    with pytest.raises(ValueError):
        store.write("conversations", {"answer": "x"})  # missing conversationId


def test_persistence_write_and_query():
    store = CosmosPersistence()
    store.write("audit", {"correlationId": "c1", "event": "x"})
    assert store.query_by_correlation("audit", "c1")[0]["event"] == "x"


# ---- tools ---------------------------------------------------------------

def test_fabric_adapter_returns_synthetic_rows():
    rows = FabricAdapter().query("gold.bed_assignment")
    assert rows and "occupied" in rows[0]


def test_github_adapter_records_calls_and_rejects_unknown_tool():
    adapter = GithubAdapter()
    adapter.invoke("add-issue-comment", {"body": "hi"})
    assert adapter.calls[0].tool == "add-issue-comment"
    with pytest.raises(ValueError):
        adapter.invoke("delete-repo", {})


def test_ceiling_exceeds():
    assert ceiling_exceeds("deploy", "write")
    assert not ceiling_exceeds("read", "write")
