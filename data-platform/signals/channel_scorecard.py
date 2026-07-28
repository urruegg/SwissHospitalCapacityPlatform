"""Sprint 32 SGA — deterministic Channel Readiness Scorecard (design §7, FR-SIG-007).

Sandbox gate before activation: schema conformance, provenance completeness,
dedup. NO network I/O in the scorer — operates on an already-fetched sample.
"""
from __future__ import annotations

from typing import Any, Dict, List


def score_channel(sample: List[Dict[str, Any]], required_fields: List[str]) -> Dict[str, Any]:
    """Return a Channel Readiness Scorecard for a fetched sample."""
    schema_ok = bool(sample) and all(all(f in row and row[f] not in (None, "", []) for f in required_fields) for row in sample)
    provenance_ok = bool(sample) and all(row.get("_provenance", {}).get("sourceAuthority") for row in sample)
    keys = [(row.get("workId"), row.get("credentialType")) for row in sample]
    dedup_ok = len(keys) == len(set(keys))
    ready = schema_ok and provenance_ok and dedup_ok
    return {
        "ready": ready,
        "checks": {"schemaConformant": schema_ok, "provenanceComplete": provenance_ok, "dedupOk": dedup_ok},
        "sampleSize": len(sample),
    }
