#!/usr/bin/env python3
"""Deterministic synthetic seed for the eventstream (patient-flow) bronze layer.

Produces the envelope corpus that materialises ``Tables/bronze_eventstream_raw``
so the patient-flow medallion lane (encounter + bed_assignment gold tables)
rebuilds reproducibly from git, with **no** live Eventstream / Event Hub.

The corpus mirrors the streaming simulator's envelope shape (design spec 4.3):
each record carries the 8 canonical columns
``eventKind, eventId, hospitalId, simulatedAt, emittedAt, simRunId, seed,
payload`` and a JSON-**string** payload (silver Gate 1 accepts string payloads;
gold ``_flatten_payload`` reads them via ``get_json_object``).

Design constraints baked in here:

* 7 eventKinds, encounter kinds first so the FK set exists before the
  bed / discharge kinds reference it (silver Gate 3, 5% orphan ceiling).
* All identifiers avoid the silver Gate 2 PHI regex catalogue
  (dob ``\\d{4}-\\d{2}-\\d{2}``, phone ``\\+?\\d[\\d\\s().-]{6,}``, email, AHV)
  in the scanned columns (eventKind / hospitalId / payload). Envelope
  timestamps live only in the allowlisted ``simulatedAt`` / ``emittedAt``
  columns, never inside the payload.
* Fully deterministic: a fixed ``seed`` yields a byte-identical corpus.

Usage::

    python gen_eventstream_seed.py --out data/synthetic/eventstream/eventstream_raw.json
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

CONTRACT_ID = "DC-EVENTSTREAM-RAW-v1"

# (hospitalId, 3-letter short code used inside identifiers). Matches the four
# curavias tenants in data/master-data/capacity/01_dim_hospital.csv.
HOSPITALS = [
    ("H_USZ", "USZ"),
    ("H_LUKS", "LUK"),
    ("H_SZB", "SZB"),
    ("H_HSL", "HSL"),
]

SPECIALTY_SERVICES = [
    "HCS-ONCOLOGY-0205",
    "HCS-CARDIOLOGY-0110",
    "HCS-ORTHOPAEDICS-0308",
    "HCS-NEUROLOGY-0412",
    "HCS-GENSURGERY-0501",
]
ADMISSION_TYPES = ["elective", "emergency", "transfer"]
ENCOUNTER_CLASSES = ["IMP", "AMB"]
WARDS = ["A", "B", "C", "D"]
BED_STATES = ["occupied", "cleaning", "available"]
DISCHARGE_RECOMMENDATIONS = ["discharge-today", "observe-24h", "escalate-care"]

# Fixed synthetic timestamp window (allowlisted columns only, never in payload).
_BASE_DAY = "2027-01-15"


def _iso(hour: int, minute: int) -> str:
    return f"{_BASE_DAY}T{hour:02d}:{minute:02d}:00Z"


def _envelope(kind: str, seq: int, hospital_id: str, sim_min: int,
              payload: dict, seed: int) -> dict:
    # eventId / simRunId are UUID-shaped and silver-allowlisted; keep them
    # digit-light so they never trip PHI regex even if the allowlist changes.
    return {
        "eventKind": kind,
        "eventId": f"evt-{kind.replace('.', '-')}-{seq:05d}",
        "hospitalId": hospital_id,
        "simulatedAt": _iso(8 + (sim_min // 60) % 12, sim_min % 60),
        "emittedAt": _iso(8 + (sim_min // 60) % 12, sim_min % 60),
        "simRunId": f"simrun-{seed:x}-reproducible",
        "seed": seed,
        "payload": json.dumps(payload, sort_keys=True, separators=(",", ":")),
    }


def build_envelopes(n_encounters: int = 200, seed: int = 42) -> list[dict]:
    """Return the deterministic list of eventstream envelopes.

    ``n_encounters`` drives the corpus size; the derived kinds are produced as
    stable fractions of the encounter population so FK integrity always holds.
    """
    rng = random.Random(seed)
    envelopes: list[dict] = []
    encounters: list[tuple[str, str]] = []  # (encounterId, hospitalId)
    sim_min = 0

    # --- encounter.admitted: one per encounter ---------------------------
    for i in range(n_encounters):
        hospital_id, code = HOSPITALS[i % len(HOSPITALS)]
        enc_id = f"ENC-{code}-{i:04d}"
        encounters.append((enc_id, hospital_id))
        payload = {
            "encounterId": enc_id,
            "status": "in-progress",
            "admissionType": rng.choice(ADMISSION_TYPES),
            "class": rng.choice(ENCOUNTER_CLASSES),
            "requestedSpecialtyServiceId": rng.choice(SPECIALTY_SERVICES),
            "expectedLOSDays": rng.randint(1, 21),
        }
        envelopes.append(_envelope("encounter.admitted", i, hospital_id,
                                   sim_min, payload, seed))
        sim_min += 1

    # --- encounter.transitioned: ~60% of encounters change state ---------
    for i, (enc_id, hospital_id) in enumerate(encounters):
        if rng.random() >= 0.6:
            continue
        payload = {
            "encounterId": enc_id,
            "status": rng.choice(["discharged", "transferred"]),
            "previousStatus": "in-progress",
            "admissionType": "n-a",
            "class": "n-a",
            "requestedSpecialtyServiceId": "n-a",
            "expectedLOSDays": 0,
        }
        envelopes.append(_envelope("encounter.transitioned", i, hospital_id,
                                   sim_min, payload, seed))
        sim_min += 1

    # --- bed.state_changed: ~50% of encounters (no FK to encounter) ------
    for i, (_enc_id, hospital_id) in enumerate(encounters):
        if rng.random() >= 0.5:
            continue
        _hid, code = HOSPITALS[i % len(HOSPITALS)]
        ward = rng.choice(WARDS)
        payload = {
            "bedId": f"BED-{code}-{ward}{rng.randint(1, 30):02d}",
            "wardId": f"WARD-{code}-{ward}",
            "state": rng.choice(BED_STATES),
        }
        envelopes.append(_envelope("bed.state_changed", i, hospital_id,
                                   sim_min, payload, seed))
        sim_min += 1

    # --- bed.assigned: ~90% of encounters (FK -> encounter) --------------
    for i, (enc_id, hospital_id) in enumerate(encounters):
        if rng.random() >= 0.9:
            continue
        _hid, code = HOSPITALS[i % len(HOSPITALS)]
        ward = rng.choice(WARDS)
        payload = {
            "encounterId": enc_id,
            "bedId": f"BED-{code}-{ward}{rng.randint(1, 30):02d}",
            "wardId": f"WARD-{code}-{ward}",
        }
        envelopes.append(_envelope("bed.assigned", i, hospital_id,
                                   sim_min, payload, seed))
        sim_min += 1

    # --- forecast.published: a handful per hospital (no encounter FK) ----
    for h_idx, (hospital_id, _code) in enumerate(HOSPITALS):
        for horizon in (24, 48, 72):
            payload = {
                "hospitalId": hospital_id,
                "horizonHours": horizon,
                "predictedOccupancy": round(rng.uniform(0.55, 0.98), 2),
            }
            envelopes.append(_envelope("forecast.published",
                                       h_idx * 10 + horizon, hospital_id,
                                       sim_min, payload, seed))
            sim_min += 1

    # --- discharge.scored: ~70% of encounters (FK -> encounter) ----------
    for i, (enc_id, hospital_id) in enumerate(encounters):
        if rng.random() >= 0.7:
            continue
        payload = {
            "encounterId": enc_id,
            "score": round(rng.uniform(0.0, 1.0), 2),
        }
        envelopes.append(_envelope("discharge.scored", i, hospital_id,
                                   sim_min, payload, seed))
        sim_min += 1

    # --- discharge.recommended: ~55% of encounters (FK -> encounter) -----
    for i, (enc_id, hospital_id) in enumerate(encounters):
        if rng.random() >= 0.55:
            continue
        payload = {
            "encounterId": enc_id,
            "recommendation": rng.choice(DISCHARGE_RECOMMENDATIONS),
        }
        envelopes.append(_envelope("discharge.recommended", i, hospital_id,
                                   sim_min, payload, seed))
        sim_min += 1

    return envelopes


def build_document(n_encounters: int = 200, seed: int = 42) -> dict:
    records = build_envelopes(n_encounters=n_encounters, seed=seed)
    return {
        "contractId": CONTRACT_ID,
        "contractVersion": "1.0.0",
        "classification": "operational-confidential",
        "residency": "US-West",
        "seed": seed,
        "recordCount": len(records),
        "records": records,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate the eventstream raw seed.")
    default_out = (Path(__file__).resolve().parents[2]
                   / "data" / "synthetic" / "eventstream" / "eventstream_raw.json")
    p.add_argument("--out", default=str(default_out))
    p.add_argument("--n-encounters", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv if argv is not None else sys.argv[1:])
    doc = build_document(n_encounters=ns.n_encounters, seed=ns.seed)
    out_path = Path(ns.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    kinds = {}
    for r in doc["records"]:
        kinds[r["eventKind"]] = kinds.get(r["eventKind"], 0) + 1
    print(f"Wrote {doc['recordCount']} envelopes -> {out_path}")
    for kind in sorted(kinds):
        print(f"  {kind:<28s} {kinds[kind]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
