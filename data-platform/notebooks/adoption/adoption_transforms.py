"""Pure transforms for the adoption-telemetry Bronze ingest.

Sprint 12 · T5 / Sprint 12.1 mini-sprint. Maps raw Entra sign-in projections
(from Log Analytics ``SigninLogs`` — or, equivalently, Microsoft Graph
``auditLogs/signIns``) to the **Bronze adoption contract** consumed downstream by
the Sprint 15 BVA medallion (``data-platform/notebooks/bva/ingest_bronze_adoption.py``)
and by the synthetic backfill (``data-platform/scripts/adoption_seed_synthetic.py``).

Contract row (design spec ``docs/superpowers/specs/2026-07-09-sprint-12-org-design.md`` §7)::

    userId, upn, appDisplayName, appId, signInTimestamp, env, resultType,
    ipAddress (redacted to /24), clientAppUsed, deviceDetailTrustType,
    locationCountryOrRegion, appRole

**No PHI** — sign-in metadata carries UPN + IP only; IP is redacted to a /24.

This module is intentionally dependency-free (no PySpark) so it can be unit
tested in CI. The Fabric notebook ``01_adoption_ingest.ipynb`` imports these
helpers and drives them against the Spark-loaded sign-in rows.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

# Canonical order of the Bronze adoption contract fields. Kept identical to the
# synthetic backfill output so real and seeded telemetry are interchangeable in
# Files/Bronze/adoption/YYYY-MM-DD/signins.json.
BRONZE_CONTRACT_FIELDS: tuple[str, ...] = (
    "userId",
    "upn",
    "appDisplayName",
    "appId",
    "signInTimestamp",
    "env",
    "resultType",
    "ipAddress",
    "clientAppUsed",
    "deviceDetailTrustType",
    "locationCountryOrRegion",
    "appRole",
)

# Successful sign-in result code (Entra). Downstream adoption KPIs count only
# successful sign-ins; Bronze keeps every row and lets Silver/Gold filter.
SIGNIN_SUCCESS = "0"

_PROD_SUFFIX = "-prod"


def redact_ip_24(ip: str | None) -> str | None:
    """Zero the last octet of an IPv4 address (``/24`` redaction).

    Non-IPv4 or empty values are returned unchanged (IPv6 has no ``/24`` octet
    notion and is passed through so Silver can decide how to bucket it).
    """
    if not ip:
        return ip
    octets = ip.split(".")
    if len(octets) != 4:
        return ip
    return f"{octets[0]}.{octets[1]}.{octets[2]}.0"


def derive_env(app_display_name: str | None, default: str = "sit") -> str:
    """Derive the deployment slot (``sit``/``prod``) from the app display name.

    The shared-user model (design spec §4) exposes one SIT slot and one PROD
    slot of the same app. PROD app registrations carry a ``-prod`` suffix; every
    other host resolves to ``sit`` during the demo phase.
    """
    name = (app_display_name or "").strip().lower()
    if name.endswith(_PROD_SUFFIX):
        return "prod"
    return default


def _iso_z(value) -> str:
    """Normalise a timestamp to ``...Z`` ISO-8601 form.

    Accepts ``str`` (Log Analytics/Graph already emit ISO) or anything with an
    ``isoformat`` method (e.g. ``datetime``). ``+00:00`` is normalised to ``Z``.
    """
    if value is None:
        return ""
    text = value.isoformat() if hasattr(value, "isoformat") else str(value)
    return text.replace("+00:00", "Z")


def signin_to_bronze_row(
    raw: Mapping,
    persona_role: Mapping[str, str] | None = None,
    default_env: str = "sit",
) -> dict:
    """Map one raw sign-in projection to a Bronze adoption contract row.

    ``raw`` uses the ``SigninLogs`` projection field names emitted by the KQL in
    ``01_adoption_ingest.ipynb`` (also produced by the Graph ``auditLogs/signIns``
    projection). ``persona_role`` maps a lower-cased UPN to its Entra app role so
    the adoption KPI can attribute each sign-in to a product capability; unknown
    users get ``appRole = None`` and are attributed to ``Aggregated`` downstream.
    """
    roles = persona_role or {}
    app_display_name = raw.get("AppDisplayName")
    upn = raw.get("UserPrincipalName")
    return {
        "userId": raw.get("UserId"),
        "upn": upn,
        "appDisplayName": app_display_name,
        "appId": raw.get("AppId"),
        "signInTimestamp": _iso_z(raw.get("TimeGenerated")),
        "env": derive_env(app_display_name, default=default_env),
        "resultType": str(raw.get("ResultType")) if raw.get("ResultType") is not None else None,
        "ipAddress": redact_ip_24(raw.get("IPAddress")),
        "clientAppUsed": raw.get("ClientAppUsed"),
        "deviceDetailTrustType": raw.get("DeviceDetail_TrustType"),
        "locationCountryOrRegion": raw.get("Location_CountryOrRegion"),
        "appRole": roles.get(upn.lower()) if upn else None,
    }


def to_bronze_rows(
    raw_rows: Iterable[Mapping],
    persona_role: Mapping[str, str] | None = None,
    default_env: str = "sit",
) -> list[dict]:
    """Map a batch of raw sign-in projections to Bronze contract rows."""
    return [signin_to_bronze_row(r, persona_role, default_env) for r in raw_rows]


def group_by_signin_day(rows: Iterable[Mapping]) -> dict[str, list[dict]]:
    """Group contract rows by their sign-in day (``YYYY-MM-DD``).

    Mirrors the synthetic backfill layout so each day lands as one
    ``Files/Bronze/adoption/<day>/signins.json`` file regardless of source.
    """
    by_day: dict[str, list[dict]] = {}
    for row in rows:
        ts = str(row.get("signInTimestamp", ""))
        if len(ts) < 10:
            continue
        by_day.setdefault(ts[:10], []).append(dict(row))
    return by_day
