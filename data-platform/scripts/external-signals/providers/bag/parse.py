"""FOPH/BAG respiratory surveillance connector -> DC-EXT-SIGNAL-v1."""
from __future__ import annotations

import json
from normalize import build_record

SOURCE_ID = "bag"
AUTHORITY = "FOPH/BAG"
LICENCE = "BAG-open-data"
VERSION = "bag-2.0.0"
_SCENARIO = {"rsv": ("F6", 2), "epidemic": ("F6", 2)}


def _severity_from_incidence(incidence: float, threshold: float) -> str:
    if incidence >= threshold * 3:
        return "Extreme"
    if incidence >= threshold * 2:
        return "Severe"
    if incidence >= threshold:
        return "Moderate"
    return "Minor"


def parse(payload: dict, *, active_binding: str = "live",
          fell_back_from: str | None = None) -> list[dict]:
    out = []
    for report in payload.get("reports", []):
        hazard = "rsv" if report.get("indicator", "").lower() == "rsv" else "epidemic"
        incidence = float(report.get("incidencePer100k", 0))
        threshold = float(report.get("thresholdPer100k", 1))
        scenario, tier = _SCENARIO.get(hazard, (None, None))
        out.append(build_record(
            signal_id=report["reportId"], source_id=SOURCE_ID,
            source_authority=AUTHORITY, hazard_type=hazard,
            severity=_severity_from_incidence(incidence, threshold),
            certainty="Observed", urgency="Expected",
            region={"cantons": report.get("cantons", [])},
            effective=report.get("publishedAt"), onset=report["weekStart"],
            status="Actual" if incidence >= threshold else "System",
            connector_version=VERSION, licence=LICENCE,
            raw=json.dumps(report, sort_keys=True).encode(),
            uri=report.get("uri"),
            mapped_scenario_template=scenario, default_lage_tier=tier,
            active_binding=active_binding, fell_back_from=fell_back_from,
            channel_kind="external",
        ))
    return out
