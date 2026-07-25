"""Unit tests for the live Foundry registration factory (Sprint 26 WS-C).

The factory is the concrete ``registration_factory`` seam that
``register_decision_tier.apply`` calls in-VNet. It speaks the Foundry Agents
(Assistants protocol) REST API in eastus2 (ADR-0032). Following
``fabric_data_agent_client.py``, both the token provider and the HTTP transport
are injected so the whole REST sequence is asserted without cloud: resolve the
assistant by name, merge a deterministic *function* tool idempotently, set the
decision-tier metadata, and POST the modify.
"""
from __future__ import annotations

import unittest
from typing import Any, Dict, List, Optional

from foundry import live_factory as lf
from foundry import register_decision_tier as reg


class _FakeResponse:
    def __init__(self, payload: Dict[str, Any], status: int = 200):
        self._payload = payload
        self._status = status

    def raise_for_status(self) -> None:
        if self._status >= 400:
            raise RuntimeError(f"HTTP {self._status}")

    def json(self) -> Dict[str, Any]:
        return self._payload


class _FakeTransport:
    """Records calls; serves a fixed assistant listing then echoes the modify."""

    def __init__(self, assistants: List[Dict[str, Any]]):
        self._assistants = assistants
        self.calls: List[Dict[str, Any]] = []

    def __call__(self, method, url, headers=None, json=None, timeout=None):
        self.calls.append(
            {"method": method, "url": url, "headers": headers, "json": json}
        )
        if method == "GET":
            return _FakeResponse({"data": self._assistants})
        # POST /{id} — echo the modified body back with the id from the URL.
        assistant_id = url.split("/assistants/")[1].split("?")[0]
        body = dict(json or {})
        body["id"] = assistant_id
        return _FakeResponse(body)


def _make(transport: _FakeTransport, token: str = "tok-123"):
    return lf.make_registration_factory(
        token_provider=lambda: token,
        http_request=transport,
    )


class TestBuildFunctionTool(unittest.TestCase):
    def test_shape_is_a_native_function_tool(self):
        tool = reg.build_plan("ooa")["tool"]
        fn = lf.build_function_tool(tool)
        self.assertEqual(fn["type"], "function")
        self.assertEqual(fn["function"]["name"], "decision_tier_coordination_ooa")
        self.assertIn("parameters", fn["function"])
        self.assertEqual(fn["function"]["parameters"]["type"], "object")
        # No non-native keys leak into the function tool (Assistants rejects them).
        self.assertEqual(set(fn["function"].keys()), {"name", "description", "parameters"})

    def test_deterministic(self):
        tool = reg.build_plan("csa")["tool"]
        self.assertEqual(lf.build_function_tool(tool), lf.build_function_tool(tool))


class TestFactoryRestSequence(unittest.TestCase):
    def _assistants(self):
        return [
            {"id": "asst_ooa", "name": "ooa-agent", "tools": [{"type": "code_interpreter"}]},
            {"id": "asst_dca", "name": "dca-agent", "tools": []},
        ]

    def test_resolves_by_name_and_posts_to_assistant_id(self):
        t = _FakeTransport(self._assistants())
        factory = _make(t)
        payload = {
            "foundryAgent": "ooa-agent",
            "tool": reg.build_plan("ooa")["tool"],
            "region": "eastus2",
        }
        result = factory(payload)
        self.assertEqual(result["assistantId"], "asst_ooa")
        self.assertEqual(result["status"], "registered")
        # GET list first, then POST to /asst_ooa.
        self.assertEqual(t.calls[0]["method"], "GET")
        self.assertEqual(t.calls[1]["method"], "POST")
        self.assertIn("/assistants/asst_ooa", t.calls[1]["url"])

    def test_url_carries_api_version_and_bearer_auth(self):
        t = _FakeTransport(self._assistants())
        factory = _make(t, token="secret-tok")
        factory(
            {
                "foundryAgent": "dca-agent",
                "tool": reg.build_plan("dca")["tool"],
                "region": "eastus2",
            }
        )
        for call in t.calls:
            self.assertIn("api-version=", call["url"])
            self.assertEqual(call["headers"]["Authorization"], "Bearer secret-tok")

    def test_preserves_existing_tools_and_appends_function_tool(self):
        t = _FakeTransport(self._assistants())
        factory = _make(t)
        factory(
            {
                "foundryAgent": "ooa-agent",
                "tool": reg.build_plan("ooa")["tool"],
                "region": "eastus2",
            }
        )
        posted = t.calls[1]["json"]
        types = [tool["type"] for tool in posted["tools"]]
        self.assertIn("code_interpreter", types)  # existing kept
        self.assertIn("function", types)  # new appended
        names = [
            tool["function"]["name"] for tool in posted["tools"] if tool["type"] == "function"
        ]
        self.assertEqual(names, ["decision_tier_coordination_ooa"])

    def test_sets_decision_tier_metadata_as_strings(self):
        t = _FakeTransport(self._assistants())
        factory = _make(t)
        factory(
            {
                "foundryAgent": "ooa-agent",
                "tool": reg.build_plan("ooa")["tool"],
                "region": "eastus2",
            }
        )
        meta = t.calls[1]["json"]["metadata"]
        self.assertEqual(meta["decision_tier_role"], "ooa")
        self.assertTrue(meta["decision_tier_lever_catalog"].endswith("ooa.yaml"))
        for value in meta.values():
            self.assertIsInstance(value, str)

    def test_idempotent_when_tool_already_present(self):
        assistants = [
            {
                "id": "asst_ooa",
                "name": "ooa-agent",
                "tools": [
                    {"type": "function", "function": {"name": "decision_tier_coordination_ooa"}}
                ],
            }
        ]
        t = _FakeTransport(assistants)
        factory = _make(t)
        result = factory(
            {
                "foundryAgent": "ooa-agent",
                "tool": reg.build_plan("ooa")["tool"],
                "region": "eastus2",
            }
        )
        self.assertTrue(result["toolAlreadyPresent"])
        posted = t.calls[1]["json"]
        names = [
            tool["function"]["name"] for tool in posted["tools"] if tool["type"] == "function"
        ]
        self.assertEqual(names, ["decision_tier_coordination_ooa"])  # no duplicate

    def test_raises_when_assistant_not_found(self):
        t = _FakeTransport(self._assistants())
        factory = _make(t)
        with self.assertRaises(RuntimeError):
            factory(
                {
                    "foundryAgent": "ghost-agent",
                    "tool": reg.build_plan("ooa")["tool"],
                    "region": "eastus2",
                }
            )


class TestApplyWithLiveFactory(unittest.TestCase):
    """The produced factory plugs into register_decision_tier.apply end-to-end."""

    def test_apply_uses_factory_and_keeps_hitl_gate(self):
        t = _FakeTransport(
            [{"id": "asst_bmca", "name": "bmca-agent", "tools": []}]
        )
        factory = _make(t)
        applied = reg.apply(
            reg.build_plan("bmca"), "urruegg", registration_factory=factory
        )
        self.assertEqual(applied["action"], "apply")
        self.assertEqual(applied["approvedBy"], "urruegg")
        self.assertEqual(applied["registration"]["assistantId"], "asst_bmca")

    def test_apply_refuses_bot_before_touching_foundry(self):
        t = _FakeTransport([{"id": "asst_bmca", "name": "bmca-agent", "tools": []}])
        factory = _make(t)
        with self.assertRaises(SystemExit):
            reg.apply(reg.build_plan("bmca"), "some-bot[bot]", registration_factory=factory)
        self.assertEqual(t.calls, [])  # no REST call attempted


if __name__ == "__main__":
    unittest.main()
