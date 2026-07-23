"""MeteoSwiss warning connector -> DC-EXT-SIGNAL-v1."""
from __future__ import annotations

import json
from normalize import build_record

SOURCE_ID = "meteoswiss"
AUTHORITY = "MeteoSwiss"
LICENCE = "MeteoSwiss-open-government-data"
VERSION = "meteoswiss-2.0.0"
_SCENARIO = {"heat": ("F8", 2), "flood": ("F8", 2)}


def _severity_from_danger_level(level: int) -> str:
    if level >= 5:
        return "Extreme"
    if level >= 4:
        return "Severe"
    if level >= 3:
        return "Moderate"
    return "Minor"


def parse(payload: dict, *, active_binding: str = "live",
          fell_back_from: str | None = None) -> list[dict]:
    out = []
    for warning in payload.get("warnings", []):
        hazard = warning.get("hazard", "heat").lower()
        danger_level = int(warning.get("dangerLevel", 1))
        scenario, tier = _SCENARIO.get(hazard, (None, None))
        out.append(build_record(
            signal_id=warning["warningId"], source_id=SOURCE_ID,
            source_authority=AUTHORITY, hazard_type=hazard,
            severity=_severity_from_danger_level(danger_level),
            certainty="Likely", urgency="Expected",
            region={"cantons": warning.get("cantons", [])},
            effective=warning.get("effective"), onset=warning["onset"],
            expires=warning.get("expires"), status="Actual",
            connector_version=VERSION, licence=LICENCE,
            raw=json.dumps(warning, sort_keys=True).encode(),
            uri=warning.get("uri"), danger_level=danger_level,
            mapped_scenario_template=scenario, default_lage_tier=tier,
            active_binding=active_binding, fell_back_from=fell_back_from,
            channel_kind="external",
        ))
    return out
