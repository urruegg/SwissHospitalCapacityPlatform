"""Declarative lever-effect interpreter (Sprint 38 M2, design spec Sec 6.2).

Reads a lever's declared ``effect`` block and executes the corresponding
SimState mutation deterministically. Adding a lever == adding a YAML effect
block; no new Python. Returns a realised-delta dict shaped to mirror
``compute_expected_impact`` so the OutcomeRecorder can compare predicted vs
realised on the same metric axis."""
from __future__ import annotations

from typing import Any, Dict

from closedloop.sim_state import SimState, Stage


def _free_bed_for_patient(state: SimState, patient_id: str) -> str | None:
    for bed in sorted(state.beds.values(), key=lambda b: b.bed_id):
        if bed.patient_id == patient_id and bed.state == "occupied":
            bed.state = "available"
            bed.patient_id = None
            return bed.bed_id
    return None


def apply_effect(state: SimState, effect: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ``effect`` against ``state`` bounded by ``params['n']``.

    Currently implements the ``set_status`` mutation on ``DischargeBarrier``
    with a ``patient_all_barriers_cleared`` cascade that discharges the patient
    and frees their bed — the mutation the four journey levers share. Returns
    ``{metric, delta, state_delta}`` where ``delta`` is the realised bed-relief
    magnitude."""
    if effect["applies_to"] != "DischargeBarrier" or effect["mutation"] != "set_status":
        raise ValueError(f"unsupported effect: {effect.get('applies_to')}/{effect.get('mutation')}")

    barrier_type = params["barrier_type"]
    n = int(params["n"])
    candidates = sorted(state.open_barriers(barrier_type), key=lambda b: b.barrier_id)[:n]

    freed_beds: list[str] = []
    discharged: list[str] = []
    for barrier in candidates:
        barrier.status = effect["to"]
        patient_id = barrier.patient_id
        remaining = [b for b in state.barriers.values()
                     if b.patient_id == patient_id and b.status == "open"]
        if not remaining and patient_id in state.patients:
            state.patients[patient_id].journey_stage = Stage.DISCHARGED
            bed_id = _free_bed_for_patient(state, patient_id)
            if bed_id:
                freed_beds.append(bed_id)
            discharged.append(patient_id)

    return {
        "metric": "beds_freed",
        "delta": len(freed_beds),
        "state_delta": {"beds_freed": sorted(freed_beds), "patients_discharged": sorted(discharged)},
    }
