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


if __name__ == "__main__":
    unittest.main()
