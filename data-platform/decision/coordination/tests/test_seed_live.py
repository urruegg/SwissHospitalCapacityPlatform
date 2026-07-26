"""Unit tests for the gated live seed (Sprint 26 WS-C).

The live seed replays the full six-role prescriptive story — the Slice-1
OOA->DCA thread plus the four WS-B fan-out threads (BMCA/ORSA/SBA/CSA) — through
the pure ``plan_runtime`` into an *injected* store. Tests prove: the replay is
deterministic; ``--action plan`` produces the exact documents that would be
written (dry run, no cloud); the replay is store-agnostic (identical over the
in-memory store and a fake Cosmos store); and ``--action apply`` refuses a bot
approver and refuses to run when Cosmos is unconfigured (no silent no-op).
"""
from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from coordination import seed_live
from coordination.cosmos_store import CosmosStore
from coordination.store import InMemoryStore
from coordination.tests.test_cosmos_store import FakeContainer


def _fake_cosmos_store() -> CosmosStore:
    return CosmosStore(
        plans_container=FakeContainer("episode_key"),
        actions_container=FakeContainer("plan_id"),
    )


class TestSeedThreads(unittest.TestCase):
    def test_covers_five_proposing_roles(self):
        roles = {t["role"] for t in seed_live.ALL_THREADS}
        self.assertEqual(roles, {"ooa", "bmca", "orsa", "sba", "csa"})

    def test_slice1_thread_is_first_and_owned_by_dca(self):
        # The 6th role (DCA) participates as the owner_role handoff target of the
        # OOA thread rather than as its own proposing thread.
        plans = seed_live.seed_into(InMemoryStore())
        ooa_plan = plans[0]
        self.assertEqual(
            ooa_plan["handoffs"],
            [
                {
                    "from_role": "ooa",
                    "to_role": "dca",
                    "action_id": ooa_plan["actions"][0],
                    "lever_id": "OOA-EXPEDITE-DISCHARGE",
                }
            ],
        )


class TestSeedDeterminism(unittest.TestCase):
    def test_seed_into_is_deterministic(self):
        self.assertEqual(
            seed_live.seed_into(InMemoryStore()),
            seed_live.seed_into(InMemoryStore()),
        )

    def test_store_agnostic_over_cosmos_and_memory(self):
        mem_plans = seed_live.seed_into(InMemoryStore())
        cosmos_plans = seed_live.seed_into(_fake_cosmos_store())
        self.assertEqual(mem_plans, cosmos_plans)


class TestDryRunDocuments(unittest.TestCase):
    def test_shape(self):
        docs = seed_live.dry_run_documents()
        self.assertEqual(set(docs), {"plans", "proposed_actions"})
        self.assertEqual(len(docs["plans"]), 5)
        self.assertEqual(len(docs["proposed_actions"]), 5)

    def test_every_plan_recomputes_once(self):
        for plan in seed_live.dry_run_documents()["plans"]:
            self.assertEqual(len(plan["forecast_deltas"]), 1, msg=plan["id"])

    def test_is_deterministic(self):
        self.assertEqual(seed_live.dry_run_documents(), seed_live.dry_run_documents())


class TestApplyGating(unittest.TestCase):
    def test_apply_refuses_bot_approver(self):
        with self.assertRaises(SystemExit):
            seed_live.apply("copilot")

    def test_apply_refuses_empty_approver(self):
        with self.assertRaises(SystemExit):
            seed_live.apply("")

    def test_apply_refuses_when_cosmos_unconfigured(self):
        # No CSA_COSMOS_ENDPOINT in the env -> from_env() is None -> refuse
        # rather than silently doing nothing.
        with self.assertRaises(SystemExit) as ctx:
            seed_live.apply("charge-nurse-anna")
        self.assertIn("Cosmos", str(ctx.exception))

    def test_apply_writes_into_injected_store(self):
        store = _fake_cosmos_store()
        result = seed_live.apply("charge-nurse-anna", store=store)
        self.assertTrue(result["applied"])
        self.assertEqual(result["planCount"], 5)
        self.assertEqual(store.get_plan("plan-EP-MEDICINE-A-20260724")["current_pct"], 94)


class TestCli(unittest.TestCase):
    def test_plan_action_prints_documents_and_returns_zero(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = seed_live.main(["--action", "plan"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(len(payload["plans"]), 5)

    def test_apply_action_requires_approver(self):
        with self.assertRaises(SystemExit):
            seed_live.main(["--action", "apply"])


if __name__ == "__main__":
    unittest.main()
