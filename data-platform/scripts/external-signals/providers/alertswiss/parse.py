"""Alertswiss CAP connector -> DC-EXT-SIGNAL-v1."""
from __future__ import annotations

import json
from normalize import build_record

SOURCE_ID = "alertswiss"
AUTHORITY = "BABS/FOCP"
LICENCE = "Alertswiss-CAP-open"
VERSION = "alertswiss-2.0.0"
_SCENARIO = {"heat": ("F8", 2), "flood": ("F8", 2), "earthquake": ("F1", 3),
             "epidemic": ("F6", 2), "rsv": ("F6", 2), "mci": ("F3", 3)}


def _hazard_from_cap(value: str) -> str:
    label = (value or "").strip().lower()
    if label in {"heat", "flood", "earthquake", "epidemic", "rsv", "mci"}:
        return label
    return "mci"


def parse(payload: dict, *, active_binding: str = "live",
          fell_back_from: str | None = None) -> list[dict]:
    out = []
    for alert in payload.get("alerts", []):
        hazard = _hazard_from_cap(alert.get("hazard", ""))
        scenario, tier = _SCENARIO.get(hazard, (None, None))
        out.append(build_record(
            signal_id=alert["identifier"], source_id=SOURCE_ID,
            source_authority=AUTHORITY, hazard_type=hazard,
            severity=alert.get("severity", "Moderate"),
            certainty=alert.get("certainty", "Likely"),
            urgency=alert.get("urgency", "Expected"),
            region={"cantons": alert.get("cantons", [])},
            effective=alert.get("effective"), onset=alert["onset"],
            expires=alert.get("expires"), status=alert.get("status", "Actual"),
            connector_version=VERSION, licence=LICENCE,
            raw=json.dumps(alert, sort_keys=True).encode(),
            uri=alert.get("uri"), cap_identifier=alert.get("identifier"),
            mapped_scenario_template=scenario, default_lage_tier=tier,
            active_binding=active_binding, fell_back_from=fell_back_from,
            channel_kind="external",
        ))
    return out
