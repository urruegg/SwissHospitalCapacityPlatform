#!/usr/bin/env python3
"""Unit tests for the Fabric-data-agent-tool registration plan (Slice 0).

Dependency-free (Python 3 standard library only). Run with::

    python -m unittest discover -s data-platform/scripts/tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import register_fabric_data_agent_tool as reg  # noqa: E402


class BuildPlanTests(unittest.TestCase):
    def test_build_plan_shape(self):
        plan = reg.build_plan(
            foundry_agent="ooa-agent",
            data_agent_endpoint="https://example/fabric-data-agent",
            workspace_id="ws-123",
            region="westus2",
        )
        self.assertEqual(plan["foundryAgent"], "ooa-agent")
        self.assertEqual(plan["tool"]["type"], "fabric_data_agent")
        self.assertEqual(plan["tool"]["workspaceId"], "ws-123")
        self.assertEqual(plan["region"], "westus2")
        self.assertEqual(plan["action"], "plan")

    def test_plan_is_deterministic(self):
        args = dict(
            foundry_agent="ooa-agent",
            data_agent_endpoint="https://example/fabric-data-agent",
            workspace_id="ws-123",
            region="westus2",
        )
        self.assertEqual(reg.build_plan(**args), reg.build_plan(**args))


class ApplyTests(unittest.TestCase):
    def test_apply_builds_connection_payload(self):
        plan = reg.build_plan(
            foundry_agent="ooa-agent",
            data_agent_endpoint="https://example/da",
            workspace_id="ws-123",
            region="westus2",
        )

        out = reg._apply(
            plan,
            approver="urruegg",
            connection_factory=lambda payload: {"id": "conn-1", "sent": payload},
        )

        self.assertEqual(out["action"], "apply")
        self.assertEqual(out["approvedBy"], "urruegg")
        self.assertEqual(out["connection"]["sent"]["tool"]["type"], "fabric_data_agent")
        self.assertEqual(out["connection"]["id"], "conn-1")

    def test_apply_rejects_bot_approver(self):
        plan = reg.build_plan("ooa-agent", "https://e/da", "ws", "westus2")

        with self.assertRaises(SystemExit):
            reg._apply(plan, approver="copilot[bot]", connection_factory=lambda p: {})

    def test_apply_rejects_empty_approver(self):
        plan = reg.build_plan("ooa-agent", "https://e/da", "ws", "westus2")

        with self.assertRaises(SystemExit):
            reg._apply(plan, approver="", connection_factory=lambda p: {})


class CliTests(unittest.TestCase):
    _BASE = [
        "--foundry-agent", "ooa-agent",
        "--data-agent-endpoint", "https://x",
        "--workspace-id", "ws-1",
    ]

    def test_default_action_is_plan(self):
        # main() returns 0 on the default (plan) path without an approver.
        self.assertEqual(reg.main(self._BASE), 0)

    def test_apply_without_approval_raises(self):
        with self.assertRaises(SystemExit):
            reg.main(self._BASE + ["--action", "apply"])

    def test_apply_with_bot_approver_raises(self):
        with self.assertRaises(SystemExit):
            reg.main(self._BASE + ["--action", "apply", "--approved-to-apply", "copilot[bot]"])


if __name__ == "__main__":
    unittest.main()
