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
    return {
        "organizations": build_organizations(cfg),
        "locations":     build_locations(cfg),
        "encounters":    [],
        "recommendations":[],
    }
