"""#424 M5 — OBO ingress seam.

Turns the caller's ``Authorization: Bearer`` header into an :class:`OboContext`
when on-behalf-of is enabled, and returns ``None`` (unchanged simulated/native
path) when it is not. This is the single point where a per-user token enters the
agent-host, so the M4 ``FabricDataAgentRlsProvider`` and M3 ``FoundryThreadProvider``
flip to per-user by **configuration** (``OBO_ENABLED`` + ``OBO_*``), not code
(ADR-0057, M5 design spec §4.2).

Deny-by-default: when OBO is enabled, a missing/invalid bearer or a failed
exchange raises :class:`~auth.token_validator.TokenValidationError` (HTTP 401 at
the endpoint) rather than silently downgrading to a wide read.

Decode + exchange are injectable so the flow is unit-tested without a live Entra
tenant; the default decode performs real JWKS-backed validation (guarded import),
never trusting an unverified token.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable

from auth.token_validator import TokenValidationError, acquire_obo_token, validate_claims

# Default downstream scope for the OBO exchange (Fabric). Overridable via env so
# the same image lifts to a Foundry scope without a rebuild.
_DEFAULT_OBO_SCOPE = "https://api.fabric.microsoft.com/.default"

_TRUE = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class OboContext:
    """A validated per-user identity plus the exchanged downstream token."""

    user_oid: str
    obo_token: str


def obo_enabled() -> bool:
    """True only when ``OBO_ENABLED`` is explicitly truthy (default off)."""
    return (os.getenv("OBO_ENABLED") or "false").strip().lower() in _TRUE


def _strip_bearer(authorization: str) -> str:
    value = authorization.lstrip()
    if value.lower().startswith("bearer "):
        return value[len("bearer ") :].strip()
    return value.strip()


def _default_decode(token: str) -> dict[str, Any]:
    """Verify + decode the JWT via the tenant JWKS (guarded import).

    Only reached in a live, OBO-enabled deployment; unit tests inject ``decode``.
    Raises if the runtime crypto/JWKS config is absent so no unverified token is
    ever trusted.
    """
    import jwt  # PyJWT, part of the runtime extra
    from jwt import PyJWKClient

    jwks_url = os.getenv("OBO_JWKS_URL", "")
    audience = os.getenv("OBO_AUDIENCE", "")
    issuer = os.getenv("OBO_ISSUER", "")
    if not (jwks_url and audience and issuer):
        raise TokenValidationError(
            "OBO decode requires OBO_JWKS_URL, OBO_AUDIENCE and OBO_ISSUER"
        )
    signing_key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token).key
    return jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        audience=audience,
        issuer=issuer,
    )


def build_obo_context(
    authorization: str,
    *,
    decode: Callable[[str], dict[str, Any]] | None = None,
    exchange: Callable[[str, str], str] | None = None,
) -> OboContext | None:
    """Build an :class:`OboContext` from the ``Authorization`` header.

    - OBO disabled → ``None`` (unchanged simulated/native path).
    - OBO enabled + missing/empty bearer → raises (deny-by-default, 401).
    - OBO enabled + bearer → decode, validate claims (aud/iss/exp/oid), exchange
      on-behalf-of, return the context. Any failure raises.
    """
    if not obo_enabled():
        return None

    token = _strip_bearer(authorization)
    if not token:
        raise TokenValidationError("OBO enabled but no bearer token was presented")

    claims = (decode or _default_decode)(token)
    caller = validate_claims(
        claims,
        expected_audience=os.getenv("OBO_AUDIENCE", ""),
        expected_issuer=os.getenv("OBO_ISSUER", ""),
    )
    scope = os.getenv("OBO_FABRIC_SCOPE", _DEFAULT_OBO_SCOPE)
    obo_token = (exchange or acquire_obo_token)(token, scope)
    return OboContext(user_oid=caller.oid, obo_token=obo_token)
