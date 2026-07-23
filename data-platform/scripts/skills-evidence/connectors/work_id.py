"""Work-ID worker-passport connector -> DC-SKILL-EVIDENCE-v1 (simulated).

Work-ID is worker-owned and anonymous by default (Step 3 sec 4). Skills are
``self``-declared (L0). The ``worker_gln`` promotion key and ``consent_scope`` are
present ONLY when the worker consented to share and link their GLN -- without
consent the row stays anonymous (no GLN, no promotion above L1). ``trust_tier`` is
C (review). Consent is revocable upstream. Synthetic / no-PHI only.
"""
from __future__ import annotations

import json

from connectors.base_connector import BaseConnector
from normalize import build_record


class WorkIdConnector(BaseConnector):
    source_id = "work_id"
    source_authority = "Work-ID passport"
    external_system = "work_id"
    licence = "synthetic"
    version = "work_id-1.0.0"
    source_mode = "simulated"
    trust_tier = "C"

    def parse(self, payload: dict) -> list[dict]:
        out: list[dict] = []
        for row in payload.get("shares", []):
            consented = bool(row.get("consentGranted"))
            worker_gln = row.get("workerGln") if consented else None
            consent_scope = row.get("consentScope") if consented else None
            out.append(build_record(
                evidence_id=row["shareId"],
                external_system=self.external_system,
                source_mode=self.source_mode,
                trust_tier=self.trust_tier,
                external_person_ref=row["workIdRef"],
                external_skill_code=row["skillCode"],
                external_skill_label=row["skillLabel"],
                self_or_confirmed="self",
                external_level=row.get("selfLevel"),
                worker_gln=worker_gln,
                consent_scope=consent_scope,
                captured_at=row["sharedAt"],
                connector_version=self.version,
                licence=self.licence,
                raw=json.dumps(row, sort_keys=True).encode(),
            ))
        return out
