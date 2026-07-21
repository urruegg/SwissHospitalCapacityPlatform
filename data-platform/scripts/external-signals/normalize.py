"""Normalize raw source payloads into DC-EXT-SIGNAL-v1 records (stdlib-only)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

CONTRACT_ID = "DC-EXT-SIGNAL-v1"
CONTRACT_VERSION = "1.0.0"


def raw_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def dedup_key(rec: dict) -> str:
    cantons = ",".join(sorted((rec.get("region") or {}).get("cantons", [])))
    parts = [
        rec.get("sourceId", ""), rec.get("capIdentifier") or "",
        rec.get("hazardType", ""), cantons, rec.get("onset", ""),
    ]
    return "|".join(parts)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_record(*, signal_id, source_id, source_authority, hazard_type,
                 severity, certainty, urgency, region, onset, status,
                 connector_version, licence, raw,
                 cap_identifier=None, danger_level=None, effective=None,
                 expires=None, uri=None, mapped_scenario_template=None,
                 default_lage_tier=None, trust_tier="A") -> dict:
    return {
        "signalId": signal_id,
        "sourceId": source_id,
        "sourceAuthority": source_authority,
        "trustTier": trust_tier,
        "capIdentifier": cap_identifier,
        "hazardType": hazard_type,
        "severity": severity,
        "certainty": certainty,
        "urgency": urgency,
        "dangerLevel": danger_level,
        "region": region,
        "effective": effective,
        "onset": onset,
        "expires": expires,
        "uri": uri,
        "status": status,
        "mappedScenarioTemplate": mapped_scenario_template,
        "defaultLageTier": default_lage_tier,
        "provenance": {
            "ingestedAt": _now(),
            "connectorVersion": connector_version,
            "licence": licence,
            "rawHash": raw_hash(raw if isinstance(raw, bytes) else json.dumps(raw, sort_keys=True).encode()),
        },
    }


def envelope(records: list[dict], dataset_id: str, residency: str = "CH") -> dict:
    return {
        "datasetId": dataset_id,
        "contractId": CONTRACT_ID,
        "contractVersion": CONTRACT_VERSION,
        "classification": "public-authority",
        "residency": residency,
        "purposeTags": ["crisis-trigger", "situational-awareness"],
        "records": records,
    }
