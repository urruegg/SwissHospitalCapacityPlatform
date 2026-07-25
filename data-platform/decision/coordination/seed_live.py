"""Gated live seed for the full six-role prescriptive story (Sprint 26 WS-C).

Replays every DC-INSIGHT-v1 coordination thread — the Slice-1 OOA->DCA thread
(:mod:`coordination.seed_slice1`) plus the four WS-B fan-out threads
BMCA/ORSA/SBA/CSA (:mod:`coordination.seed_fanout`) — through the pure
:mod:`coordination.plan_runtime` into an *injected* store, so the same replay
seeds either the deterministic :class:`~coordination.store.InMemoryStore` (dry
run / tests) or the live :class:`~coordination.cosmos_store.CosmosStore`
(``--action apply``).

Two-stage HITL gate (``AGENTS.md`` §4):

* ``--action plan`` (default) prints the exact ``plans`` / ``proposed_actions``
  documents that *would* be written. Pure, no cloud, no credentials.
* ``--action apply`` requires ``--approved-to-apply <github-handle>`` (a
  non-bot human) AND a configured, reachable Cosmos account
  (``CSA_COSMOS_ENDPOINT``). Per ADR-0029 the SIT account is private-endpoint
  only, so a real apply runs from inside the VNet (the agent-host), never from
  a laptop or a hosted CI runner.

Run from the ``data-platform/decision`` directory:
``python -m coordination.seed_live --action plan``.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from coordination import seed_slice1
from coordination.cosmos_store import CosmosStore
from coordination.plan_runtime import (
    _is_bot_approver,
    approve_action,
    open_plan,
    propose_action,
)
from coordination.seed_fanout import CATALOG as _FANOUT_CATALOG
from coordination.seed_fanout import FANOUT_THREADS
from coordination.store import InMemoryStore, PlanStore

#: The Slice-1 OOA->DCA thread, reconstructed from the seed_slice1 constants so
#: its fixture stays single-source-of-truth. Its lever is owned by DCA, so
#: approving it records the ``ooa -> dca`` handoff (the 6th role).
SLICE1_THREAD: Dict[str, Any] = {
    "role": "ooa",
    "ward": seed_slice1.WARD,
    "episode_key": seed_slice1.EPISODE_KEY,
    "bed_capacity": seed_slice1.BED_CAPACITY,
    "baseline_occupied_beds": seed_slice1.BASELINE_OCCUPIED_BEDS,
    "target_pct": seed_slice1.TARGET_PCT,
    "lever_id": "OOA-EXPEDITE-DISCHARGE",
    "params": {"n": 6, "before": "17:00"},
    "approver": seed_slice1.APPROVER,
}

#: Slice-1 thread first, then the four fan-out threads, in a stable order.
ALL_THREADS: List[Dict[str, Any]] = [SLICE1_THREAD, *FANOUT_THREADS]


def _union_catalog() -> List[Dict[str, Any]]:
    """Merge the Slice-1 and fan-out lever catalogs, de-duped by ``lever_id``."""
    merged: Dict[str, Dict[str, Any]] = {}
    for entry in [*seed_slice1.CATALOG, *_FANOUT_CATALOG]:
        merged.setdefault(entry["lever_id"], entry)
    return list(merged.values())


#: Flat catalog covering all six roles' levers, consumed by
#: ``compute_expected_impact`` during the replay.
CATALOG: List[Dict[str, Any]] = _union_catalog()


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


def seed_into(store: PlanStore) -> List[Dict[str, Any]]:
    """Replay all threads into ``store`` and return the resulting plans in order.

    Deterministic and store-agnostic: no randomness, no wall-clock reads (the
    runtime's fixed ``DEFAULT_NOW`` sentinel is used throughout). The same call
    sequence over any conformant :class:`PlanStore` yields identical plans.
    """
    plans: List[Dict[str, Any]] = []
    for thread in ALL_THREADS:
        gold = _gold_for(thread)
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
        plans.append(
            approve_action(
                store,
                action_id=action["id"],
                approver=thread["approver"],
                gold=gold,
                catalog=CATALOG,
            )
        )
    return plans


def dry_run_documents() -> Dict[str, List[Dict[str, Any]]]:
    """Return ``{"plans": [...], "proposed_actions": [...]}`` — the exact
    documents a live apply would write — computed against an in-memory store.
    """
    store = InMemoryStore()
    plans = seed_into(store)
    actions: List[Dict[str, Any]] = []
    for plan in plans:
        actions.extend(store.list_actions(plan["id"]))
    return {"plans": plans, "proposed_actions": actions}


def apply(
    approver: str,
    *,
    store: Optional[PlanStore] = None,
) -> Dict[str, Any]:
    """Live-seed all threads into Cosmos. HITL-gated per ``AGENTS.md`` §4.

    Refuses (``SystemExit``) when ``approver`` is falsy or a bot identity, or
    when no store is injected and Cosmos is unconfigured/unreachable
    (``CosmosStore.from_env()`` returns ``None``) — never a silent no-op. Tests
    inject a fake ``store`` to exercise the write path without cloud.
    """
    if not approver:
        raise SystemExit("apply requires --approved-to-apply <github-handle> (AGENTS.md §4)")
    if _is_bot_approver(approver):
        raise SystemExit(f"apply approver must be a human, not a bot identity: {approver!r} (AGENTS.md §4)")

    target = store if store is not None else CosmosStore.from_env()
    if target is None:
        raise SystemExit(
            "Cosmos is not configured or unreachable: set CSA_COSMOS_ENDPOINT and "
            "run from inside the SIT VNet (private-endpoint only per ADR-0029)."
        )

    plans = seed_into(target)
    return {
        "applied": True,
        "approvedBy": approver,
        "planCount": len(plans),
        "plans": [plan["id"] for plan in plans],
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", choices=["plan", "apply"], default="plan")
    parser.add_argument("--approved-to-apply", dest="approver", default="")
    args = parser.parse_args(argv)

    if args.action == "plan":
        print(json.dumps(dry_run_documents(), indent=2, sort_keys=True))
        return 0

    if not args.approver:
        raise SystemExit("apply requires --approved-to-apply <github-handle> (AGENTS.md §4)")
    print(json.dumps(apply(args.approver), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
