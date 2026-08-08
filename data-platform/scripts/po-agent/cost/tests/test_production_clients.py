"""Sprint 41 WS-RET Task RET.4: real Cost Management + Copilot usage clients.

Reading `cost/azure_cost.py` and `cost/copilot_cost.py` first (per the task's
diligence requirement) shows the pure-logic functions the production clients
below must satisfy:

    azure_cost.get_effective_prod_cost(client, scope, start, end)
        -> client.query_actual_cost(scope, start, end) -> {amount, currency}
    copilot_cost.get_copilot_cost(client, start, end)
        -> client.get_usage(start, end) -> {turns, cost, currency}

This differs from the plan's sample in two ways, both confirmed by reading
the real code/environment before writing (see the module docstrings in
`azure_cost.py`/`copilot_cost.py` for the full rationale):

1. `azure-mgmt-costmanagement` is not an installed dependency here
   (verified: `ModuleNotFoundError: No module named 'azure.mgmt'`), so the
   Cost Management client is a raw REST call exposing exactly
   `query_actual_cost(scope, start, end)` - not a raw SDK
   `CostManagementClient`, whose shape (`client.query.usage(...)`) would
   not match what `get_effective_prod_cost` calls.
2. `session_store_reader`/`SessionStoreClient` (the plan's sample import
   for Copilot cost) do NOT exist anywhere in this repo (verified via
   `grep -r "session_store_reader\\|SessionStoreClient"`). The Copilot
   usage client here instead wraps the GitHub REST Billing Usage API,
   the real authoritative-cost source `docs/agent_cost.md` already names.

Every client is exercised here with an injected fake `http_request`/
`token_provider` so no test ever makes a real network call.
"""
from __future__ import annotations

import azure_cost
import copilot_cost
from azure_cost import _CostManagementQueryClient
from azure_cost import build_production_client as build_cost_client
from copilot_cost import _GitHubCopilotBillingUsageClient
from copilot_cost import build_production_client as build_copilot_client


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


# ---------------------------------------------------------------------------
# azure_cost.build_production_client
# ---------------------------------------------------------------------------


def test_build_cost_client_exposes_scope_and_no_network():
    # Construction must not call get_token()/requests (both lazily deferred
    # to query_actual_cost()) - if it did, this would raise since no
    # credential/network is available in CI.
    client = build_cost_client(subscription_id="sub-123")
    assert hasattr(client, "query_actual_cost")
    assert client.default_scope == "/subscriptions/sub-123"


def test_cost_management_client_posts_actual_cost_query_and_parses_amount():
    calls = {}

    def fake_http_request(method, url, headers=None, json=None, timeout=None):
        calls["method"] = method
        calls["url"] = url
        calls["body"] = json
        return _FakeResponse(
            {
                "properties": {
                    "columns": [{"name": "Cost"}, {"name": "Currency"}],
                    "rows": [[90_000.0, "CHF"]],
                }
            }
        )

    client = _CostManagementQueryClient(
        token_provider=lambda: "tok", http_request=fake_http_request
    )
    result = client.query_actual_cost("/subscriptions/sub-123", "2026-07-01", "2026-07-31")

    assert result == {"amount": 90_000.0, "currency": "CHF"}
    assert calls["method"] == "POST"
    assert "/subscriptions/sub-123/providers/Microsoft.CostManagement/query" in calls["url"]
    assert calls["body"]["type"] == "ActualCost"
    assert calls["body"]["timePeriod"]["from"] == "2026-07-01T00:00:00Z"
    assert calls["body"]["timePeriod"]["to"] == "2026-07-31T00:00:00Z"


def test_cost_management_client_defaults_amount_when_no_rows():
    client = _CostManagementQueryClient(
        token_provider=lambda: "tok",
        http_request=lambda *a, **k: _FakeResponse({"properties": {"columns": [], "rows": []}}),
    )
    result = client.query_actual_cost("/subscriptions/sub-123", "2026-07-01", "2026-07-31")
    assert result == {"amount": 0.0, "currency": "USD"}


def test_cost_client_feeds_get_effective_prod_cost():
    client = _CostManagementQueryClient(
        token_provider=lambda: "tok",
        http_request=lambda *a, **k: _FakeResponse(
            {
                "properties": {
                    "columns": [{"name": "Cost"}, {"name": "Currency"}],
                    "rows": [[42.0, "CHF"]],
                }
            }
        ),
    )
    observation = azure_cost.get_effective_prod_cost(
        client, "/subscriptions/sub-123", "2026-07-01", "2026-07-31"
    )
    assert observation.amount == 42.0
    assert observation.currency == "CHF"


# ---------------------------------------------------------------------------
# copilot_cost.build_production_client
# ---------------------------------------------------------------------------


def test_build_copilot_client_defaults_username_and_no_network(monkeypatch):
    monkeypatch.delenv("GITHUB_COPILOT_BILLING_USER", raising=False)
    client = build_copilot_client()
    assert hasattr(client, "get_usage")
    assert client._username == "urruegg"


def test_build_copilot_client_honours_username_override(monkeypatch):
    monkeypatch.setenv("GITHUB_COPILOT_BILLING_USER", "someone-else")
    client = build_copilot_client()
    assert client._username == "someone-else"


def test_github_billing_usage_client_filters_window_and_product():
    calls = []

    def fake_http_request(method, url, headers=None, json=None, timeout=None):
        calls.append(url)
        return _FakeResponse(
            {
                "usageItems": [
                    {
                        "date": "2026-07-05T00:00:00Z",
                        "product": "copilot",
                        "quantity": 100,
                        "netAmount": 12.5,
                    },
                    {
                        "date": "2026-07-20T00:00:00Z",
                        "product": "copilot",
                        "quantity": 50,
                        "netAmount": 6.25,
                    },
                    {
                        "date": "2026-07-20T00:00:00Z",
                        "product": "actions",
                        "quantity": 999,
                        "netAmount": 999.0,
                    },
                    {
                        "date": "2026-06-01T00:00:00Z",
                        "product": "copilot",
                        "quantity": 999,
                        "netAmount": 999.0,
                    },
                ]
            }
        )

    client = _GitHubCopilotBillingUsageClient(
        username="urruegg", token_provider=lambda: "tok", http_request=fake_http_request
    )
    result = client.get_usage("2026-07-01", "2026-07-31")

    assert result == {"turns": 150, "cost": 18.75, "currency": "USD"}
    assert any("users/urruegg/settings/billing/usage" in u for u in calls)


def test_copilot_client_feeds_get_copilot_cost():
    client = _GitHubCopilotBillingUsageClient(
        username="urruegg",
        token_provider=lambda: "tok",
        http_request=lambda *a, **k: _FakeResponse(
            {
                "usageItems": [
                    {"date": "2026-07-10", "product": "copilot", "quantity": 10, "netAmount": 5.0}
                ]
            }
        ),
    )
    cost = copilot_cost.get_copilot_cost(client, "2026-07-01", "2026-07-31")
    assert cost.turns == 10
    assert cost.amount == 5.0
