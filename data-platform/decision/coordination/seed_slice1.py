"""Deterministic seed for the Sprint 26 Slice 1 golden thread.

Assembles the canonical OOA -> DCA coordination thread: a human
(``charge-nurse-anna``) approves an ``OOA-EXPEDITE-DISCHARGE`` recommendation
for ward "Medicine A", which recovers 6 beds and drives forecast occupancy
from 102% down to 94%, recording an ``ooa -> dca`` handoff on the plan.

Run as a module from the ``data-platform/decision`` directory
(``python -m coordination.seed_slice1``) to print the resulting plan as JSON,
or import :func:`build_slice1` to get the plan dict programmatically (e.g. from
tests, verifying determinism).

No PyYAML dependency: the lever catalog fields needed by
``compute_expected_impact`` (``lever_id``, ``impact_formula_ref``,
``owner_role``) are hand-constructed here from
``data-platform/decision/levers/ooa.yaml`` and ``dca.yaml`` (read, not parsed,
by this module) so the seed runs without optional dependencies.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from coordination.plan_runtime import approve_action, open_plan, propose_action
from coordination.store import InMemoryStore

#: Hand-constructed flat catalog mirroring the relevant fields of
#: data-platform/decision/levers/ooa.yaml and dca.yaml (role, owner_role,
#: impact_formula_ref) — avoids a PyYAML dependency for this deterministic seed.
CATALOG: List[Dict[str, Any]] = [
    {
        "lever_id": "OOA-EXPEDITE-DISCHARGE",
        "role": "ooa",
        "owner_role": "dca",
        "impact_formula_ref": "expedite_discharge_beds",
    },
    {
        "lever_id": "DCA-UNBLOCK-BARRIER",
        "role": "dca",
        "owner_role": "dca",
        "impact_formula_ref": "unblock_barrier_beds",
    },
]

#: Verified self-consistent WS-A gold forecast fixture: ward Medicine A at
#: bed_capacity=75, forecastOccupiedBeds=76.5 -> baseline_pct = round(102.0) = 102.
#: Approving OOA-EXPEDITE-DISCHARGE(n=6) recovers delta=min(6, round(76.5)=76)=6
#: beds -> current_pct = round((76.5 - 6) / 75 * 100) = round(94.0) = 94.
GOLD: Dict[str, Any] = {
    "forecast": [
        {
            "wardId": "Medicine A",
            "horizonH": 72,
            "bedCapacity": 75,
            "forecastOccupiedBeds": 76.5,
        }
    ],
    "drivers": [],
}

EPISODE_KEY = "EP-MEDICINE-A-20260724"
WARD = "Medicine A"
BED_CAPACITY = 75
BASELINE_OCCUPIED_BEDS = 76.5
TARGET_PCT = 94
APPROVER = "charge-nurse-anna"


def build_slice1() -> Dict[str, Any]:
    """Build the OOA -> DCA golden thread and return the resulting plan dict.

    Deterministic: no randomness, no wall-clock reads (uses the runtime's
    fixed ``DEFAULT_NOW`` sentinel throughout). Calling this twice yields two
    identical plan dicts.
    """
    store = InMemoryStore()

    plan = open_plan(
        store,
        episode_key=EPISODE_KEY,
        ward=WARD,
        bed_capacity=BED_CAPACITY,
        baseline_occupied_beds=BASELINE_OCCUPIED_BEDS,
        target_pct=TARGET_PCT,
    )

    action = propose_action(
        store,
        plan_id=plan["id"],
        role="ooa",
        lever_id="OOA-EXPEDITE-DISCHARGE",
        params={"n": 6, "before": "17:00"},
        gold=GOLD,
        catalog=CATALOG,
    )

    plan = approve_action(
        store,
        action_id=action["id"],
        approver=APPROVER,
        gold=GOLD,
        catalog=CATALOG,
    )

    return plan


def main() -> Dict[str, Any]:
    plan = build_slice1()
    print(json.dumps(plan, indent=2, sort_keys=True))
    return plan


if __name__ == "__main__":
    main()
