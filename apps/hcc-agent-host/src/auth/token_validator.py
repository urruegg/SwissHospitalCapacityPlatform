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

import os
import time
from dataclasses import dataclass
from typing import Any, Callable

from .group_roles import group_role_map


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

    # Sprint 43 WS-6 follow-up: assigning a principal to an App Role requires
    # a directory role admin@ does not hold (see group_roles.py docstring),
    # but `groupMembershipClaims` is owner-level/self-service and reflects
    # memberships that already exist. Union any group-derived roles onto the
    # direct `roles` claim (deduped, order-preserving) so downstream role
    # checks (`_require_active_role_held` et al.) keep working unchanged
    # regardless of which mechanism populated them.
    groups = claims.get("groups", [])
    if isinstance(groups, str):
        groups = [g for g in groups.replace(",", " ").split() if g]
    gmap = group_role_map()
    group_derived_roles = [gmap[g] for g in groups if g in gmap]
    all_roles = tuple(dict.fromkeys([*roles, *group_derived_roles]))

    return ValidatedCaller(
        oid=str(oid),
        roles=all_roles,
        hospital=str(claims.get("hospital", "aggregated")),
        env=str(claims.get("env", "dev")),
    )


def _default_obo_credential(
    *, tenant_id: str, client_id: str, client_secret: str, user_assertion: str
) -> Any:
    """Build the live ``azure-identity`` on-behalf-of credential.

    Imported lazily so the module imports without the ``runtime`` extra (CI/dev).
    Never returns a fabricated token — if ``azure-identity`` is absent the import
    raises, which the caller surfaces as a clear error.
    """
    from azure.identity import OnBehalfOfCredential

    return OnBehalfOfCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
        user_assertion=user_assertion,
    )


def acquire_obo_token(
    user_assertion: str,
    scope: str,
    *,
    credential_factory: Callable[..., Any] | None = None,
) -> str:
    """On-behalf-of token exchange for downstream Fabric/Foundry calls.

    Exchanges the signed-in user's assertion for a token scoped to ``scope`` via
    an ``OnBehalfOfCredential`` built from ``OBO_TENANT_ID`` / ``OBO_CLIENT_ID`` /
    ``OBO_CLIENT_SECRET`` (no secret is hard-coded — copilot-instructions §4).
    ``credential_factory`` is injected in tests so the flow is verified without a
    live tenant. Deny-by-default: a missing assertion or missing config raises
    rather than returning an unusable or fabricated token.
    """
    if not user_assertion:
        raise TokenValidationError("OBO exchange requires a user assertion")

    tenant_id = os.getenv("OBO_TENANT_ID", "")
    client_id = os.getenv("OBO_CLIENT_ID", "")
    client_secret = os.getenv("OBO_CLIENT_SECRET", "")
    if not (tenant_id and client_id and client_secret):
        raise TokenValidationError(
            "OBO exchange requires OBO_TENANT_ID, OBO_CLIENT_ID and OBO_CLIENT_SECRET"
        )

    factory = credential_factory or _default_obo_credential
    credential = factory(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
        user_assertion=user_assertion,
    )
    return credential.get_token(scope).token
