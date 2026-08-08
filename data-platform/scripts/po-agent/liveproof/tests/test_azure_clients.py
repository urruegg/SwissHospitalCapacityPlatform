"""Sprint 41 WS-RET Task RET.3: real read-only Azure clients for Class B probes.py.

Reading `liveproof/probes.py` first (per the task's diligence requirement)
shows `liveProof`'s injected `clients=` dict is looked up with these EXACT
keys/methods, no arguments beyond the fake in `test_probes.py`:

    clients["resource_graph"].query(kql) -> list[dict]
    clients["fabric_rest"].list_workspaces() -> list
    clients["foundry_agents"].list_agents() -> list[dict]

This differs from the plan's sample in two ways, both confirmed by reading
the real code before writing:

1. `list_agents()` takes NO `project_endpoint` argument (unlike the plan's
   `list_agents(self, project_endpoint)`); the Foundry project endpoint must
   be baked into the client at build time instead. This repo already has
   that convention in `data-platform/decision/foundry/live_factory.py`
   (`FOUNDRY_SCOPE`, `DEFAULT_ENDPOINT`, `DEFAULT_PROJECT`, ADR-0032 SIT
   defaults, overridable via `FOUNDRY_PROJECT_ENDPOINT`/`FOUNDRY_PROJECT_NAME`)
   - reused here rather than re-derived.
2. `azure-mgmt-resourcegraph` is not an installed dependency in this
   environment (verified: `ModuleNotFoundError: No module named
   'azure.mgmt'`), so the Resource Graph client is a raw REST call
   (DefaultAzureCredential + requests) instead of the mgmt SDK, matching the
   injectable-transport pattern `ontology/data_agent.py`'s
   `_RawFabricDataAgentClient` already established for this repo.

Every client is exercised here with an injected fake `http_request`/
`token_provider` so no test ever makes a real network call.
"""
from __future__ import annotations

import azure_clients
from azure_clients import (
    _FabricRestWorkspacesClient,
    _FoundryAgentsListClient,
    _ResourceGraphQueryClient,
    build_production_clients,
)


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_build_production_clients_returns_read_only_client_map():
    clients = build_production_clients(subscription_id="sub-123")
    assert set(clients.keys()) == {"resource_graph", "fabric_rest", "foundry_agents"}
    # probes.py calls these exact methods with no extra arguments.
    assert hasattr(clients["resource_graph"], "query")
    assert hasattr(clients["fabric_rest"], "list_workspaces")
    assert hasattr(clients["foundry_agents"], "list_agents")


def test_build_production_clients_does_not_touch_the_network():
    # Construction must not call get_token()/requests (both lazily deferred
    # to a later query()/list_workspaces()/list_agents() call) - if it did,
    # this would raise since no credential/network is available in CI.
    build_production_clients(subscription_id="sub-123")


def test_resource_graph_client_posts_kql_and_returns_data():
    calls = {}

    def fake_http_request(method, url, headers=None, json=None, timeout=None):
        calls["method"] = method
        calls["url"] = url
        calls["body"] = json
        return _FakeResponse({"data": [{"sku": "F2"}]})

    client = _ResourceGraphQueryClient(
        subscription_id="sub-123", token_provider=lambda: "tok", http_request=fake_http_request
    )
    rows = client.query("resources | where type =~ 'microsoft.fabric/capacities'")

    assert rows == [{"sku": "F2"}]
    assert calls["method"] == "POST"
    assert "Microsoft.ResourceGraph/resources" in calls["url"]
    assert calls["body"]["subscriptions"] == ["sub-123"]
    assert "microsoft.fabric/capacities" in calls["body"]["query"]


def test_fabric_rest_client_lists_workspaces():
    def fake_http_request(method, url, headers=None, json=None, timeout=None):
        assert method == "GET"
        assert url == "https://api.fabric.microsoft.com/v1/workspaces"
        return _FakeResponse({"value": [{"id": "ws-1"}, {"id": "ws-2"}]})

    client = _FabricRestWorkspacesClient(token_provider=lambda: "tok", http_request=fake_http_request)
    assert client.list_workspaces() == [{"id": "ws-1"}, {"id": "ws-2"}]


def test_foundry_agents_client_lists_agents_from_configured_project():
    calls = {}

    def fake_http_request(method, url, headers=None, json=None, timeout=None):
        calls["method"] = method
        calls["url"] = url
        return _FakeResponse({"value": [{"name": "bmca-agent", "status": "Running"}]})

    client = _FoundryAgentsListClient(
        endpoint="https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com",
        project="ai-ihzhhpf-sit-eastus2-project",
        token_provider=lambda: "tok",
        http_request=fake_http_request,
    )
    agents = client.list_agents()

    assert agents == [{"name": "bmca-agent", "status": "Running"}]
    assert calls["method"] == "GET"
    assert (
        calls["url"]
        == "https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com/api/projects/"
        "ai-ihzhhpf-sit-eastus2-project/agents?api-version=2025-05-15-preview"
    )


def test_foundry_agents_client_defaults_to_adr_0032_sit_project(monkeypatch):
    monkeypatch.delenv("FOUNDRY_PROJECT_ENDPOINT", raising=False)
    monkeypatch.delenv("FOUNDRY_PROJECT_NAME", raising=False)
    client = azure_clients._FoundryAgentsListClient(token_provider=lambda: "tok")
    assert client._endpoint == "https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com"
    assert client._project == "ai-ihzhhpf-sit-eastus2-project"
