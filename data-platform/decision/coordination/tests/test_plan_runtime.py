"""Unit tests for the coordination runtime (Sprint 26 WS-C): the golden-thread
lifecycle open -> propose -> approve (HITL) -> live-sync -> handoff.

Dependency-light: catalog and gold fixtures are injected literals (mirroring
the WS-B impact tests' convention in
``data-platform/decision/impact/tests/test_impact_pure.py``) — no PyYAML, no
jsonschema, no Fabric/Cosmos I/O.
"""
from __future__ import annotations

import copy
import unittest

from coordination.plan_runtime import approve_action, open_plan, propose_action, reject_action
from coordination.seed_slice1 import build_slice1
from coordination.store import InMemoryStore

CATALOG = [
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

# Medicine A: bed_capacity=75, forecastOccupiedBeds=76.5 -> baseline_pct=102.
GOLD = {
    "forecast": [
        {"wardId": "Medicine A", "horizonH": 72, "bedCapacity": 75, "forecastOccupiedBeds": 76.5}
    ],
    "drivers": [],
}


def _open_medicine_a_plan(store):
    return open_plan(
        store,
        episode_key="EP-TEST-MEDICINE-A",
        ward="Medicine A",
        bed_capacity=75,
        baseline_occupied_beds=76.5,
        target_pct=94,
    )


def _propose_expedite(store, plan_id):
    return propose_action(
        store,
        plan_id=plan_id,
        role="ooa",
        lever_id="OOA-EXPEDITE-DISCHARGE",
        params={"n": 6, "before": "17:00"},
        gold=GOLD,
        catalog=CATALOG,
    )


class TestGoldenThreadHappyPath(unittest.TestCase):
    def test_open_propose_approve_yields_102_to_94(self):
        store = InMemoryStore()
        plan = _open_medicine_a_plan(store)
        self.assertEqual(plan["baseline_pct"], 102)
        self.assertEqual(plan["current_pct"], 102)

        action = _propose_expedite(store, plan["id"])
        self.assertEqual(action["status"], "proposed")
        self.assertEqual(action["expected_impact"]["delta"], 6)
        self.assertEqual(action["owner_role"], "dca")

        updated_plan = approve_action(
            store,
            action_id=action["id"],
            approver="charge-nurse-anna",
            gold=GOLD,
            catalog=CATALOG,
        )

        self.assertEqual(updated_plan["baseline_pct"], 102)
        self.assertEqual(updated_plan["current_pct"], 94)

        self.assertEqual(len(updated_plan["forecast_deltas"]), 1)
        self.assertEqual(updated_plan["forecast_deltas"][0]["delta"], 6)
        self.assertEqual(updated_plan["forecast_deltas"][0]["resulting_pct"], 94)

        self.assertEqual(len(updated_plan["handoffs"]), 1)
        handoff = updated_plan["handoffs"][0]
        self.assertEqual(handoff["from_role"], "ooa")
        self.assertEqual(handoff["to_role"], "dca")

        applied_action = store.get_action(action["id"])
        self.assertEqual(applied_action["status"], "applied")
        self.assertEqual(applied_action["hitl_approver"], "charge-nurse-anna")
        self.assertIsNotNone(applied_action["approved_at"])


class TestRefuseBotApprover(unittest.TestCase):
    def _assert_plan_unchanged(self, store, plan_id):
        plan = store.get_plan(plan_id)
        self.assertEqual(plan["current_pct"], 102)
        self.assertEqual(plan["forecast_deltas"], [])
        self.assertEqual(plan["handoffs"], [])

    def test_refuse_github_actions_bot(self):
        store = InMemoryStore()
        plan = _open_medicine_a_plan(store)
        action = _propose_expedite(store, plan["id"])

        with self.assertRaises(PermissionError):
            approve_action(
                store,
                action_id=action["id"],
                approver="github-actions[bot]",
                gold=GOLD,
                catalog=CATALOG,
            )
        self._assert_plan_unchanged(store, plan["id"])

    def test_refuse_copilot(self):
        store = InMemoryStore()
        plan = _open_medicine_a_plan(store)
        action = _propose_expedite(store, plan["id"])

        with self.assertRaises(PermissionError):
            approve_action(
                store,
                action_id=action["id"],
                approver="Copilot",
                gold=GOLD,
                catalog=CATALOG,
            )
        self._assert_plan_unchanged(store, plan["id"])


class TestRefuseSelfApproval(unittest.TestCase):
    def test_refuse_when_approver_equals_proposing_role(self):
        store = InMemoryStore()
        plan = _open_medicine_a_plan(store)
        action = _propose_expedite(store, plan["id"])

        with self.assertRaises(PermissionError):
            approve_action(
                store,
                action_id=action["id"],
                approver="ooa",
                gold=GOLD,
                catalog=CATALOG,
            )

        unchanged_plan = store.get_plan(plan["id"])
        self.assertEqual(unchanged_plan["current_pct"], 102)
        self.assertEqual(unchanged_plan["forecast_deltas"], [])

    def test_refuse_case_insensitive_self_approval(self):
        store = InMemoryStore()
        plan = _open_medicine_a_plan(store)
        action = _propose_expedite(store, plan["id"])

        with self.assertRaises(PermissionError):
            approve_action(
                store,
                action_id=action["id"],
                approver="OOA",
                gold=GOLD,
                catalog=CATALOG,
            )


class TestRefuseDoubleApproval(unittest.TestCase):
    def test_refuse_second_approval_of_applied_action(self):
        store = InMemoryStore()
        plan = _open_medicine_a_plan(store)
        action = _propose_expedite(store, plan["id"])

        approve_action(
            store,
            action_id=action["id"],
            approver="charge-nurse-anna",
            gold=GOLD,
            catalog=CATALOG,
        )
        plan_after_first = store.get_plan(plan["id"])
        self.assertEqual(plan_after_first["current_pct"], 94)

        with self.assertRaises(ValueError):
            approve_action(
                store,
                action_id=action["id"],
                approver="dr-mueller",
                gold=GOLD,
                catalog=CATALOG,
            )

        plan_after_second_attempt = store.get_plan(plan["id"])
        self.assertEqual(plan_after_second_attempt["current_pct"], 94)
        self.assertEqual(len(plan_after_second_attempt["forecast_deltas"]), 1)


class TestReject(unittest.TestCase):
    def test_reject_marks_status_without_plan_mutation(self):
        store = InMemoryStore()
        plan = _open_medicine_a_plan(store)
        action = _propose_expedite(store, plan["id"])

        rejected = reject_action(store, action_id=action["id"], approver="charge-nurse-anna")
        self.assertEqual(rejected["status"], "rejected")

        unchanged_plan = store.get_plan(plan["id"])
        self.assertEqual(unchanged_plan["current_pct"], 102)
        self.assertEqual(unchanged_plan["forecast_deltas"], [])

    def test_reject_twice_raises(self):
        store = InMemoryStore()
        plan = _open_medicine_a_plan(store)
        action = _propose_expedite(store, plan["id"])
        reject_action(store, action_id=action["id"], approver="charge-nurse-anna")
        with self.assertRaises(ValueError):
            reject_action(store, action_id=action["id"], approver="charge-nurse-anna")


class TestSeedDeterminism(unittest.TestCase):
    def test_seed_runs_twice_produce_identical_plans(self):
        plan_1 = build_slice1()
        plan_2 = build_slice1()
        self.assertEqual(plan_1, plan_2)
        self.assertEqual(plan_1["baseline_pct"], 102)
        self.assertEqual(plan_1["current_pct"], 94)


class TestCumulativeDelta(unittest.TestCase):
    def test_two_approved_actions_sum_cumulatively(self):
        store = InMemoryStore()
        plan = _open_medicine_a_plan(store)

        expedite = _propose_expedite(store, plan["id"])
        plan = approve_action(
            store,
            action_id=expedite["id"],
            approver="charge-nurse-anna",
            gold=GOLD,
            catalog=CATALOG,
        )
        self.assertEqual(plan["current_pct"], 94)

        unblock = propose_action(
            store,
            plan_id=plan["id"],
            role="dca",
            lever_id="DCA-UNBLOCK-BARRIER",
            params={"barrier_type": "transport", "n": 2},
            gold=GOLD,
            catalog=CATALOG,
        )
        plan = approve_action(
            store,
            action_id=unblock["id"],
            approver="dr-mueller",
            gold=GOLD,
            catalog=CATALOG,
        )

        # baseline_occupied_beds=76.5, cumulative delta=6+2=8
        # current_occupied=68.5 -> current_pct = round(68.5/75*100) = round(91.333) = 91
        self.assertEqual(plan["current_pct"], 91)
        self.assertEqual(len(plan["forecast_deltas"]), 2)
        self.assertEqual(plan["forecast_deltas"][1]["delta"], 2)
        # Same role proposed + owns DCA-UNBLOCK-BARRIER -> no new handoff edge.
        self.assertEqual(len(plan["handoffs"]), 1)


class TestActionAndPlanNotFound(unittest.TestCase):
    def test_propose_unknown_plan_raises(self):
        store = InMemoryStore()
        with self.assertRaises(ValueError):
            propose_action(
                store,
                plan_id="no-such-plan",
                role="ooa",
                lever_id="OOA-EXPEDITE-DISCHARGE",
                params={"n": 6, "before": "17:00"},
                gold=GOLD,
                catalog=CATALOG,
            )

    def test_approve_unknown_action_raises(self):
        store = InMemoryStore()
        with self.assertRaises(ValueError):
            approve_action(
                store,
                action_id="no-such-action",
                approver="charge-nurse-anna",
                gold=GOLD,
                catalog=CATALOG,
            )


class TestDeterminismWithinFunctions(unittest.TestCase):
    def test_approve_action_is_deterministic_given_same_inputs(self):
        def run_once():
            store = InMemoryStore()
            plan = _open_medicine_a_plan(store)
            action = _propose_expedite(store, plan["id"])
            return approve_action(
                store,
                action_id=action["id"],
                approver="charge-nurse-anna",
                gold=copy.deepcopy(GOLD),
                catalog=copy.deepcopy(CATALOG),
            )

        self.assertEqual(run_once(), run_once())


if __name__ == "__main__":
    unittest.main()
