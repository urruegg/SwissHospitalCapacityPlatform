from __future__ import annotations

from datetime import datetime, timezone


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_thin_demand_envelope() -> dict:
    now = _utc_now_iso()
    return {
        "datasetId": "DS-DEMAND-ENC-sit-thin",
        "contractId": "DC-DEMAND-ENCOUNTER-v1",
        "contractVersion": "1.0.0",
        "classification": "operational-confidential",
        "residency": "CH",
        "purposeTags": ["capacity-planning"],
        "records": [
            {
                "contractId": "DC-DEMAND-ENCOUNTER-v1",
                "encounterId": "ENC-2026-9001",
                "pseudonymId": "PID-1234ABCD",
                "organizationId": "ORG-HIRSLANDEN",
                "class": "IMP",
                "status": "planned",
                "admissionType": "elective",
                "requestedSpecialtyServiceId": "HCS-ONCOLOGY-0205",
                "requiredCharacteristics": [],
                "acuityBand": "routine",
                "expectedArrivalTimestamp": "2026-06-21T10:00:00Z",
                "expectedLOSDays": 2,
                "statusHistory": [
                    {
                        "status": "planned",
                        "periodStart": "2026-06-21T10:00:00Z",
                        "periodEnd": None,
                        "locationId": None,
                    }
                ],
                "purposeTag": "capacity-planning",
                "dataResidencyRegion": "switzerlandnorth",
                "asOfTimestamp": now,
            }
        ],
    }
