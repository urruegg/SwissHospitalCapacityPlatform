"""SLF avalanche channel -> DC-EXT-SIGNAL-v1 (simulator-backed)."""
from __future__ import annotations

import json
from normalize import build_record

SOURCE_ID = "slf"
AUTHORITY = "SLF"
LICENCE = "SLF-open-data"
VERSION = "slf-1.0.0"
HAZARD = "avalanche"
SCENARIO = "F8"
LAGE_TIER = 2

_VALID_SEVERITY = {"Minor", "Moderate", "Severe", "Extreme"}


def parse(payload: dict, *, active_binding: str = "live",
          fell_back_from: str | None = None) -> list[dict]:
    out = []
    for ev in payload.get("events", []):
        severity = ev.get("severity", "Moderate")
        if severity not in _VALID_SEVERITY:
            severity = "Moderate"
        out.append(build_record(
            signal_id=ev["eventId"], source_id=SOURCE_ID,
            source_authority=AUTHORITY, hazard_type=HAZARD,
            severity=severity, certainty="Likely", urgency="Expected",
            region={"cantons": ev.get("cantons", [])},
            effective=ev.get("time"), onset=ev.get("time"),
            expires=ev.get("expires"), status="Actual",
            connector_version=VERSION, licence=LICENCE,
            raw=json.dumps(ev, sort_keys=True).encode(), uri=ev.get("uri"),
            mapped_scenario_template=SCENARIO, default_lage_tier=LAGE_TIER,
            active_binding=active_binding, fell_back_from=fell_back_from,
            channel_kind="external",
        ))
    return out
