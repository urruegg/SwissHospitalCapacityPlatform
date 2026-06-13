#!/usr/bin/env python3
"""Sprint 07 planning datasets generator.

Builds four pseudonymised synthetic datasets for the Patient Capacity
Planning data product:

  * DC-SUPPLY-ORGANIZATION-v1
  * DC-SUPPLY-LOCATION-v1   (Site / Ward / Bed, recursive)
  * DC-DEMAND-ENCOUNTER-v1
  * DC-MATCH-RECOMMENDATION-v1  (via a deterministic stub matcher)

Pure Python stdlib; deterministic for a given --seed.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import random
from dataclasses import dataclass, field, asdict


CONTRACT_VERSION = "1.0.0"
TAXONOMY_VERSION = "1.0.0"
RESIDENCY_REGIONS = ("switzerlandnorth", "switzerlandwest")
SPECIALTIES = (
    ("cardiology",    "inpatient"),
    ("orthopedics",   "surgical"),
    ("internal-med",  "inpatient"),
    ("neurology",     "inpatient"),
    ("oncology",      "inpatient"),
    ("rehab",         "rehab"),
)
BED_CHARACTERISTICS = (
    "single-room", "cardiac-monitoring", "isolation",
    "negative-pressure", "bariatric", "pediatric-equipped",
)
OPS_STATUS = ("U", "O", "H", "I", "K", "C")
DEFAULT_ORGS = (
    ("ORG-HIRSLANDEN",    "Klinik Hirslanden",   "CH-ZH", "switzerlandnorth"),
    ("ORG-ZOLLIKERBERG",  "Spital Zollikerberg", "CH-ZH", "switzerlandnorth"),
)


@dataclass
class GeneratorConfig:
    organizations:    int = 2
    sites_per_org:    int = 2
    stations_per_site:int = 6
    beds_per_station: int = 12
    with_beds:        bool = False
    encounters:       int = 500
    horizon_days:     int = 14
    seed:             int = 42
    as_of:            str = "2026-06-12T08:00:00Z"


def _rng(cfg: GeneratorConfig, salt: str) -> random.Random:
    """Deterministic per-purpose RNG so adding new builders never re-shuffles
    earlier ones (avoids fixture churn)."""
    seed = int(hashlib.sha256(f"{cfg.seed}:{salt}".encode()).hexdigest(), 16)
    return random.Random(seed & 0xFFFFFFFF)


def build_organizations(cfg: GeneratorConfig) -> list[dict]:
    records = []
    for org_id, name, canton, region in DEFAULT_ORGS[: cfg.organizations]:
        records.append({
            "contractId": "DC-SUPPLY-ORGANIZATION-v1",
            "organizationId": org_id,
            "name": name,
            "organizationType": "prov",
            "active": True,
            "country": "CH",
            "canton": canton,
            "dataResidencyRegion": region,
        })
    return records


def build_locations(cfg: GeneratorConfig) -> list[dict]:
    rng = _rng(cfg, "locations")
    records: list[dict] = []
    for org_id, _, _, _ in DEFAULT_ORGS[: cfg.organizations]:
        org_short = org_id.split("-", 1)[1][:5]
        for s in range(1, cfg.sites_per_org + 1):
            site_id = f"LOC-{org_short}-SITE-{s:02d}"
            records.append({
                "contractId": "DC-SUPPLY-LOCATION-v1",
                "locationId": site_id,
                "organizationId": org_id,
                "physicalType": "si",
                "partOfId": None,
                "name": f"{org_short} Campus {s}",
                "status": "active",
                "asOfTimestamp": cfg.as_of,
            })
            for w in range(1, cfg.stations_per_site + 1):
                ward_id = f"LOC-{org_short}-WARD-{s:02d}{w:02d}"
                specialty, category = SPECIALTIES[(w - 1) % len(SPECIALTIES)]
                hcs_id = f"HCS-{specialty.upper()}-{s:02d}{w:02d}"
                beds_total = cfg.beds_per_station
                beds_available = rng.randint(0, beds_total)
                records.append({
                    "contractId": "DC-SUPPLY-LOCATION-v1",
                    "locationId": ward_id,
                    "organizationId": org_id,
                    "physicalType": "wa",
                    "partOfId": site_id,
                    "name": f"{specialty.title()} Ward {s}-{w}",
                    "status": "active",
                    "bedsTotal": beds_total,
                    "bedsAvailable": beds_available,
                    "specialtyServiceIds": [hcs_id],
                    "healthcareServices": [{
                        "healthcareServiceId": hcs_id,
                        "specialty": specialty,
                        "specialtyTaxonomyVersion": TAXONOMY_VERSION,
                        "category": category,
                    }],
                    "asOfTimestamp": cfg.as_of,
                })
                if cfg.with_beds:
                    for b in range(1, cfg.beds_per_station + 1):
                        bed_id = f"LOC-{org_short}-BED-{s:02d}{w:02d}{b:03d}"
                        chars = rng.sample(BED_CHARACTERISTICS,
                                           k=rng.randint(0, 2))
                        records.append({
                            "contractId": "DC-SUPPLY-LOCATION-v1",
                            "locationId": bed_id,
                            "organizationId": org_id,
                            "physicalType": "bd",
                            "partOfId": ward_id,
                            "name": f"Bed {s}-{w}-{b}",
                            "status": "active",
                            "operationalStatus": rng.choice(OPS_STATUS),
                            "characteristic": chars,
                            "asOfTimestamp": cfg.as_of,
                        })
    return records


def build_bundle(cfg: GeneratorConfig) -> dict:
    organizations = build_organizations(cfg)
    locations     = build_locations(cfg)
    encounters    = build_encounters(cfg, locations)
    return {
        "organizations":   organizations,
        "locations":       locations,
        "encounters":      encounters,
        "recommendations": [],
    }


ACUITY_WEIGHTS = [("routine", 60), ("urgent", 25), ("asap", 12), ("stat", 3)]
ADMISSION_TYPES = ("emergency", "elective", "transfer", "observation")
PURPOSE_TAGS = ("capacity-planning", "bed-management")


def _weighted_choice(rng: random.Random, weighted: list[tuple[str, int]]) -> str:
    total = sum(w for _, w in weighted)
    pick = rng.randint(1, total)
    cum = 0
    for value, weight in weighted:
        cum += weight
        if pick <= cum:
            return value
    return weighted[-1][0]


def _iso(ts: _dt.datetime) -> str:
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def _pseudonym(rng: random.Random) -> str:
    return f"PID-{rng.randint(0, 0xFFFFFFFF):08X}"


def _build_status_history(rng: random.Random, start: _dt.datetime,
                          admission_type: str
                          ) -> tuple[str, list[dict], str | None]:
    """Lifecycle subsets the spec state machine (§6.3); deterministic for a given RNG state."""
    history: list[dict] = []
    cursor = start - _dt.timedelta(days=2)
    history.append({"status": "planned", "periodStart": _iso(cursor),
                    "periodEnd": _iso(start), "locationId": None})
    cursor = start
    if admission_type == "emergency":
        triage_end = cursor + _dt.timedelta(minutes=rng.randint(15, 60))
        history.append({"status": "arrived", "periodStart": _iso(cursor),
                        "periodEnd": _iso(triage_end), "locationId": None})
        in_progress_start = triage_end + _dt.timedelta(minutes=rng.randint(10, 45))
        history.append({"status": "triaged", "periodStart": _iso(triage_end),
                        "periodEnd": _iso(in_progress_start), "locationId": None})
        cursor = in_progress_start
    else:
        cursor = cursor + _dt.timedelta(minutes=rng.randint(0, 30))
    if rng.random() < 0.7:
        history.append({"status": "in-progress", "periodStart": _iso(cursor),
                        "periodEnd": None, "locationId": None})
        return "in-progress", history, None
    finished_at = cursor + _dt.timedelta(hours=rng.randint(8, 96))
    history.append({"status": "in-progress", "periodStart": _iso(cursor),
                    "periodEnd": _iso(finished_at), "locationId": None})
    history.append({"status": "finished", "periodStart": _iso(finished_at),
                    "periodEnd": None, "locationId": None})
    return "finished", history, None


def build_encounters(cfg: GeneratorConfig, locations: list[dict]) -> list[dict]:
    rng = _rng(cfg, "encounters")
    base = _dt.datetime.strptime(cfg.as_of.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
    services_by_org: dict[str, list[dict]] = {}
    for loc in locations:
        for svc in loc.get("healthcareServices", []):
            services_by_org.setdefault(loc["organizationId"], []).append({
                "id": svc["healthcareServiceId"],
                "wardId": loc["locationId"],
            })
    org_ids = sorted(services_by_org.keys())
    records: list[dict] = []
    for i in range(1, cfg.encounters + 1):
        org_id = rng.choice(org_ids)
        svc = rng.choice(services_by_org[org_id])
        admission_type = rng.choice(ADMISSION_TYPES)
        arrival_offset = rng.randint(0, cfg.horizon_days * 24 * 60)
        arrival = base + _dt.timedelta(minutes=arrival_offset)
        status, history, _ = _build_status_history(rng, arrival, admission_type)
        records.append({
            "contractId": "DC-DEMAND-ENCOUNTER-v1",
            "encounterId": f"ENC-2026-{i:04d}",
            "pseudonymId": _pseudonym(rng),
            "organizationId": org_id,
            "class": "IMP",
            "status": status,
            "admissionType": admission_type,
            "requestedSpecialtyServiceId": svc["id"],
            "requiredCharacteristics": rng.sample(
                ["isolation", "cardiac-monitoring", "single-room"],
                k=rng.randint(0, 1)),
            "acuityBand": _weighted_choice(rng, ACUITY_WEIGHTS),
            "expectedArrivalTimestamp": _iso(arrival),
            "expectedLOSDays": rng.randint(1, 14),
            "statusHistory": history,
            "purposeTag": rng.choice(PURPOSE_TAGS),
            "dataResidencyRegion": "switzerlandnorth",
            "asOfTimestamp": cfg.as_of,
        })
    return records
