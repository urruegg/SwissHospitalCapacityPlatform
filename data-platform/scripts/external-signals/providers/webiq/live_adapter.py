"""Gated Microsoft Web IQ live binding.

Disabled unless WEBIQ_LIVE_ENABLED=true AND a Key Vault-backed credential
resolves. Always mocked in CI (NFR-EXT-PLG-001); demo/SIT run simulator-only
(NFR-EXT-WEBIQ-002, ADR-0060). This stub makes a real call impossible in demo
scope by refusing when disabled.
"""
from __future__ import annotations

import os


def is_enabled() -> bool:
    return os.environ.get("WEBIQ_LIVE_ENABLED", "").lower() == "true"


def fetch(terms: list[str], *, token_provider=None, http_request=None) -> dict:
    if not is_enabled():
        raise RuntimeError("REFUSE: webiq-live-binding-disabled (GA/credential-gated)")
    # GA/credential-gated real path - intentionally not wired in demo scope.
    raise NotImplementedError(
        "Web IQ live binding is GA-gated; enable only with a vetted credential."
    )
