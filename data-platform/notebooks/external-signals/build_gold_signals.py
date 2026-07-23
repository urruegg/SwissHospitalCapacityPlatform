"""Sprint 21 M3 - Gold projection for the Trusted External Signals lane.

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


_DATA_MODE = {"live": "Live", "simulated": "Simulated", "internal": "Internal"}


def data_mode_for(active_binding: str) -> str:
    """Map a provenance active binding to its display trust-badge data mode."""
    return _DATA_MODE[active_binding]


def ext_dim_source_row(rec: dict) -> dict:
    """Build one gold.ext_dim_source row, carrying the trust badge."""
    prov = rec.get("provenance", {})
    binding = prov.get("activeBinding", "live")
    return {
        "ext_source_id": rec.get("sourceId"),
        "ext_source_authority": rec.get("sourceAuthority"),
        "ext_trust_tier": rec.get("trustTier"),
        "ext_data_mode": data_mode_for(binding),
        "ext_fell_back_from": prov.get("fellBackFrom"),
        "ext_last_live_at": prov.get("ingestedAt") if binding == "live" else None,
    }


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
    source_seen_at: dict[str, str] = {}
    hazards: dict[str, dict] = {}
    regions: dict[str, dict] = {}
    for rec in records:
        sid = rec.get("sourceId")
        if sid:
            ingested = (rec.get("provenance") or {}).get("ingestedAt") or ""
            if sid not in sources or ingested >= source_seen_at.get(sid, ""):
                sources[sid] = ext_dim_source_row(rec)
                source_seen_at[sid] = ingested
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
