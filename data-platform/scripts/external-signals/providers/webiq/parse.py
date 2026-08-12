"""Microsoft Web IQ result set -> DC-EXT-SIGNAL-v1 records (Trust-B, stdlib-only).

Web content is UNTRUSTED (NFR-SIG-001, ADR-0060): only typed fields are
extracted, never free text forwarded into a tool/query. Trust-B never arms a
lever or auto-triggers CSA - that is enforced downstream by trigger_rules' trust
-tier gate; this module only normalizes and attaches grounded web citations.
"""
from __future__ import annotations

import json
import re

from normalize import build_record

SOURCE_ID = "webiq"
AUTHORITY = "Microsoft Web IQ"
LICENCE = "microsoft-web-iq-preview-terms"
VERSION = "microsoft-webiq-1.0.0"
_TRIGGER_CONFIDENCE = 0.6
# Hospital-service-relevant hazards only (Sprint 44 Q1): each maps to the CSA
# ScenarioTemplate the matching Trust-A authority feed uses, so a Web IQ signal
# corroborates rather than contradicts (epidemic->BAG F6, heat->MeteoSwiss F8,
# air-quality->NABEL F8, mass-casualty->trauma F3).
_SCENARIO = {"epidemic": ("F6", 2), "heat": ("F8", 2),
             "mass-casualty": ("F3", 3), "air-quality": ("F8", 1)}
# ADR-0016: outbound Web IQ queries must never carry PHI-shaped terms.
_PHI_PATTERNS = [
    re.compile(p, re.I) for p in (r"\bpatient\b", r"\bahv\b", r"\d{3}\.\d{4}", r"\bname\b")
]


def build_query(terms: list[str]) -> str:
    """Assemble an outbound Web IQ query, refusing any PHI-shaped term."""
    joined = " ".join(terms)
    for pat in _PHI_PATTERNS:
        if pat.search(joined):
            raise ValueError("REFUSE: phi-in-webiq-query")
    return joined


def _severity_from_confidence(conf: float) -> str:
    if conf >= 0.85:
        return "Severe"
    if conf >= 0.6:
        return "Moderate"
    return "Minor"


def parse(payload: dict, *, active_binding: str = "live",
          fell_back_from: str | None = None) -> list[dict]:
    out = []
    for i, res in enumerate(payload.get("results", [])):
        conf = float(res.get("confidence", 0.0))
        hazard = str(res.get("hazard", "public-health")).lower()
        scenario, tier = _SCENARIO.get(hazard, (None, None))
        # Below-threshold web results are quarantined (never Actual -> never trigger).
        status = "Actual" if conf >= _TRIGGER_CONFIDENCE else "System"
        rec = build_record(
            signal_id=f"webiq-{i}-{res.get('uri', '')}", source_id=SOURCE_ID,
            source_authority=AUTHORITY, hazard_type=hazard,
            severity=_severity_from_confidence(conf),
            certainty="Possible", urgency="Future",
            region={"cantons": res.get("cantons", [])},
            onset=res.get("publishedAt"), effective=res.get("publishedAt"),
            status=status, connector_version=VERSION, licence=LICENCE,
            raw=json.dumps(res, sort_keys=True).encode(),
            uri=res.get("uri"), mapped_scenario_template=scenario,
            default_lage_tier=tier, trust_tier="B",
            active_binding=active_binding, fell_back_from=fell_back_from,
            channel_kind="external",
        )
        rec["webCitations"] = [{
            "title": res.get("title", ""), "uri": res.get("uri", ""),
            "publishedAt": res.get("publishedAt", ""), "snippet": res.get("snippet", ""),
        }]
        out.append(rec)
    return out
