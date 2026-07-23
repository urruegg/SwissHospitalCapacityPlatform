"""Normalize raw source payloads into DC-SKILL-EVIDENCE-v1 records (stdlib-only).

Mirrors ``external-signals/normalize.py``: a ``build_record`` factory that fills
provenance + the live-vs-simulated badge, and an ``envelope`` wrapper. The
``sourceMode`` (live | simulated) and ``trustTier`` (A | B | C) badge travels in
the contract, is preserved through Bronze/Silver, and surfaces on
``gold.fact_skill_assertion`` -- never invented downstream.

Synthetic / no-PHI only (ADR-0013 / ADR-0016).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

CONTRACT_ID = "DC-SKILL-EVIDENCE-v1"
CONTRACT_VERSION = "1.0.0"


def raw_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def dedup_key(rec: dict) -> str:
    """Canonical identity of an evidence row: one assertion per person/skill/system."""
    parts = [
        rec.get("externalSystem", ""),
        rec.get("externalPersonRef", ""),
        rec.get("externalSkillCode", ""),
    ]
    return "|".join(parts)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_bytes(raw) -> bytes:
    return raw if isinstance(raw, bytes) else json.dumps(raw, sort_keys=True).encode()


def build_record(*, evidence_id, external_system, source_mode, external_person_ref,
                 external_skill_code, external_skill_label, self_or_confirmed,
                 captured_at, connector_version, licence, raw,
                 trust_tier="A", worker_gln=None, external_level=None,
                 consent_scope=None) -> dict:
    """Build a single DC-SKILL-EVIDENCE-v1 record.

    ``source_mode`` is the live-vs-simulated badge origin; ``worker_gln`` is the
    GLN promotion key and is present only when consent was granted (Work-ID).
    """
    return {
        "evidenceId": evidence_id,
        "externalSystem": external_system,
        "sourceMode": source_mode,
        "trustTier": trust_tier,
        "externalPersonRef": external_person_ref,
        "workerGln": worker_gln,
        "externalSkillCode": external_skill_code,
        "externalSkillLabel": external_skill_label,
        "selfOrConfirmed": self_or_confirmed,
        "externalLevel": external_level,
        "consentScope": consent_scope,
        "capturedAt": captured_at,
        "provenance": {
            "ingestedAt": _now(),
            "connectorVersion": connector_version,
            "licence": licence,
            "rawHash": raw_hash(_as_bytes(raw)),
        },
    }


def envelope(records: list[dict], dataset_id: str, residency: str = "CH") -> dict:
    return {
        "datasetId": dataset_id,
        "contractId": CONTRACT_ID,
        "contractVersion": CONTRACT_VERSION,
        "classification": "personal-synthetic",
        "residency": residency,
        "purposeTags": ["skills-evidence", "workforce-capability"],
        "records": records,
    }
