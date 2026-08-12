"""Sprint 44 live path (Slice 2) — gold-shaped signals snapshot for the app.

Projects the runner's ``DC-EXT-SIGNAL-v1`` records into the gold shape the
agent-host golden surface consumes (``ext_fact_signal`` + ``ext_dim_source``
rows), so live signals reach the app via a small Blob snapshot **without** an
OneLake external read (which needs a Fabric tenant-admin setting we lack). See
``docs/superpowers/specs/2026-08-12-webiq-live-signals-without-fabric-admin-design.md``.

Self-contained (the container ships only ``scripts/external-signals/``); a
test-only parity guard asserts the 9 canonical gold columns match
``build_gold_signals.to_gold_signal``. The additive ``ext_web_citations`` column
carries the Trust-B web grounding the canonical Delta projection currently drops.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

_DATA_MODE = {"live": "Live", "simulated": "Simulated", "internal": "Internal"}


def _fact(rec: dict[str, Any]) -> dict[str, Any]:
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
        "ext_web_citations": rec.get("webCitations") or [],
    }


def _source(rec: dict[str, Any]) -> dict[str, Any]:
    prov = rec.get("provenance") or {}
    binding = prov.get("activeBinding", "live")
    return {
        "ext_source_id": rec.get("sourceId"),
        "ext_source_authority": rec.get("sourceAuthority"),
        "ext_trust_tier": rec.get("trustTier"),
        "ext_data_mode": _DATA_MODE.get(binding, "Simulated"),
        "ext_fell_back_from": prov.get("fellBackFrom"),
        "ext_last_live_at": prov.get("ingestedAt") if binding == "live" else None,
    }


def build_snapshot(
    records: list[dict[str, Any]], *, generated_at: str | None = None
) -> dict[str, Any]:
    """Return ``{ext_fact_signal[], ext_dim_source[], generatedAt}`` (latest-wins per source)."""
    sources: dict[str, dict[str, Any]] = {}
    seen_at: dict[str, str] = {}
    for rec in records:
        sid = rec.get("sourceId")
        if not sid:
            continue
        ingested = (rec.get("provenance") or {}).get("ingestedAt") or ""
        if sid not in sources or ingested >= seen_at.get(sid, ""):
            sources[sid] = _source(rec)
            seen_at[sid] = ingested
    return {
        "ext_fact_signal": [_fact(r) for r in records],
        "ext_dim_source": [sources[k] for k in sorted(sources)],
        "generatedAt": generated_at
        or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
