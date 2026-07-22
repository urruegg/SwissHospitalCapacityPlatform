"""Collapse overlapping ExternalSignal records into HazardEvents."""
from __future__ import annotations

from normalize import dedup_key

SEVERITY_RANK = {"Minor": 1, "Moderate": 2, "Severe": 3, "Extreme": 4}


def collapse(records: list[dict]) -> list[dict]:
    """Group by dedup key (minus onset noise handled upstream); one event per hazard/region."""
    groups: dict[tuple, list[dict]] = {}
    for rec in records:
        cantons = tuple(sorted((rec.get("region") or {}).get("cantons", [])))
        key = (rec.get("hazardType"), cantons)
        groups.setdefault(key, []).append(rec)

    events = []
    for (hazard, cantons), recs in groups.items():
        primary = max(recs, key=lambda r: SEVERITY_RANK.get(r["severity"], 0))
        events.append({
            "hazardType": hazard,
            "cantons": list(cantons),
            "severity": primary["severity"],
            "defaultLageTier": primary.get("defaultLageTier"),
            "mappedScenarioTemplate": primary.get("mappedScenarioTemplate"),
            "sources": sorted({r["sourceId"] for r in recs}),
            "signalIds": sorted(r["signalId"] for r in recs),
            "dedupKeys": sorted({dedup_key(r) for r in recs}),
        })
    return events
