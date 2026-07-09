"""Sprint 16 T2 — Fabric Mirroring fallback: Cosmos change-feed → Bronze.

INTENTIONAL STUB. Fabric Mirroring for external Azure Cosmos DB (preview,
``westus2`` demo scope per ADR-0013) is the primary replication path from the
CSA Cosmos account to OneLake — see ``MIRRORING.md``. This Spark job is the
documented **fallback** activated ONLY if Mirroring is blocked at go-live
(sovereign-cloud restriction or preview outage).

Keep this body empty until the fallback is actually needed. When activated, it
reads the Cosmos change feed for the four CSA containers (``scenarios``,
``agent-memory``, ``response-levers``, ``simulation-runs``) and appends to the
Fabric Bronze layer as Delta tables, preserving the same schema Mirroring would
surface.

Publishing / scheduling this notebook is a ``deploy``-class action and requires
an ``approved-to-apply`` comment per AGENTS.md §4.
"""
from __future__ import annotations


def run() -> None:  # pragma: no cover - Fabric Spark runtime + change-feed access
    """Fabric entrypoint — inert until the Mirroring fallback is activated."""
    raise NotImplementedError(
        "Fabric Mirroring is the primary path (see MIRRORING.md). Activate this "
        "change-feed fallback only if Mirroring is blocked at go-live, behind an "
        "approved-to-apply gate (AGENTS.md §4)."
    )


if __name__ == "__main__":  # pragma: no cover
    run()
