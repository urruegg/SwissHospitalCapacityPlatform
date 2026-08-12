"""#424 M2 — golden-source read service (agent-host, read ceiling).

Serves the synthetic Gold board payloads over a real, RLS-scoped REST surface so
the hcc-app-fluent RoleBoard loaders can read `live` golden evidence (provenance
`live`) instead of the app's built-in fixtures. The payloads are the **same**
synthetic fixtures that ship in the app (single source of truth): they are
exported to ``data/*.json`` and a vitest parity guard in the app fails if they
drift from the RoleBoard ``*_PINNED`` constants.

Contract (mirrors ``data/roleboard/rls-scope.ts`` + ``golden-source-client.ts``):

- **Deny-by-default** — a read with no proven hospital scope or no caller oid is
  refused (the app's ``iqFetch`` already refuses to call without a
  ``ContextEnvelope``; the server enforces the same at the trust boundary).
- **Row-level security** — ``hospitalScope == 'aggregated'`` returns all rows;
  any other scope returns only rows whose ``hospital`` tag matches, plus rows
  that carry no ``hospital`` tag (site-agnostic demo fixtures). This is the seam
  that lifts to live Fabric RLS in #424 M4 without an app change (ADR-0052).

Synthetic-only, no PHI (ADR-0016).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from golden.rls import RlsProvider, RlsProviderError, SimulatedRlsProvider
from golden.signals_source import SnapshotSource

# Module singleton: env-gated internally (SIGNALS_SNAPSHOT_URL). When live signals
# are available they replace the occupancy external-signals; otherwise the payload
# is unchanged and the app falls back to its built-in signals.
_SNAPSHOT_SOURCE = SnapshotSource()

GOLDEN_RESOURCES: tuple[str, ...] = (
    "occupancy",
    "discharge",
    "bed-manager",
    "or-steering",
    "staffing",
    "crisis",
    "network",
)

_DATA_DIR = Path(__file__).resolve().parent / "data"


class UnknownResourceError(KeyError):
    """Raised when a requested board resource is not one of GOLDEN_RESOURCES."""


# #424 M4 — the deny-by-default scope gate now lives in the RlsProvider seam.
# ``GoldenScopeError`` is retained as an alias so existing callers/tests that
# catch it keep working; the provider raises ``RlsProviderError`` (same class).
GoldenScopeError = RlsProviderError


@lru_cache(maxsize=len(GOLDEN_RESOURCES))
def _read_fixture(resource: str) -> str:
    return (_DATA_DIR / f"{resource}.json").read_text(encoding="utf-8")


def apply_row_scope(rows: list[dict[str, Any]], hospital_scope: str) -> list[dict[str, Any]]:
    """Filter site-tagged rows to the caller's scope (aggregated => all).

    Thin wrapper over the in-process provider's row filter, kept for existing
    callers/tests.
    """
    if hospital_scope == "aggregated":
        return list(rows)
    return [row for row in rows if row.get("hospital") in (None, hospital_scope)]


def _scope_payload(
    payload: dict[str, Any],
    *,
    hospital_scope: str,
    user_oid: str,
    provider: RlsProvider,
) -> dict[str, Any]:
    """Route every top-level list of site-tagged rows through the RLS provider.

    Board fixtures are single-site (no ``hospital`` tag) so this is a no-op for
    them; the ``network`` resource carries multi-site rows and is filtered to the
    caller's scope. The enforcement point is the provider, not the browser.
    """
    scoped: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
            scoped[key] = provider.scope(
                value, hospital_scope=hospital_scope, user_oid=user_oid
            ).rows
        else:
            scoped[key] = value
    return scoped


def load_golden(
    resource: str,
    *,
    hospital_scope: str,
    user_oid: str,
    provider: RlsProvider | None = None,
    signals_source: SnapshotSource | None = None,
) -> dict[str, Any]:
    """Return the RLS-scoped golden payload for ``resource`` with ``_rls`` metadata.

    Raises ``UnknownResourceError`` for an unknown board and ``RlsProviderError``
    (aliased ``GoldenScopeError``) deny-by-default when the read is not grounded
    (missing scope or oid), or when a dormant provider (Fabric, no OBO) refuses.
    """
    if resource not in GOLDEN_RESOURCES:
        raise UnknownResourceError(resource)
    provider = provider or SimulatedRlsProvider()
    # Enforce deny-by-default and capture provenance metadata up front, so an
    # ungrounded read is refused regardless of the payload's shape.
    decision = provider.scope([], hospital_scope=hospital_scope, user_oid=user_oid)
    payload = json.loads(_read_fixture(resource))
    scoped = _scope_payload(
        payload, hospital_scope=hospital_scope, user_oid=user_oid, provider=provider
    )
    scoped["_rls"] = {
        "scope": decision.scope,
        "provider": decision.provider,
        "provenance": decision.provenance,
    }
    # Sprint 44 (B'): live external signals from the runner Blob snapshot, when
    # configured. External feeds are site-agnostic, so no RLS filtering applies.
    if resource == "occupancy":
        live_signals = (signals_source or _SNAPSHOT_SOURCE).external_signals()
        if live_signals is not None:
            scoped["signals"] = live_signals
    return scoped
