"""Unit tests for the live Foundry registration factory (Sprint 26 WS-C).

The factory is the concrete ``registration_factory`` seam that
``register_decision_tier.apply`` calls in-VNet. It speaks the **Foundry Agent
Service** ``/agents`` REST API in eastus2 (ADR-0032) — the eight platform agents
are versioned ``agent`` objects, NOT OpenAI Assistants. Following
``fabric_data_agent_client.py``, both the token provider and the HTTP transport
are injected so the whole REST sequence is asserted without cloud: read the
agent's latest version, append a deterministic *function* tool to its definition
idempotently, set the decision-tier metadata, and POST the update (which the
service turns into a new immutable version).
"""
from __future__ import annotations

import copy
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
    """Serves a single agent object on GET and echoes the update on POST.

    ``agents`` maps agent name -> the ``agent`` object returned by
    ``GET /agents/{name}``. A GET for an unknown name yields HTTP 404.
    """

    def __init__(self, agents: Dict[str, Dict[str, Any]]):
        self._agents = agents
        self.calls: List[Dict[str, Any]] = []

    def __call__(self, method, url, headers=None, json=None, timeout=None):
        self.calls.append(
            {"method": method, "url": url, "headers": headers, "json": json}
        )
        name = url.split("/agents/")[1].split("?")[0]
        if method == "GET":
            agent = self._agents.get(name)
            if agent is None:
                return _FakeResponse({"error": "not found"}, status=404)
            return _FakeResponse(copy.deepcopy(agent))
        # POST /agents/{name} -> the service creates a new version. Echo an
        # AgentObject whose latest version carries the posted definition/metadata.
        body = dict(json or {})
        prior = self._agents.get(name, {})
        prior_ver = (((prior.get("versions") or {}).get("latest") or {}).get("version")) or "0"
        next_ver = str(int(prior_ver) + 1)
        return _FakeResponse(
            {
                "object": "agent",
                "id": name,
                "name": name,
                "state": "enabled",
                "versions": {
                    "latest": {
                        "object": "agent.version",
                        "id": f"{name}:{next_ver}",
                        "name": name,
                        "version": next_ver,
                        "definition": body.get("definition"),
                        "metadata": body.get("metadata"),
                    }
                },
            }
        )


def _agent(name: str, *, model: str = "gpt-5", tools=None, metadata=None) -> Dict[str, Any]:
    return {
        "object": "agent",
        "id": name,
        "name": name,
        "state": "enabled",
        "versions": {
            "latest": {
                "object": "agent.version",
                "id": f"{name}:4",
                "name": name,
                "version": "4",
                "description": "",
                "definition": {
                    "kind": "prompt",
                    "model": model,
                    "instructions": f"{name} instructions",
                    "reasoning": {"effort": "low"},
                    "tools": list(tools) if tools is not None else [],
                },
                "metadata": dict(metadata) if metadata is not None else {},
            }
        },
    }


_FABRIC_TOOL = {
    "type": "fabric_dataagent_preview",
    "fabric_dataagent_preview": {"project_connections": [{"project_connection_id": "conn-1"}]},
}


def _make(transport: _FakeTransport, token: str = "tok-123"):
    return lf.make_registration_factory(
        token_provider=lambda: token,
        http_request=transport,
    )


class TestScope(unittest.TestCase):
    def test_scope_is_ai_azure_com(self):
        # The Foundry Agent Service data plane requires the ai.azure.com audience;
        # cognitiveservices.azure.com returns 401 (Sprint 26 WS-C root cause).
        self.assertEqual(lf.FOUNDRY_SCOPE, "https://ai.azure.com/.default")


class TestBuildFunctionTool(unittest.TestCase):
    def test_shape_is_a_flat_responses_function_tool(self):
        tool = reg.build_plan("ooa")["tool"]
        fn = lf.build_function_tool(tool)
        self.assertEqual(fn["type"], "function")
        # Flat Responses-API shape: name/description/parameters at the top level,
        # NOT nested under a "function" key (that is the Assistants API shape).
        self.assertEqual(fn["name"], "decision_tier_coordination_ooa")
        self.assertNotIn("function", fn)
        self.assertIn("parameters", fn)
        self.assertEqual(fn["parameters"]["type"], "object")
        self.assertEqual(set(fn.keys()), {"type", "name", "description", "parameters"})

    def test_deterministic(self):
        tool = reg.build_plan("csa")["tool"]
        self.assertEqual(lf.build_function_tool(tool), lf.build_function_tool(tool))


class TestFactoryRestSequence(unittest.TestCase):
    def _agents(self):
        return {
            "ooa-agent": _agent("ooa-agent", model="gpt-5", tools=[_FABRIC_TOOL]),
            "dca-agent": _agent("dca-agent", model="gpt-5", tools=[]),
        }

    def _payload(self, role: str):
        return {
            "foundryAgent": f"{role}-agent",
            "tool": reg.build_plan(role)["tool"],
            "region": "eastus2",
        }

    def test_reads_agent_then_posts_update(self):
        t = _FakeTransport(self._agents())
        factory = _make(t)
        result = factory(self._payload("ooa"))
        self.assertEqual(result["agentName"], "ooa-agent")
        self.assertEqual(result["status"], "registered")
        self.assertEqual(result["agentVersion"], "5")  # new version promoted
        self.assertEqual(t.calls[0]["method"], "GET")
        self.assertTrue(t.calls[0]["url"].split("?")[0].endswith("/agents/ooa-agent"))
        self.assertEqual(t.calls[1]["method"], "POST")
        self.assertTrue(t.calls[1]["url"].split("?")[0].endswith("/agents/ooa-agent"))

    def test_targets_agents_path_not_assistants(self):
        t = _FakeTransport(self._agents())
        factory = _make(t)
        factory(self._payload("dca"))
        for call in t.calls:
            self.assertIn("/agents/", call["url"])
            self.assertNotIn("/assistants", call["url"])

    def test_url_carries_api_version_and_bearer_auth(self):
        t = _FakeTransport(self._agents())
        factory = _make(t, token="secret-tok")
        factory(self._payload("dca"))
        for call in t.calls:
            self.assertIn("api-version=", call["url"])
            self.assertEqual(call["headers"]["Authorization"], "Bearer secret-tok")

    def test_preserves_definition_and_appends_function_tool(self):
        t = _FakeTransport(self._agents())
        factory = _make(t)
        factory(self._payload("ooa"))
        posted = t.calls[1]["json"]["definition"]
        # Existing definition fields are preserved verbatim.
        self.assertEqual(posted["kind"], "prompt")
        self.assertEqual(posted["model"], "gpt-5")
        self.assertEqual(posted["instructions"], "ooa-agent instructions")
        self.assertEqual(posted["reasoning"], {"effort": "low"})
        tool_types = [tool["type"] for tool in posted["tools"]]
        self.assertIn("fabric_dataagent_preview", tool_types)  # existing kept
        self.assertIn("function", tool_types)  # new appended
        fn_names = [tl["name"] for tl in posted["tools"] if tl["type"] == "function"]
        self.assertEqual(fn_names, ["decision_tier_coordination_ooa"])

    def test_creates_tools_list_when_absent(self):
        agents = {"dca-agent": _agent("dca-agent", tools=None)}
        # simulate a definition with no 'tools' key at all
        del agents["dca-agent"]["versions"]["latest"]["definition"]["tools"]
        t = _FakeTransport(agents)
        factory = _make(t)
        factory(self._payload("dca"))
        posted = t.calls[1]["json"]["definition"]
        self.assertEqual([tl["type"] for tl in posted["tools"]], ["function"])

    def test_sets_and_preserves_metadata_as_strings(self):
        agents = {
            "ooa-agent": _agent(
                "ooa-agent", tools=[_FABRIC_TOOL], metadata={"existing_key": "keep-me"}
            )
        }
        t = _FakeTransport(agents)
        factory = _make(t)
        factory(self._payload("ooa"))
        meta = t.calls[1]["json"]["metadata"]
        self.assertEqual(meta["existing_key"], "keep-me")  # preserved
        self.assertEqual(meta["decision_tier_role"], "ooa")
        self.assertTrue(meta["decision_tier_lever_catalog"].endswith("ooa.yaml"))
        for value in meta.values():
            self.assertIsInstance(value, str)

    def test_idempotent_when_tool_already_present(self):
        already = {
            "type": "function",
            "name": "decision_tier_coordination_ooa",
            "description": "x",
            "parameters": {"type": "object", "properties": {}},
        }
        agents = {"ooa-agent": _agent("ooa-agent", tools=[_FABRIC_TOOL, already])}
        t = _FakeTransport(agents)
        factory = _make(t)
        result = factory(self._payload("ooa"))
        self.assertTrue(result["toolAlreadyPresent"])
        posted = t.calls[1]["json"]["definition"]
        fn_names = [tl["name"] for tl in posted["tools"] if tl["type"] == "function"]
        self.assertEqual(fn_names, ["decision_tier_coordination_ooa"])  # no duplicate

    def test_raises_when_agent_not_found(self):
        t = _FakeTransport(self._agents())
        factory = _make(t)
        with self.assertRaises(RuntimeError):
            factory(self._payload_named("ghost-agent"))

    def _payload_named(self, name: str):
        return {
            "foundryAgent": name,
            "tool": reg.build_plan("ooa")["tool"],
            "region": "eastus2",
        }


class TestApplyWithLiveFactory(unittest.TestCase):
    """The produced factory plugs into register_decision_tier.apply end-to-end."""

    def _agents(self):
        return {"bmca-agent": _agent("bmca-agent", tools=[])}

    def test_apply_uses_factory_and_keeps_hitl_gate(self):
        t = _FakeTransport(self._agents())
        factory = _make(t)
        applied = reg.apply(reg.build_plan("bmca"), "urruegg", registration_factory=factory)
        self.assertEqual(applied["action"], "apply")
        self.assertEqual(applied["approvedBy"], "urruegg")
        self.assertEqual(applied["registration"]["agentName"], "bmca-agent")
        self.assertEqual(applied["registration"]["status"], "registered")

    def test_apply_refuses_bot_before_touching_foundry(self):
        t = _FakeTransport(self._agents())
        factory = _make(t)
        with self.assertRaises(SystemExit):
            reg.apply(reg.build_plan("bmca"), "some-bot[bot]", registration_factory=factory)
        self.assertEqual(t.calls, [])  # no REST call attempted


if __name__ == "__main__":
    unittest.main()
