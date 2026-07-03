#!/usr/bin/env python3
"""Deterministic OR sample data generator (Sprint 09 v2.0.0 — T5.4).

Emits two envelope-format JSON files that conform to
`data/synthetic/schema/dc-or-schedule-v1.schema.json` and
`data/synthetic/schema/dc-or-case-v1.schema.json`.

Produces ≥ 1 000 slots and ≥ 500 unique cases (each case emits a multi-event
stream, so `records[]` in `or_case.json` is several thousand rows).

Hospital identity is encoded in the ID prefix (`ORS-USZ-...`, `ORT-USZ-...`)
because the contract schemas do not carry a top-level `hospitalId`. The loader
notebook (T5.5) derives `hospitalId` from the prefix when projecting to the
gold layer.

Deterministic: `python generate.py` with `seed=42` must produce byte-identical
files on every run. Do not introduce ordering that depends on `dict.items()`
insertion order beyond what CPython 3.7+ guarantees. Do not use `uuid.uuid4()`.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --------------------------------------------------------------------------- #
# Domain constants
# --------------------------------------------------------------------------- #

HOSPITALS = ("USZ", "LUKS", "SZB")
THEATRES_PER_HOSPITAL = 5

# Weighted specialty mix — orthopedics / general-surgery dominate to mirror
# T3.1 hospital presets. Each entry is (HCS id suffix, weight, anaesthesia).
SPECIALTIES = (
    ("ORTHO",     35, "general"),
    ("GEN-SURG",  30, "general"),
    ("URO",       15, "regional"),
    ("CARDIO",    12, "general"),
    ("NEURO",      8, "general"),
)

CANCELLATION_REASONS = (
    "patient-condition",
    "staffing-shortage",
    "equipment-outage",
    "no-bed-available",
    "surgeon-unavailable",
)
BLOCK_REASONS = (
    "maintenance",
    "cleaning",
    "equipment-outage",
    "staffing-shortage",
)

# Sprint 09 v2 canonical demo window (matches simulator seed epoch).
START_DATE = datetime(2027, 1, 4, tzinfo=timezone.utc)  # Monday
MONTHS = 3

AS_OF = "2027-04-01T00:00:00Z"

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def iso_z(dt: datetime) -> str:
    """Emit UTC ISO-8601 with 'Z' suffix (no fractional seconds)."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def weighted_choice(rng: random.Random, choices):
    total = sum(w for _, w, *_ in choices)
    r = rng.randint(1, total)
    upto = 0
    for entry in choices:
        upto += entry[1]
        if r <= upto:
            return entry
    return choices[-1]


# --------------------------------------------------------------------------- #
# Generators
# --------------------------------------------------------------------------- #


def generate(seed: int = 42):
    rng = random.Random(seed)

    slot_records = []
    case_event_records = []

    slot_counter = {h: 0 for h in HOSPITALS}
    case_counter = {h: 0 for h in HOSPITALS}
    event_counter = {h: 0 for h in HOSPITALS}
    encounter_counter = 0

    total_days = MONTHS * 30

    for hospital in HOSPITALS:
        for theatre_num in range(1, THEATRES_PER_HOSPITAL + 1):
            theatre_id = f"ORT-{hospital}-{theatre_num:02d}"

            for day_offset in range(total_days):
                day = START_DATE + timedelta(days=day_offset)
                # Elective schedule Monday-Friday only.
                if day.weekday() >= 5:
                    continue

                # Two slots per weekday: morning + afternoon.
                for slot_start_hour in (8, 13):
                    slot_counter[hospital] += 1
                    slot_start = day.replace(hour=slot_start_hour, minute=0)
                    planned_minutes = rng.choice([120, 180, 240])
                    slot_end = slot_start + timedelta(minutes=planned_minutes)
                    slot_id = f"ORS-{hospital}-{slot_counter[hospital]:06d}"

                    specialty_code, _weight, anaesthesia = weighted_choice(rng, SPECIALTIES)
                    specialty_id = f"HCS-{specialty_code}"

                    # 8% of slots are blocked (maintenance / cleaning / etc).
                    is_blocked = rng.random() < 0.08
                    block_reason = rng.choice(BLOCK_REASONS) if is_blocked else None

                    # If blocked: no planned case; status=blocked.
                    # Else: 92% get a planned case; status=planned/available.
                    has_case = (not is_blocked) and (rng.random() < 0.90)

                    if is_blocked:
                        status = "blocked"
                        planned_case_id = None
                        encounter_id = None
                        anaesthesia_field = None
                    elif has_case:
                        status = "planned"
                        case_counter[hospital] += 1
                        planned_case_id = f"ORC-{hospital}-{case_counter[hospital]:06d}"
                        encounter_counter += 1
                        encounter_id = f"ENC-2027-{encounter_counter:06d}"
                        anaesthesia_field = anaesthesia
                    else:
                        status = "available"
                        planned_case_id = None
                        encounter_id = None
                        anaesthesia_field = None

                    slot_record = {
                        "contractId": "DC-OR-SCHEDULE-v1",
                        "orSlotId": slot_id,
                        "theatreId": theatre_id,
                        "slotStart": iso_z(slot_start),
                        "slotEnd": iso_z(slot_end),
                        "plannedDurationMinutes": planned_minutes,
                        "status": status,
                        "plannedCaseId": planned_case_id,
                        "encounterId": encounter_id,
                        "specialtyServiceId": specialty_id,
                        "requiredAnaesthesiaType": anaesthesia_field,
                        "requiredEquipmentIds": [],
                        "primarySurgeonRoleId": f"ROLE-SURG-{hospital}-{theatre_num:02d}"
                        if has_case
                        else None,
                        "blockReason": block_reason,
                        "purposeTag": "or-steering",
                        "dataResidencyRegion": "switzerlandnorth",
                        "asOfTimestamp": AS_OF,
                    }
                    slot_records.append(slot_record)

                    if not has_case:
                        continue

                    # ---- Case event stream ---------------------------------
                    # ~7% short-notice cancellations, ~15% overruns on rest.
                    cancelled = rng.random() < 0.07
                    events = _emit_case_events(
                        rng=rng,
                        hospital=hospital,
                        case_id=planned_case_id,
                        slot_id=slot_id,
                        encounter_id=encounter_id,
                        slot_start=slot_start,
                        planned_minutes=planned_minutes,
                        cancelled=cancelled,
                    )
                    for ev in events:
                        event_counter[hospital] += 1
                        ev["caseEventId"] = f"ORCE-{hospital}-{event_counter[hospital]:06d}"
                        case_event_records.append(ev)

    return slot_records, case_event_records


def _emit_case_events(
    *,
    rng: random.Random,
    hospital: str,
    case_id: str,
    slot_id: str,
    encounter_id: str,
    slot_start: datetime,
    planned_minutes: int,
    cancelled: bool,
) -> list[dict]:
    """Emit the event stream for one case. Order matters (chronological)."""
    base = {
        "contractId": "DC-OR-CASE-v1",
        "caseId": case_id,
        "orSlotId": slot_id,
        "encounterId": encounter_id,
        "plannedDurationMinutes": planned_minutes,
        "purposeTag": "or-steering",
        "dataResidencyRegion": "switzerlandnorth",
        "asOfTimestamp": AS_OF,
    }

    if cancelled:
        # Case is cancelled 1-72h before slot start.
        lead_hours = rng.randint(1, 72)
        cancel_ts = slot_start - timedelta(hours=lead_hours)
        return [
            _event(base, "scheduled", slot_start - timedelta(days=3)),
            _event(
                base,
                "cancelled",
                cancel_ts,
                cancellationReason=rng.choice(CANCELLATION_REASONS),
            ),
        ]

    # Successful case timeline.
    # 92% start on time; otherwise 1-30 min late.
    delay_min = 0 if rng.random() < 0.92 else rng.randint(1, 30)
    patient_in = slot_start + timedelta(minutes=delay_min)
    anaesthesia_consult = patient_in - timedelta(hours=rng.randint(2, 24))
    incision_start = patient_in + timedelta(minutes=rng.randint(10, 25))

    # Actual surgical duration: planned ± bias toward overrun.
    duration_delta = rng.randint(-20, 40)
    actual_duration = max(15, planned_minutes + duration_delta)
    incision_end = incision_start + timedelta(minutes=actual_duration)
    patient_out = incision_end + timedelta(minutes=rng.randint(5, 20))

    overrun_min = max(
        0, (patient_out - (slot_start + timedelta(minutes=planned_minutes))).total_seconds() // 60
    )
    overrun_min = int(overrun_min)

    turnover_started = patient_out
    turnover_completed = turnover_started + timedelta(minutes=rng.randint(15, 45))

    events = [
        _event(base, "scheduled", slot_start - timedelta(days=3)),
        _event(base, "anaesthesia-consult-completed", anaesthesia_consult),
        _event(base, "patient-in-room", patient_in),
        _event(base, "incision-start", incision_start),
        _event(
            base,
            "incision-end",
            incision_end,
            actualDurationMinutes=actual_duration,
        ),
    ]
    if overrun_min > 0:
        events.append(_event(base, "overrun", incision_end, overrunMinutes=overrun_min))
    events.append(_event(base, "patient-out-of-room", patient_out))
    events.append(_event(base, "turnover-started", turnover_started))
    events.append(
        _event(
            base,
            "turnover-completed",
            turnover_completed,
        )
    )
    return events


def _event(base: dict, event_type: str, ts: datetime, **extras) -> dict:
    """Build one event record with the canonical field order for stable JSON."""
    record = {
        "contractId": base["contractId"],
        # caseEventId injected by caller after emission.
        "caseEventId": None,
        "caseId": base["caseId"],
        "orSlotId": base["orSlotId"],
        "encounterId": base["encounterId"],
        "eventType": event_type,
        "eventTimestamp": iso_z(ts),
        "plannedDurationMinutes": base["plannedDurationMinutes"],
        "actualDurationMinutes": extras.get("actualDurationMinutes"),
        "overrunMinutes": extras.get("overrunMinutes"),
        "cancellationReason": extras.get("cancellationReason"),
        "turnoverPredecessorCaseId": extras.get("turnoverPredecessorCaseId"),
        "purposeTag": base["purposeTag"],
        "dataResidencyRegion": base["dataResidencyRegion"],
        "asOfTimestamp": base["asOfTimestamp"],
    }
    return record


# --------------------------------------------------------------------------- #
# Envelopes
# --------------------------------------------------------------------------- #


def wrap_schedule(records: list[dict]) -> dict:
    return {
        "datasetId": "DS-OR-SCHEDULE-samples-2027q1",
        "contractId": "DC-OR-SCHEDULE-v1",
        "contractVersion": "1.0.0",
        "classification": "operational-confidential",
        "residency": "CH",
        "purposeTags": ["or-steering", "capacity-planning", "scheduling-optimization"],
        "records": records,
    }


def wrap_cases(records: list[dict]) -> dict:
    return {
        "datasetId": "DS-OR-CASE-samples-2027q1",
        "contractId": "DC-OR-CASE-v1",
        "contractVersion": "1.0.0",
        "classification": "operational-confidential",
        "residency": "CH",
        "purposeTags": ["or-steering", "case-monitoring", "utilization-analytics"],
        "records": records,
    }


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main() -> None:
    slots, case_events = generate(seed=42)
    unique_cases = len({r["caseId"] for r in case_events})

    out_dir = Path(__file__).parent
    (out_dir / "or_schedule.json").write_text(
        json.dumps(wrap_schedule(slots), indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "or_case.json").write_text(
        json.dumps(wrap_cases(case_events), indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Generated {len(slots)} slots, "
        f"{unique_cases} unique cases ({len(case_events)} case-event records)"
    )


if __name__ == "__main__":
    main()
