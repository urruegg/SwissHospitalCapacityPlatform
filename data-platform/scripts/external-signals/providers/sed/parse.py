"""SED FDSN earthquake connector -> DC-EXT-SIGNAL-v1."""
from __future__ import annotations

import json
from normalize import build_record

SOURCE_ID = "sed"
AUTHORITY = "SED-ETH"
LICENCE = "SED-ETH-open-data"
VERSION = "sed-2.0.0"


def _severity_from_magnitude(mag: float) -> str:
    if mag >= 6.0:
        return "Extreme"
    if mag >= 5.0:
        return "Severe"
    if mag >= 4.0:
        return "Moderate"
    return "Minor"


def parse(payload: dict, *, active_binding: str = "live",
          fell_back_from: str | None = None) -> list[dict]:
    out = []
    for ev in payload.get("events", []):
        mag = float(ev.get("magnitude", 0.0))
        out.append(build_record(
            signal_id=ev["eventId"], source_id=SOURCE_ID,
            source_authority=AUTHORITY, hazard_type="earthquake",
            severity=_severity_from_magnitude(mag), certainty="Observed",
            urgency="Immediate", region={"cantons": ev.get("cantons", [])},
            effective=ev.get("time"), onset=ev.get("time"),
            expires=ev.get("expires"), status="Actual",
            connector_version=VERSION, licence=LICENCE,
            raw=json.dumps(ev, sort_keys=True).encode(), uri=ev.get("uri"),
            danger_level=None, mapped_scenario_template="F1", default_lage_tier=3,
            active_binding=active_binding, fell_back_from=fell_back_from,
            channel_kind="external",
        ))
    return out
