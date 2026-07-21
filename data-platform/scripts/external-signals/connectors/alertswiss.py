"""Alertswiss CAP connector -> DC-EXT-SIGNAL-v1."""
from __future__ import annotations

import json
from connectors.base_connector import BaseConnector
from normalize import build_record


def _hazard_from_cap(value: str) -> str:
    label = (value or "").strip().lower()
    if label in {"heat", "flood", "earthquake", "epidemic", "rsv", "mci"}:
        return label
    return "mci"


class AlertswissConnector(BaseConnector):
    source_id = "alertswiss"
    source_authority = "BABS/FOCP"
    licence = "Alertswiss-public"
    version = "alertswiss-1.0.0"

    def parse(self, payload: dict) -> list[dict]:
        out = []
        for alert in payload.get("alerts", []):
            hazard = _hazard_from_cap(alert.get("hazard", ""))
            scenario, tier = self.scenario_for(hazard)
            out.append(build_record(
                signal_id=alert["identifier"], source_id=self.source_id,
                source_authority=self.source_authority, hazard_type=hazard,
                severity=alert.get("severity", "Moderate"),
                certainty=alert.get("certainty", "Likely"),
                urgency=alert.get("urgency", "Expected"),
                region={"cantons": alert.get("cantons", [])},
                effective=alert.get("effective"), onset=alert["onset"],
                expires=alert.get("expires"), status=alert.get("status", "Actual"),
                connector_version=self.version, licence=self.licence,
                raw=json.dumps(alert, sort_keys=True).encode(),
                uri=alert.get("uri"), cap_identifier=alert.get("identifier"),
                mapped_scenario_template=scenario, default_lage_tier=tier,
            ))
        return out
