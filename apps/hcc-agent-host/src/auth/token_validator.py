"""Sprint 13 T5 — server-side MSAL token validation + OBO placeholder.

Validates the caller's bearer token (issuer, audience, expiry, roles) before the
host dispatches any agent. The live implementation verifies the JWT signature via
the tenant JWKS; this module provides the claim-validation surface and a
deny-by-default posture. OBO exchange for a Fabric token is represented by
:func:`acquire_obo_token` (wired to ``azure-identity`` at deploy time).

No secrets are hard-coded (copilot-instructions §4): issuer/audience come from
environment configuration.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


class TokenValidationError(Exception):
    """Raised when a token fails validation. Callers must treat as 401."""


@dataclass(frozen=True)
class ValidatedCaller:
    oid: str
    roles: tuple[str, ...]
    hospital: str
    env: str


def validate_claims(
    claims: dict[str, Any],
    *,
    expected_audience: str,
    expected_issuer: str,
    now: float | None = None,
) -> ValidatedCaller:
    """Validate decoded token claims. Deny-by-default on any mismatch.

    Signature verification is performed by the live JWKS-backed decoder before
    this function is reached; here we enforce audience, issuer, and expiry and
    project the app claims the host consumes.
    """
    now = now if now is not None else time.time()

    if claims.get("aud") != expected_audience:
        raise TokenValidationError("audience mismatch")
    if claims.get("iss") != expected_issuer:
        raise TokenValidationError("issuer mismatch")
    exp = claims.get("exp")
    if not isinstance(exp, (int, float)) or exp <= now:
        raise TokenValidationError("token expired or missing exp")

    oid = claims.get("oid")
    if not oid:
        raise TokenValidationError("missing oid")

    roles = claims.get("roles", [])
    if isinstance(roles, str):
        roles = [r for r in roles.replace(",", " ").split() if r]

    return ValidatedCaller(
        oid=str(oid),
        roles=tuple(roles),
        hospital=str(claims.get("hospital", "aggregated")),
        env=str(claims.get("env", "dev")),
    )


def acquire_obo_token(user_assertion: str, scope: str) -> str:
    """On-behalf-of token exchange for downstream Fabric calls.

    Placeholder for the live ``azure-identity`` OBO flow (wired at deploy time).
    Raises in dev/CI so no code path silently assumes a real token.
    """
    raise NotImplementedError(
        "OBO exchange requires the azure-identity runtime extra (deploy-time)."
    )
