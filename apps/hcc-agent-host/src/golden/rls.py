"""#424 M4 - row-level-security provider seam for the golden read service.

Evidence-grounded capability ladder (see the M4 design spec). The structured
golden read enforces RLS by ``hospitalScope`` through a swappable provider so the
enforcement point is a single, named, testable unit (mirrors the M3
``ThreadProvider``). What is *provably* deployable today bounds each rung:

- **Rung 0 - ``SimulatedRlsProvider`` (default).** Filters the synthetic gold rows
  **in the agent-host**; provenance ``simulated``. Honest demonstration of the RLS
  *shape* (aggregated => all; a site => that site + untagged), not live Fabric
  enforcement. Runs inside the ADR-0013 westus2 synthetic/no-PHI demo scope.

- **Rung 1 - ``FabricDataAgentRlsProvider``.** Reuses the **proven, live** Fabric
  Data Agent client (``da_hospital_capacity``) - the surface that already enforces
  the Direct-Lake semantic model's RLS + the ADR-0016 PHI gate (proven live in
  ``docs/architecture/fabric-iq-ready-evidence.md`` sections 4/5). Two
  independently verified facts bound it: (a) the agent-host queries Fabric under
  its **managed identity**, not the end user, so enforcement is **model/MI scope**,
  uniform for all callers - true per-user scope needs **OBO** (M5); (b) the deployed
  roles have **no dynamic ``USERPRINCIPALNAME()`` row predicate** (the persona logic
  lives in display measures over a non-deployable local CSV), so per-hospital-by-
  user scope additionally needs a **dynamic-RLS TMDL change + deployable persona
  source** (data-lane follow-up). Therefore, without an OBO token this provider
  refuses the *structured* read rather than serve MI-scoped rows as if they were
  per-user.

- **Rung 2 - M5.** The same Data-Agent path under the user's OBO token, once the
  dynamic-RLS TMDL predicate lands - config, not code.

Selection is via the ``RLS_PROVIDER`` env var (default ``simulated``).

Synthetic-only, no PHI (ADR-0016).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

Row = dict[str, Any]


class RlsProviderError(PermissionError):
    """Raised deny-by-default when a read cannot be safely scoped.

    Covers an ungrounded read (missing hospital scope or caller oid) and a live
    provider that cannot yet enforce per-user structured scope (no OBO token).
    Maps to HTTP 401 at the endpoint.
    """


@dataclass(frozen=True)
class ScopeDecision:
    """The rows a caller may see plus the provenance of that decision."""

    rows: list[Row]
    scope: str
    provider: str
    provenance: str


@runtime_checkable
class RlsProvider(Protocol):
    provider: str
    provenance: str

    def scope(self, rows: list[Row], *, hospital_scope: str, user_oid: str) -> ScopeDecision:
        ...


def _require_grounding(hospital_scope: str, user_oid: str) -> None:
    """Deny-by-default: a read must be grounded by a proven scope and caller oid."""
    if not hospital_scope or not user_oid:
        raise RlsProviderError(
            "golden read requires a proven hospital scope and caller oid"
        )


def _filter_rows(rows: list[Row], hospital_scope: str) -> list[Row]:
    """Aggregated => all rows; a site scope => rows tagged that site + untagged."""
    if hospital_scope == "aggregated":
        return list(rows)
    return [row for row in rows if row.get("hospital") in (None, hospital_scope)]


class SimulatedRlsProvider:
    """Rung 0 (default): synthetic in-agent-host row filtering. Provenance simulated."""

    provider = "simulated"
    provenance = "simulated"

    def scope(self, rows: list[Row], *, hospital_scope: str, user_oid: str) -> ScopeDecision:
        _require_grounding(hospital_scope, user_oid)
        return ScopeDecision(
            rows=_filter_rows(rows, hospital_scope),
            scope=hospital_scope,
            provider=self.provider,
            provenance=self.provenance,
        )


class FabricDataAgentRlsProvider:
    """Rung 1: reuse the proven live Fabric Data Agent client (da_hospital_capacity).

    The Data Agent already enforces the Direct-Lake semantic model's RLS + the
    ADR-0016 PHI gate (proven live). But it enforces at **model/MI scope** because
    the agent-host authenticates with its managed identity, and the deployed roles
    carry no dynamic per-user row predicate. Per-user *structured* row scope is
    therefore gated on an OBO token (M5) **and** a dynamic-RLS TMDL change. Until
    both land, this provider refuses the structured read rather than pass MI-scoped
    rows off as the caller's.
    """

    provider = "fabric-data-agent"
    provenance = "live"

    def __init__(self, *, client: Any, obo_token: str | None = None):
        self.client = client
        self._obo_token = obo_token

    def scope(self, rows: list[Row], *, hospital_scope: str, user_oid: str) -> ScopeDecision:
        _require_grounding(hospital_scope, user_oid)
        if not self._obo_token:
            raise RlsProviderError(
                "FabricDataAgentRlsProvider cannot enforce per-user structured RLS "
                "without an OBO token: the agent-host queries Fabric under its "
                "managed identity (model/MI scope). Live model RLS + PHI are "
                "enforced on the /chat grounding path via the Fabric Data Agent; "
                "per-user structured scope lands at #424 M5 (OBO + dynamic-RLS TMDL)."
            )
        # TODO(#424 M5): with the user's OBO token and the dynamic-RLS TMDL
        # predicate in place, run the Direct-Lake read on-behalf-of the user and
        # return the live per-user rows with provenance="live".
        raise RlsProviderError(
            "live per-user structured Fabric RLS not wired until #424 M5 "
            "(OBO token present, dynamic-RLS TMDL predicate pending)"
        )


def build_rls_provider(
    *, data_agent_client: Any | None = None, obo_token: str | None = None
) -> RlsProvider:
    """Select the RLS provider via ``RLS_PROVIDER`` (default ``simulated``).

    ``fabric-data-agent`` requires the proven Data Agent client to be injected;
    selecting it without one is a misconfiguration and raises rather than build a
    provider that denies every read.
    """
    choice = (os.getenv("RLS_PROVIDER") or "simulated").strip().lower()
    if choice in ("fabric-data-agent", "fabric"):
        if data_agent_client is None:
            raise RlsProviderError(
                "RLS_PROVIDER=fabric-data-agent requires the live Fabric Data Agent "
                "client to be injected (available once FABRIC_DATA_AGENT_* is set)"
            )
        return FabricDataAgentRlsProvider(client=data_agent_client, obo_token=obo_token)
    return SimulatedRlsProvider()
