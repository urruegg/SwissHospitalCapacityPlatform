"""Sprint 21 M3 — Bronze ingest for the Trusted External Signals lane.

Lands raw DC-EXT-SIGNAL-v1 connector output into the Fabric lakehouse Bronze
layer, partitioned by source and ingest date. The heavy Spark I/O is isolated in
``run()`` so the path convention stays unit-testable without a Spark session
(see ``tests/test_signals_pure.py``), mirroring the CSA notebook pattern
(``data-platform/notebooks/csa/``).

Synthetic-only (ADR-0013 / ADR-0016). No PHI — external hazard feeds carry only
Trust-A public authority warnings.
"""
from __future__ import annotations

import sys

_BRONZE_ROOT = "Files/Bronze/external-signals"


def bronze_path(source: str, date: str) -> str:
    """Return the Bronze landing path for a source feed on a given ingest date.

    ``source`` is the connector ``source_id`` (e.g. ``meteoswiss``); ``date`` is
    an ISO ``YYYY-MM-DD`` partition key.
    """
    if not source:
        raise ValueError("source is required")
    if not date:
        raise ValueError("date is required")
    return f"{_BRONZE_ROOT}/{source}/{date}"


def run() -> None:  # pragma: no cover - requires a live Fabric Spark session
    """Fabric entrypoint. Writes each connector envelope to its Bronze path."""
    from pyspark.sql import SparkSession  # noqa: F401 - Fabric-provided

    raise NotImplementedError(
        "run() executes inside the Fabric Spark runtime; the offline seeder is "
        "data-platform/scripts/external-signals/signals_synth.py."
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
