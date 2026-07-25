"""Normalize raw skills-event payloads into DC-SKILL-EVENT-v1 records (stdlib-only).

Mirrors ``skills-evidence/normalize.py`` and ``external-signals/normalize.py``: a
``build_event`` factory that fills provenance + the live-vs-simulated badge, and an
``envelope`` wrapper. The ``sourceMode`` (live | simulated) and ``trustTier``
(A | B | C) badge travels in the contract, is preserved through Bronze/Silver, and
surfaces on the gold skill-event fact -- never invented downstream.

The three event kinds are the WS-A4 (design D4) Eventstream lane's narrow set:

* ``credential-expiry``        -- a certification/credential lapsed; ``credentialValid``
  goes ``False`` so downstream stops counting the associated assertion.
* ``consent-grant-or-revoke``  -- a Work-ID consent decision; ``consentAction`` is
  ``grant`` (sets ``workerGln`` + ``consentScope``) or ``revoke`` (both cleared).
* ``newly-confirmed-assertion``-- an employer confirmed a self-declared skill;
  ``confirmed`` is ``True`` (the L0 -> L1 transition).

Synthetic / no-PHI only (ADR-0013 / ADR-0016).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

CONTRACT_ID = "DC-SKILL-EVENT-v1"
CONTRACT_VERSION = "1.0.0"

EVENT_KINDS = ("credential-expiry", "consent-grant-or-revoke", "newly-confirmed-assertion")


def raw_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def dedup_key(rec: dict) -> str:
    """Canonical identity of an event: one event per kind/person/skill/effectiveAt."""
    parts = [
        rec.get("eventKind", ""),
        rec.get("externalSystem", ""),
        rec.get("externalPersonRef", ""),
        rec.get("externalSkillCode", ""),
        rec.get("effectiveAt", ""),
    ]
    return "|".join(parts)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_bytes(raw) -> bytes:
    return raw if isinstance(raw, bytes) else json.dumps(raw, sort_keys=True).encode()


def build_event(*, event_id, event_kind, external_system, source_mode,
                external_person_ref, external_skill_code, effective_at,
                connector_version, licence, raw,
                trust_tier="A", worker_gln=None, external_skill_label=None,
                consent_action=None, consent_scope=None, credential_valid=None,
                confirmed=None) -> dict:
    """Build a single DC-SKILL-EVENT-v1 record.

    ``source_mode`` is the live-vs-simulated badge origin; ``worker_gln`` is the
    GLN promotion key and is present only when Work-ID consent is granted.
    """
    if event_kind not in EVENT_KINDS:
        raise ValueError(f"event_kind {event_kind!r} not in {EVENT_KINDS}")
    return {
        "eventId": event_id,
        "eventKind": event_kind,
        "externalSystem": external_system,
        "sourceMode": source_mode,
        "trustTier": trust_tier,
        "externalPersonRef": external_person_ref,
        "workerGln": worker_gln,
        "externalSkillCode": external_skill_code,
        "externalSkillLabel": external_skill_label,
        "consentAction": consent_action,
        "consentScope": consent_scope,
        "credentialValid": credential_valid,
        "confirmed": confirmed,
        "effectiveAt": effective_at,
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
