"""MeteoSwiss warning connector -> DC-EXT-SIGNAL-v1."""
from __future__ import annotations

import json
from connectors.base_connector import BaseConnector
from normalize import build_record


def _severity_from_danger_level(level: int) -> str:
    if level >= 5:
        return "Extreme"
    if level >= 4:
        return "Severe"
    if level >= 3:
        return "Moderate"
    return "Minor"


class MeteoSwissConnector(BaseConnector):
    source_id = "meteoswiss"
    source_authority = "MeteoSwiss"
    licence = "MeteoSwiss-open-government-data"
    version = "meteoswiss-1.0.0"

    def parse(self, payload: dict) -> list[dict]:
        out = []
        for warning in payload.get("warnings", []):
            hazard = warning.get("hazard", "heat").lower()
            danger_level = int(warning.get("dangerLevel", 1))
            scenario, tier = self.scenario_for(hazard)
            out.append(build_record(
                signal_id=warning["warningId"], source_id=self.source_id,
                source_authority=self.source_authority, hazard_type=hazard,
                severity=_severity_from_danger_level(danger_level),
                certainty="Likely", urgency="Expected",
                region={"cantons": warning.get("cantons", [])},
                effective=warning.get("effective"), onset=warning["onset"],
                expires=warning.get("expires"), status="Actual",
                connector_version=self.version, licence=self.licence,
                raw=json.dumps(warning, sort_keys=True).encode(),
                uri=warning.get("uri"), danger_level=danger_level,
                mapped_scenario_template=scenario, default_lage_tier=tier,
            ))
        return out
