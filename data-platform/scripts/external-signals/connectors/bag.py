"""FOPH/BAG respiratory surveillance connector -> DC-EXT-SIGNAL-v1."""
from __future__ import annotations

import json
from connectors.base_connector import BaseConnector
from normalize import build_record


def _severity_from_incidence(incidence: float, threshold: float) -> str:
    if incidence >= threshold * 3:
        return "Extreme"
    if incidence >= threshold * 2:
        return "Severe"
    if incidence >= threshold:
        return "Moderate"
    return "Minor"


class BagConnector(BaseConnector):
    source_id = "bag"
    source_authority = "FOPH/BAG"
    licence = "FOPH-open-government-data"
    version = "bag-1.0.0"

    def parse(self, payload: dict) -> list[dict]:
        out = []
        for report in payload.get("reports", []):
            hazard = "rsv" if report.get("indicator", "").lower() == "rsv" else "epidemic"
            incidence = float(report.get("incidencePer100k", 0))
            threshold = float(report.get("thresholdPer100k", 1))
            scenario, tier = self.scenario_for(hazard)
            out.append(build_record(
                signal_id=report["reportId"], source_id=self.source_id,
                source_authority=self.source_authority, hazard_type=hazard,
                severity=_severity_from_incidence(incidence, threshold),
                certainty="Observed", urgency="Expected",
                region={"cantons": report.get("cantons", [])},
                effective=report.get("publishedAt"), onset=report["weekStart"],
                status="Actual" if incidence >= threshold else "System",
                connector_version=self.version, licence=self.licence,
                raw=json.dumps(report, sort_keys=True).encode(),
                uri=report.get("uri"),
                mapped_scenario_template=scenario, default_lage_tier=tier,
            ))
        return out
