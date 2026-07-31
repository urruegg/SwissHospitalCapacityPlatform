"""Declarative lever-effect interpreter (Sprint 38 M2, design spec Sec 6.2).

Reads a lever's declared ``effect`` block and executes the corresponding
SimState mutation deterministically. Adding a lever == adding a YAML effect
block; no new Python. Returns a realised-delta dict shaped to mirror
``compute_expected_impact`` so the OutcomeRecorder can compare predicted vs
realised on the same metric axis."""
from __future__ import annotations

import re
from typing import Any, Dict

from closedloop.sim_state import SimState, Stage


_STAGE_BY_NAME = {s.value: s for s in Stage}


def _free_bed_for_patient(state: SimState, patient_id: str) -> str | None:
    for bed in sorted(state.beds.values(), key=lambda b: b.bed_id):
        if bed.patient_id == patient_id and bed.state == "occupied":
            bed.state = "available"
            bed.patient_id = None
            return bed.bed_id
    return None


def _parse_cascade_stage(cascade: list[dict[str, Any]]) -> Stage | None:
    """Parse the declared cascade into a target Stage (or None if no cascade).

    Supports exactly one rule shape:
    ``{when: patient_all_barriers_cleared, set: "Patient.stage=<STAGE>"}``.
    Raises ValueError (fail-closed) for any other shape so a lever author gets a
    clear error rather than silently-different behavior."""
    if not cascade:
        return None
    if len(cascade) != 1:
        raise ValueError(f"unsupported cascade: expected 0 or 1 rule, got {len(cascade)}")
    rule = cascade[0]
    if rule.get("when") != "patient_all_barriers_cleared":
        raise ValueError(f"unsupported cascade.when: {rule.get('when')!r}")
    match = re.fullmatch(r"Patient\.stage=([A-Z_]+)", str(rule.get("set", "")).strip())
    if not match or match.group(1) not in _STAGE_BY_NAME:
        raise ValueError(f"unsupported cascade.set: {rule.get('set')!r}")
    return _STAGE_BY_NAME[match.group(1)]


def apply_effect(state: SimState, effect: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a declarative lever ``effect`` against ``state`` bounded by ``params['n']``.

    Honors the declared ``from`` (barrier status to select), ``select_by``
    (only ``barrier_type`` is supported), and ``cascade`` (the downstream
    patient-stage transition). Fail-closed: raises ValueError for any
    ``applies_to`` / ``mutation`` / ``select_by`` / ``cascade`` shape it cannot
    honor. Returns ``{metric, delta, state_delta}`` where ``delta`` is the
    realised bed-relief magnitude (beds are freed only when the cascade
    discharges the patient)."""
    if effect.get("applies_to") != "DischargeBarrier":
        raise ValueError(f"unsupported effect.applies_to: {effect.get('applies_to')!r} (only 'DischargeBarrier')")
    if effect.get("mutation") != "set_status":
        raise ValueError(f"unsupported effect.mutation: {effect.get('mutation')!r} (only 'set_status')")
    select_by = effect.get("select_by", "barrier_type")
    if select_by != "barrier_type":
        raise ValueError(f"unsupported effect.select_by: {select_by!r} (only 'barrier_type')")

    from_status = effect.get("from", "open")
    to_status = effect["to"]
    cascade_stage = _parse_cascade_stage(effect.get("cascade", []))

    barrier_type = params["barrier_type"]
    n = int(params["n"])
    candidates = sorted(
        (b for b in state.barriers.values()
         if b.barrier_type == barrier_type and b.status == from_status),
        key=lambda b: b.barrier_id,
    )[:n]

    freed_beds: list[str] = []
    discharged: list[str] = []
    promoted: list[str] = []
    for barrier in candidates:
        barrier.status = to_status
        patient_id = barrier.patient_id
        remaining = [
            b for b in state.barriers.values()
            if b.patient_id == patient_id and b.status == from_status
        ]
        if remaining or patient_id not in state.patients or cascade_stage is None:
            continue
        state.patients[patient_id].journey_stage = cascade_stage
        if cascade_stage == Stage.DISCHARGED:
            bed_id = _free_bed_for_patient(state, patient_id)
            if bed_id:
                freed_beds.append(bed_id)
            discharged.append(patient_id)
        else:
            promoted.append(patient_id)

    return {
        "metric": "beds_freed",
        "delta": len(freed_beds),
        "state_delta": {
            "beds_freed": sorted(freed_beds),
            "patients_discharged": sorted(discharged),
            "patients_promoted": sorted(promoted),
        },
    }
