"""Skills-Manager company-inventory connector -> DC-SKILL-EVIDENCE-v1 (simulated).

Skills-Manager is the employer's skills-inventory cockpit (Step 3). Ingest runs in
one of three connector modes (A = confirmed export, B = read-only discovery,
C = candidate surfacing). Confirmed rows are ``employer_confirmed`` (L1); discovery
/ candidate rows are ``self`` (L0) -- flagged, never auto-counted as safety supply.
All rows sit below the federal evidence floor. ``trust_tier`` is B (review).
"""
from __future__ import annotations

import json

from connectors.base_connector import BaseConnector
from normalize import build_record

# Connector mode -> confirmation source (Step 3 modes A/B/C).
_MODE_CONFIRMATION = {
    "A": "employer_confirmed",  # confirmed export
    "B": "self",                # read-only discovery
    "C": "self",                # candidate surfacing
}


class SkillsManagerConnector(BaseConnector):
    source_id = "skills_manager"
    source_authority = "Skills-Manager (company inventory)"
    external_system = "skills_manager"
    licence = "synthetic"
    version = "skills_manager-1.0.0"
    source_mode = "simulated"
    trust_tier = "B"

    def parse(self, payload: dict) -> list[dict]:
        mode = payload.get("mode", "B")
        confirmation = _MODE_CONFIRMATION.get(mode, "self")
        out: list[dict] = []
        for row in payload.get("inventory", []):
            out.append(build_record(
                evidence_id=row["entryId"],
                external_system=self.external_system,
                source_mode=self.source_mode,
                trust_tier=self.trust_tier,
                external_person_ref=row["personRef"],
                external_skill_code=row["skillCode"],
                external_skill_label=row["skillLabel"],
                self_or_confirmed=confirmation,
                external_level=row.get("level"),
                captured_at=row["capturedAt"],
                connector_version=self.version,
                licence=self.licence,
                raw=json.dumps(row, sort_keys=True).encode(),
            ))
        return out
