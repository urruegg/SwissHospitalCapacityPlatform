"""SuccessFactors HRIS connector -> DC-SKILL-EVIDENCE-v1 (simulated).

SuccessFactors is the authoritative HRIS: every record is employer-confirmed
(L1). Real API mechanics are ``[confirm with vendor]`` and stay behind ``fetch``.
"""
from __future__ import annotations

import json

from connectors.base_connector import BaseConnector
from normalize import build_record


class SuccessFactorsConnector(BaseConnector):
    source_id = "successfactors"
    source_authority = "SuccessFactors HRIS"
    external_system = "successfactors"
    licence = "synthetic"
    version = "successfactors-1.0.0"
    source_mode = "simulated"
    trust_tier = "A"

    def parse(self, payload: dict) -> list[dict]:
        out: list[dict] = []
        for row in payload.get("assignments", []):
            out.append(build_record(
                evidence_id=row["assignmentId"],
                external_system=self.external_system,
                source_mode=self.source_mode,
                trust_tier=self.trust_tier,
                external_person_ref=row["employeeRef"],
                external_skill_code=row["skillCode"],
                external_skill_label=row["skillLabel"],
                self_or_confirmed="employer_confirmed",
                external_level=row.get("proficiency"),
                captured_at=row["effectiveDate"],
                connector_version=self.version,
                licence=self.licence,
                raw=json.dumps(row, sort_keys=True).encode(),
            ))
        return out
