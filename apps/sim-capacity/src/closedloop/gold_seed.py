# apps/sim-capacity/src/closedloop/gold_seed.py
"""Seed a Sprint 38 SimState from a materialized EPIC-simulator gold snapshot
(Sprint 39 P1).

The gold snapshot is the current-state materialisation of the sim's gold event
streams (bed.state_changed / encounter.* / discharge.scored) — the same shape the
app Live toggle reads. This maps it into the SimState so the evidence harness (and
the Plan 2 operational loop) run on REAL simulator data: a captured deterministic
snapshot for CI, live SIT gold at runtime. PHI-free: synthetic ids only."""
from __future__ import annotations

from typing import Any, Dict

from closedloop.sim_state import Bed, DischargeBarrier, Patient, SimState, Stage, Ward

# encounter status -> journey stage
_STATUS_STAGE = {
    "arrived": Stage.ARRIVAL,
    "triaged": Stage.TRIAGE,
    "admitted": Stage.ADMIT,
    "in-progress": Stage.INPATIENT,
    "inpatient": Stage.INPATIENT,
    "discharge-ready": Stage.DISCHARGE_READY,
    "finished": Stage.DISCHARGED,
    "discharged": Stage.DISCHARGED,
}

# a discharge-readiness score at/above this promotes an inpatient to DISCHARGE_READY
_READY_SCORE = 0.8


def seed_sim_state_from_gold(gold: Dict[str, Any]) -> SimState:
    """Map a materialized gold snapshot into a SimState. Ids are taken verbatim
    (synthetic); a bed's ``patientId`` is expected to match an encounter's
    ``encounterId`` and a barrier's ``encounterId`` for the discharge cascade."""
    state = SimState(hospital_id=gold["hospital_id"])

    for w in gold.get("wards", []):
        state.wards[w["wardId"]] = Ward(
            ward_id=w["wardId"],
            specialty=w.get("specialty", ""),
            staffed_capacity=int(w["bedCapacity"]),
        )

    scores = {s["encounterId"]: float(s["score"]) for s in gold.get("discharge_scores", [])}
    for enc in gold.get("encounters", []):
        pid = enc["encounterId"]
        stage = _STATUS_STAGE.get(str(enc.get("status", "inpatient")).lower(), Stage.INPATIENT)
        if stage == Stage.INPATIENT and scores.get(pid, 0.0) >= _READY_SCORE:
            stage = Stage.DISCHARGE_READY
        state.patients[pid] = Patient(
            patient_id=pid,
            acuity=int(enc.get("acuity", 2)),
            specialty=enc.get("specialty", ""),
            journey_stage=stage,
        )

    for b in gold.get("beds", []):
        state.beds[b["bedId"]] = Bed(
            bed_id=b["bedId"],
            ward_id=b["wardId"],
            state=b["state"],
            patient_id=b.get("patientId"),
        )

    for br in gold.get("barriers", []):
        state.barriers[br["barrierId"]] = DischargeBarrier(
            barrier_id=br["barrierId"],
            patient_id=br["encounterId"],
            barrier_type=br["barrierType"],
            status=br.get("status", "open"),
            aged_h=int(br.get("agedH", 0)),
        )

    return state
