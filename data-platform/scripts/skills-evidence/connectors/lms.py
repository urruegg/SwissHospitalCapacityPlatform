"""LMS (learning / certification) connector -> DC-SKILL-EVIDENCE-v1 (simulated).

Course / certification completions from the learning store are employer-confirmed
(L1). Real LMS export mechanics are ``[confirm with vendor]``.
"""
from __future__ import annotations

import json

from connectors.base_connector import BaseConnector
from normalize import build_record


class LmsConnector(BaseConnector):
    source_id = "lms"
    source_authority = "Learning Management System"
    external_system = "lms"
    licence = "synthetic"
    version = "lms-1.0.0"
    source_mode = "simulated"
    trust_tier = "A"

    def parse(self, payload: dict) -> list[dict]:
        out: list[dict] = []
        for row in payload.get("completions", []):
            out.append(build_record(
                evidence_id=row["completionId"],
                external_system=self.external_system,
                source_mode=self.source_mode,
                trust_tier=self.trust_tier,
                external_person_ref=row["learnerRef"],
                external_skill_code=row["courseCode"],
                external_skill_label=row["courseTitle"],
                self_or_confirmed="employer_confirmed",
                external_level=row.get("result"),
                captured_at=row["completedOn"],
                connector_version=self.version,
                licence=self.licence,
                raw=json.dumps(row, sort_keys=True).encode(),
            ))
        return out
