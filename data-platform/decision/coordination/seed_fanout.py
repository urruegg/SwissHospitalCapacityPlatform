"""Deterministic seed for the Sprint 26 WS-B fan-out coordination threads.

Fans the OOA -> DCA Slice 1 pattern (see :mod:`coordination.seed_slice1`) out to
the four remaining roles — BMCA, ORSA, SBA, CSA — each driving its own
``open_plan -> propose_action -> HITL approve_action -> live-sync`` thread over
the same pure :mod:`coordination.plan_runtime` and the role-agnostic
``plans`` / ``proposed_actions`` store surface. No new Cosmos container is
required: the two containers merged in Slice 1 are keyed by ``/episode_key`` and
``/plan_id`` and carry any role.

Run as a module from the ``data-platform/decision`` directory
(``python -m coordination.seed_fanout``) to print each role's resulting plan as
JSON, or import :func:`build_all_threads` for a ``{role: plan}`` mapping.

No PyYAML dependency: the catalog fields needed by ``compute_expected_impact``
(``lever_id``, ``impact_formula_ref``, ``owner_role``) are hand-constructed here
from ``data-platform/decision/levers/{bmca,orsa,sba,csa}.yaml`` (read, not
parsed, by this module) so the seed runs without optional dependencies.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from coordination.plan_runtime import approve_action, open_plan, propose_action
from coordination.store import InMemoryStore

#: Hand-constructed flat catalog mirroring the relevant fields of the four
#: fanned-out role YAMLs (role, owner_role, impact_formula_ref) — avoids a
#: PyYAML dependency for this deterministic seed.
CATALOG: List[Dict[str, Any]] = [
    {
        "lever_id": "BMCA-REBALANCE-CENSUS",
        "role": "bmca",
        "owner_role": "bmca",
        "impact_formula_ref": "rebalance_census_beds",
    },
    {
        "lever_id": "ORSA-DEFER-ELECTIVE",
        "role": "orsa",
        "owner_role": "orsa",
        "impact_formula_ref": "defer_elective_slots",
    },
    {
        "lever_id": "SBA-FLEX-STAFF-BEDS",
        "role": "sba",
        "owner_role": "sba",
        "impact_formula_ref": "flex_staff_beds",
    },
    {
        "lever_id": "CSA-ACTIVATE-SURGE",
        "role": "csa",
        "owner_role": "csa",
        "impact_formula_ref": "activate_surge_beds",
    },
]

#: Per-role golden threads. Each fixture is self-consistent: the ward's
#: ``bedCapacity`` / ``forecastOccupiedBeds`` in ``gold`` match the ``open_plan``
#: baseline, and approving the single lever recovers ``params["n"]`` beds (bound
#: by physically occupied beds) to drop occupancy below the breaching baseline.
FANOUT_THREADS: List[Dict[str, Any]] = [
    {
        "role": "bmca",
        "ward": "Surgery A",
        "episode_key": "EP-SURGERY-A-20260724",
        "bed_capacity": 60,
        "baseline_occupied_beds": 63,
        "target_pct": 97,
        "lever_id": "BMCA-REBALANCE-CENSUS",
        "params": {"n": 5, "to_ward": "Surgery B"},
        "approver": "bed-manager-lena",
    },
    {
        "role": "orsa",
        "ward": "Ortho A",
        "episode_key": "EP-ORTHO-A-20260724",
        "bed_capacity": 40,
        "baseline_occupied_beds": 42,
        "target_pct": 95,
        "lever_id": "ORSA-DEFER-ELECTIVE",
        "params": {"n": 4, "before": "07:00"},
        "approver": "or-lead-marco",
    },
    {
        "role": "sba",
        "ward": "Medicine C",
        "episode_key": "EP-MEDICINE-C-20260724",
        "bed_capacity": 50,
        "baseline_occupied_beds": 52,
        "target_pct": 98,
        "lever_id": "SBA-FLEX-STAFF-BEDS",
        "params": {"n": 3, "shift": "night"},
        "approver": "staffing-lead-nadia",
    },
    {
        "role": "csa",
        "ward": "ICU A",
        "episode_key": "EP-ICU-A-20260724",
        "bed_capacity": 20,
        "baseline_occupied_beds": 24,
        "target_pct": 80,
        "lever_id": "CSA-ACTIVATE-SURGE",
        "params": {"n": 8, "scope": "cantonal"},
        "approver": "crisis-lead-tom",
    },
]

_THREADS_BY_ROLE = {t["role"]: t for t in FANOUT_THREADS}


def _gold_for(thread: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "forecast": [
            {
                "wardId": thread["ward"],
                "horizonH": 72,
                "bedCapacity": thread["bed_capacity"],
                "forecastOccupiedBeds": thread["baseline_occupied_beds"],
            }
        ],
        "drivers": [],
    }


def build_role_thread(role: str) -> Dict[str, Any]:
    """Build one role's fan-out golden thread and return the resulting plan.

    Deterministic: no randomness, no wall-clock reads (uses the runtime's fixed
    ``DEFAULT_NOW`` sentinel). Raises ``KeyError`` for an unknown role.
    """
    thread = _THREADS_BY_ROLE[role]
    gold = _gold_for(thread)
    store = InMemoryStore()

    plan = open_plan(
        store,
        episode_key=thread["episode_key"],
        ward=thread["ward"],
        bed_capacity=thread["bed_capacity"],
        baseline_occupied_beds=thread["baseline_occupied_beds"],
        target_pct=thread["target_pct"],
    )

    action = propose_action(
        store,
        plan_id=plan["id"],
        role=thread["role"],
        lever_id=thread["lever_id"],
        params=thread["params"],
        gold=gold,
        catalog=CATALOG,
    )

    return approve_action(
        store,
        action_id=action["id"],
        approver=thread["approver"],
        gold=gold,
        catalog=CATALOG,
    )


def build_all_threads() -> Dict[str, Dict[str, Any]]:
    """Return ``{role: resulting_plan}`` for all four fanned-out roles.

    Deterministic end-to-end: calling twice yields identical mappings.
    """
    return {thread["role"]: build_role_thread(thread["role"]) for thread in FANOUT_THREADS}


def main() -> Dict[str, Dict[str, Any]]:
    results = build_all_threads()
    print(json.dumps(results, indent=2, sort_keys=True))
    return results


if __name__ == "__main__":
    main()
