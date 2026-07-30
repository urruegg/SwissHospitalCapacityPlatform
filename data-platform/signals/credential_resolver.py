"""Sprint 32 SGA ? deterministic credential->competency resolution + skills enrichment.

Staff-PII safe: operates only on pseudonymised work-IDs (WID-*), never names/AHV
(nDSG; ADR-0016). NO randomness.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

_WID = re.compile(r"^WID-[0-9a-f]{8,}$")


def resolve_competencies(credential_type: str, taxonomy: Dict[str, List[str]]) -> List[str]:
    """Map a credential type to its competency codes (empty if unknown)."""
    return list(taxonomy.get(credential_type, []))


def enrich_skill_tags(
    pool: Dict[str, List[str]],
    credentials: List[Dict[str, Any]],
    taxonomy: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """Merge resolved competencies into the skills baseline, keyed by pseudonymised work-ID."""
    out: Dict[str, List[str]] = {k: list(v) for k, v in pool.items()}
    for cred in credentials:
        wid = cred.get("workId", "")
        if not _WID.match(wid):
            raise ValueError(f"workId must be a pseudonymised WID-*, got {wid!r}")
        merged = set(out.get(wid, [])) | set(resolve_competencies(cred.get("credentialType", ""), taxonomy))
        out[wid] = sorted(merged)
    return out
