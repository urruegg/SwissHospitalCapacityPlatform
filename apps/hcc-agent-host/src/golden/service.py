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

GOLDEN_RESOURCES: tuple[str, ...] = (
    "occupancy",
    "discharge",
    "bed-manager",
    "or-steering",
    "staffing",
    "crisis",
)

_DATA_DIR = Path(__file__).resolve().parent / "data"


class UnknownResourceError(KeyError):
    """Raised when a requested board resource is not one of GOLDEN_RESOURCES."""


class GoldenScopeError(PermissionError):
    """Raised deny-by-default when a read is not grounded by a proven scope/oid."""


@lru_cache(maxsize=len(GOLDEN_RESOURCES))
def _read_fixture(resource: str) -> str:
    return (_DATA_DIR / f"{resource}.json").read_text(encoding="utf-8")


def apply_row_scope(rows: list[dict[str, Any]], hospital_scope: str) -> list[dict[str, Any]]:
    """Filter site-tagged rows to the caller's scope (aggregated => all)."""
    if hospital_scope == "aggregated":
        return list(rows)
    return [row for row in rows if row.get("hospital") in (None, hospital_scope)]


def _scope_payload(payload: dict[str, Any], hospital_scope: str) -> dict[str, Any]:
    """Apply RLS to any top-level list of site-tagged rows in the payload.

    The demo board fixtures are single-site (no ``hospital`` tag), so this is a
    no-op for them today; it becomes meaningful the moment multi-site rows land,
    keeping the enforcement point server-side rather than in the browser.
    """
    scoped: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
            scoped[key] = apply_row_scope(value, hospital_scope)
        else:
            scoped[key] = value
    return scoped


def load_golden(resource: str, *, hospital_scope: str, user_oid: str) -> dict[str, Any]:
    """Return the RLS-scoped golden payload for ``resource``.

    Raises ``UnknownResourceError`` for an unknown board and ``GoldenScopeError``
    deny-by-default when the read is not grounded (missing scope or oid).
    """
    if resource not in GOLDEN_RESOURCES:
        raise UnknownResourceError(resource)
    if not hospital_scope or not user_oid:
        raise GoldenScopeError("golden read requires a proven hospital scope and caller oid")
    payload = json.loads(_read_fixture(resource))
    return _scope_payload(payload, hospital_scope)
