"""SED (ETH seismology) FDSN connector -> DC-EXT-SIGNAL-v1."""
from __future__ import annotations

import json
from connectors.base_connector import BaseConnector
from normalize import build_record


def _severity_from_magnitude(mag: float) -> str:
    if mag >= 6.0:
        return "Extreme"
    if mag >= 5.0:
        return "Severe"
    if mag >= 4.0:
        return "Moderate"
    return "Minor"


class SedConnector(BaseConnector):
    source_id = "sed"
    source_authority = "SED-ETH"
    licence = "ETH-open"
    version = "sed-1.0.0"

    def parse(self, payload: dict) -> list[dict]:
        out = []
        for ev in payload.get("events", []):
            scenario, tier = self.scenario_for("earthquake")
            out.append(build_record(
                signal_id=ev["eventId"], source_id=self.source_id,
                source_authority=self.source_authority, hazard_type="earthquake",
                severity=_severity_from_magnitude(float(ev["magnitude"])),
                certainty="Observed", urgency="Immediate",
                region={"cantons": ev.get("cantons", [])},
                onset=ev["time"], status="Actual",
                connector_version=self.version, licence=self.licence,
                raw=json.dumps(ev, sort_keys=True).encode(),
                uri=ev.get("uri"), danger_level=None,
                mapped_scenario_template=scenario, default_lage_tier=tier,
            ))
        return out
