"""Unit tests for the Foundry decision-tier registration tool (Sprint 26 WS-C).

The tool wires the deterministic coordination runtime (Cosmos ``plans`` /
``proposed_actions`` + the ``compute_expected_impact`` tool + each role's lever
catalog) onto the six Foundry proposing agents. Tests assert the plan is pure
and deterministic, covers exactly the six decision-tier agents, points each
agent at its own role catalog, and that ``apply`` honours the HITL gate
(``AGENTS.md`` §4): non-empty, non-bot approver and an explicit live
registration factory (no accidental cloud writes).
"""
from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from foundry import register_decision_tier as reg


class TestBuildPlan(unittest.TestCase):
    def test_covers_six_decision_tier_agents(self):
        agents = {p["foundryAgent"] for p in reg.build_all_plans()}
        self.assertEqual(
            agents,
            {
                "ooa-agent",
                "dca-agent",
                "bmca-agent",
                "orsa-agent",
                "sba-agent",
                "csa-agent",
            },
        )

    def test_plan_is_deterministic(self):
        self.assertEqual(reg.build_all_plans(), reg.build_all_plans())

    def test_plan_is_pure_and_write_ceiling(self):
        plan = reg.build_plan("ooa")
        self.assertEqual(plan["action"], "plan")
        self.assertEqual(plan["tool"]["ceiling"], "write")
        self.assertEqual(plan["tool"]["cosmos"]["plans"], "plans")
        self.assertEqual(plan["tool"]["cosmos"]["proposedActions"], "proposed_actions")

    def test_region_defaults_to_eastus2(self):
        self.assertEqual(reg.build_plan("ooa")["region"], "eastus2")

    def test_each_agent_points_at_its_role_catalog(self):
        for plan in reg.build_all_plans():
            role = plan["tool"]["role"]
            self.assertTrue(
                plan["tool"]["leverCatalog"].endswith(f"levers/{role}.yaml"),
                msg=plan["foundryAgent"],
            )

    def test_hitl_gate_declared(self):
        hitl = reg.build_plan("csa")["tool"]["hitl"]
        self.assertEqual(hitl["approvalPhrase"], "approved-to-apply")
        self.assertTrue(hitl["refuseBotApprovers"])

    def test_unknown_role_raises(self):
        with self.assertRaises(KeyError):
            reg.build_plan("no-such-role")


class TestApplyGating(unittest.TestCase):
    def _plan(self):
        return reg.build_plan("ooa")

    def test_apply_refuses_empty_approver(self):
        with self.assertRaises(SystemExit):
            reg.apply(self._plan(), "", registration_factory=lambda p: {"ok": True})

    def test_apply_refuses_bot_approver(self):
        with self.assertRaises(SystemExit):
            reg.apply(self._plan(), "copilot", registration_factory=lambda p: {"ok": True})

    def test_apply_refuses_bracket_bot_approver(self):
        with self.assertRaises(SystemExit):
            reg.apply(
                self._plan(),
                "github-actions[bot]",
                registration_factory=lambda p: {"ok": True},
            )

    def test_apply_requires_factory(self):
        with self.assertRaises(SystemExit):
            reg.apply(self._plan(), "urruegg")

    def test_apply_with_factory_returns_applied(self):
        applied = reg.apply(
            self._plan(),
            "urruegg",
            registration_factory=lambda payload: {"registrationId": "reg-123"},
        )
        self.assertEqual(applied["action"], "apply")
        self.assertEqual(applied["approvedBy"], "urruegg")
        self.assertEqual(applied["registration"]["registrationId"], "reg-123")


class TestCli(unittest.TestCase):
    def test_plan_action_prints_all_six_and_returns_zero(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = reg.main(["--action", "plan"])
        self.assertEqual(rc, 0)
        self.assertEqual(len(json.loads(buf.getvalue())), 6)

    def test_plan_single_role(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = reg.main(["--action", "plan", "--role", "csa"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["foundryAgent"], "csa-agent")

    def test_apply_requires_approver(self):
        with self.assertRaises(SystemExit):
            reg.main(["--action", "apply", "--role", "ooa"])


if __name__ == "__main__":
    unittest.main()
