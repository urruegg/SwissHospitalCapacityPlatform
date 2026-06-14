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


ALGORITHM_ID      = "stub-rules-v1"
ALGORITHM_VERSION = "1.0.0"
STALENESS_MIN     = 30


def _bed_fit_factors(bed: dict) -> list[str]:
    factors = []
    chars = bed.get("characteristic", [])
    if "single-room" in chars:
        factors.append("single-room-available")
    if "cardiac-monitoring" in chars:
        factors.append("monitoring-equipped")
    if "isolation" in chars or "negative-pressure" in chars:
        factors.append("isolation-capable")
    if "bariatric" in chars:
        factors.append("bariatric-equipped")
    return factors or ["last-cleaned-within-2h"]


def _score_station(ward: dict, encounter: dict) -> tuple[float, list[dict]]:
    """Deterministic scoring -- not an algorithm commitment."""
    specialty_match = ward["specialtyServiceIds"][0] == encounter["requestedSpecialtyServiceId"]
    headroom_norm = min(ward.get("bedsAvailable", 0) / max(ward.get("bedsTotal", 1), 1), 1.0)
    required = set(encounter.get("requiredCharacteristics", []))
    char_match = 1.0 if not required else (1.0 if required.issubset({"isolation", "cardiac-monitoring", "single-room"}) else 0.5)
    weights = [
        ("specialty-match",      0.5 if specialty_match else 0.0),
        ("capacity-headroom",    0.3 * headroom_norm),
        ("characteristic-match", 0.2 * char_match),
    ]
    total = sum(w for _, w in weights) or 1.0
    norm = [{"factor": f, "weight": round(w / total, 4)} for f, w in weights]
    return round(total, 4), norm


def build_recommendations(cfg: GeneratorConfig, bundle: dict) -> list[dict]:
    locs = bundle["locations"]
    org_emits_beds = {l["organizationId"] for l in locs if l["physicalType"] == "bd"}
    wards_by_org: dict[str, list[dict]] = {}
    beds_by_ward: dict[str, list[dict]] = {}
    for loc in locs:
        if loc["physicalType"] == "wa":
            wards_by_org.setdefault(loc["organizationId"], []).append(loc)
        elif loc["physicalType"] == "bd":
            beds_by_ward.setdefault(loc["partOfId"], []).append(loc)
    gen_at = _dt.datetime.strptime(cfg.as_of.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
    valid_until = gen_at + _dt.timedelta(minutes=STALENESS_MIN)
    results: list[dict] = []
    for enc in bundle["encounters"]:
        org_id = enc["organizationId"]
        candidate_wards = [w for w in wards_by_org.get(org_id, [])
                           if w["specialtyServiceIds"][0] == enc["requestedSpecialtyServiceId"]]
        if not candidate_wards:
            continue
        considered_ids = [w["locationId"] for w in candidate_wards]
        scored = [(w, *_score_station(w, enc)) for w in candidate_wards]
        scored.sort(key=lambda t: t[1], reverse=True)
        top = scored[:5]
        arrival = _dt.datetime.strptime(enc["expectedArrivalTimestamp"].rstrip("Z"),
                                        "%Y-%m-%dT%H:%M:%S")
        candidates = []
        for rank, (ward, score, factors) in enumerate(top, start=1):
            bed = None
            if org_id in org_emits_beds:
                available = [b for b in beds_by_ward.get(ward["locationId"], [])
                             if b.get("operationalStatus") == "U"]
                bed = available[0] if available else beds_by_ward.get(ward["locationId"], [None])[0]
            candidate = {
                "rank": rank,
                "stationLocationId": ward["locationId"],
                "recommendedBedLocationId": bed["locationId"] if bed else None,
                "fitScore": score,
                "capacityHeadroom": ward.get("bedsAvailable", 0),
                "expectedAdmitWindowStart": _iso(arrival),
                "expectedAdmitWindowEnd": _iso(arrival + _dt.timedelta(hours=6)),
                "explanationFactors": factors,
                "hardConstraintsMet": True,
            }
            if bed:
                candidate["bedFitFactors"] = _bed_fit_factors(bed)
            candidates.append(candidate)
        if not candidates:
            continue
        results.append({
            "contractId": "DC-MATCH-RECOMMENDATION-v1",
            "recommendationId": f"REC-{cfg.as_of}-{enc['encounterId']}",
            "encounterId": enc["encounterId"],
            "organizationId": org_id,
            "generatedAt": cfg.as_of,
            "validUntil": _iso(valid_until),
            "algorithmId": ALGORITHM_ID,
            "algorithmVersion": ALGORITHM_VERSION,
            "status": "advisory",
            "dataResidencyRegion": enc["dataResidencyRegion"],
            "inputSnapshot": {
                "encounterAsOf": enc["asOfTimestamp"],
                "supplyAsOf":    cfg.as_of,
                "consideredStationIds": considered_ids,
            },
            "candidates": candidates,
        })
    return results


def build_manifest(cfg: GeneratorConfig, bundle: dict) -> dict:
    return {
        "manifestVersion": "1.0.0",
        "generatedAt": cfg.as_of,
        "seed": cfg.seed,
        "config": asdict(cfg),
        "counts": {k: len(v) for k, v in bundle.items()},
        "checksums": {
            k: hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()
            for k, v in bundle.items()
        },
    }


def _wrap_dataset(records: list[dict], contract_id: str,
                  dataset_id: str, ds_prefix: str) -> dict:
    payload = {
        "datasetId": dataset_id,
        "contractId": contract_id,
        "contractVersion": CONTRACT_VERSION,
        "classification": "operational-confidential",
        "residency": "CH",
        "records": records,
    }
    if contract_id in ("DC-DEMAND-ENCOUNTER-v1", "DC-MATCH-RECOMMENDATION-v1"):
        payload["purposeTags"] = ["capacity-planning", "bed-management"]
    return payload


def write_datasets(cfg: GeneratorConfig, out_dir: str) -> dict:
    bundle = build_bundle(cfg)
    bundle["recommendations"] = build_recommendations(cfg, bundle)
    os.makedirs(out_dir, exist_ok=True)
    plan = [
        ("dc-supply-organization-v1.sample.json",
         "DC-SUPPLY-ORGANIZATION-v1",
         "DS-SUPPLY-ORG-sit-2026-06-12", bundle["organizations"]),
        ("dc-supply-location-v1.sample.json",
         "DC-SUPPLY-LOCATION-v1",
         "DS-SUPPLY-LOC-sit-2026-06-12", bundle["locations"]),
        ("dc-demand-encounter-v1.sample.json",
         "DC-DEMAND-ENCOUNTER-v1",
         "DS-DEMAND-ENC-sit-2026-06-12", bundle["encounters"]),
        ("dc-match-recommendation-v1.sample.json",
         "DC-MATCH-RECOMMENDATION-v1",
         "DS-MATCH-REC-sit-2026-06-12", bundle["recommendations"]),
    ]
    for fname, contract_id, ds_id, records in plan:
        payload = _wrap_dataset(records, contract_id, ds_id, "")
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=False)
            fh.write("\n")
    manifest = build_manifest(cfg, bundle)
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=False)
        fh.write("\n")
    return manifest


def _parse_args(argv: list[str] | None = None) -> GeneratorConfig:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--organizations",     type=int,  default=2)
    p.add_argument("--sites-per-org",     type=int,  default=2)
    p.add_argument("--stations-per-site", type=int,  default=6)
    p.add_argument("--beds-per-station",  type=int,  default=12)
    p.add_argument("--with-beds",         action="store_true")
    p.add_argument("--encounters",        type=int,  default=500)
    p.add_argument("--horizon-days",      type=int,  default=14)
    p.add_argument("--seed",              type=int,  default=42)
    p.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "datasets"))
    args = p.parse_args(argv)
    cfg = GeneratorConfig(
        organizations=args.organizations,
        sites_per_org=args.sites_per_org,
        stations_per_site=args.stations_per_site,
        beds_per_station=args.beds_per_station,
        with_beds=args.with_beds,
        encounters=args.encounters,
        horizon_days=args.horizon_days,
        seed=args.seed,
    )
    cfg.__dict__["_out_dir"] = args.out
    return cfg


def main(argv: list[str] | None = None) -> int:
    cfg = _parse_args(argv)
    out_dir = cfg.__dict__.pop("_out_dir")
    manifest = write_datasets(cfg, out_dir)
    print(json.dumps(manifest["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
