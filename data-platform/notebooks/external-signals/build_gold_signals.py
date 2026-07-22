"""Sprint 21 M3 — Gold projection for the Trusted External Signals lane.

Projects clean Silver DC-EXT-SIGNAL-v1 records onto the star-schema Gold layer
that the forecast overlay + semantic model consume: a ``gold.ext_fact_signal``
fact plus ``gold.ext_dim_source`` / ``gold.ext_dim_hazard_type`` /
``gold.ext_dim_region`` dimensions. Column names are prefixed ``ext_`` to keep
the external-signal spine distinct from the internal capacity gold tables.

The pure functions here are unit-tested without Spark (see
``tests/test_signals_pure.py``), following the CSA notebook pattern.
"""
from __future__ import annotations

import sys


def to_gold_signal(rec: dict) -> dict:
    """Project one Silver signal record onto a ``gold.ext_fact_signal`` row."""
    return {
        "ext_signal_id": rec.get("signalId"),
        "ext_source_id": rec.get("sourceId"),
        "ext_hazard_type": rec.get("hazardType"),
        "ext_severity": rec.get("severity"),
        "ext_scenario_template": rec.get("mappedScenarioTemplate"),
        "ext_lage_tier": rec.get("defaultLageTier"),
        "ext_cantons": list((rec.get("region") or {}).get("cantons", [])),
        "ext_onset": rec.get("onset"),
        "ext_status": rec.get("status"),
    }


def to_gold_dims(records: list[dict]) -> dict[str, list[dict]]:
    """Derive the three Gold dimensions from a batch of Silver records."""
    sources: dict[str, dict] = {}
    hazards: dict[str, dict] = {}
    regions: dict[str, dict] = {}
    for rec in records:
        sid = rec.get("sourceId")
        if sid and sid not in sources:
            sources[sid] = {
                "ext_source_id": sid,
                "ext_source_authority": rec.get("sourceAuthority"),
                "ext_trust_tier": rec.get("trustTier"),
            }
        haz = rec.get("hazardType")
        if haz and haz not in hazards:
            hazards[haz] = {
                "ext_hazard_type": haz,
                "ext_scenario_template": rec.get("mappedScenarioTemplate"),
                "ext_default_lage_tier": rec.get("defaultLageTier"),
            }
        for canton in (rec.get("region") or {}).get("cantons", []):
            if canton not in regions:
                regions[canton] = {"ext_canton": canton}
    return {
        "ext_dim_source": [sources[k] for k in sorted(sources)],
        "ext_dim_hazard_type": [hazards[k] for k in sorted(hazards)],
        "ext_dim_region": [regions[k] for k in sorted(regions)],
    }


def run() -> None:  # pragma: no cover - requires a live Fabric Spark session
    """Fabric entrypoint. Reads Silver, writes gold.ext_fact_signal + dims."""
    from pyspark.sql import SparkSession  # noqa: F401 - Fabric-provided

    raise NotImplementedError(
        "run() executes inside the Fabric Spark runtime; the offline seeder is "
        "data-platform/scripts/external-signals/signals_synth.py."
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
