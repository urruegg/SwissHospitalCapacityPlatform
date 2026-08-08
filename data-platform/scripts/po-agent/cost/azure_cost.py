"""WS-C Class C cost: read-only Azure Cost Management feed.

Wraps a read-only Cost Management query client so the effective PROD
Azure cost over a bounded window can be measured. No mutation; the live
client is injected so CI supplies a fake.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CostAmount:
    amount: float
    currency: str
    window_start: str
    window_end: str


def get_effective_prod_cost(
    client: Any, scope: str, window_start: str, window_end: str
) -> CostAmount:
    """Query effective (actual) PROD cost for ``scope`` over the window.

    ``client`` must expose a read-only ``query_actual_cost(scope, start,
    end) -> {amount, currency}``. Read-only: no budget or resource is
    mutated.
    """

    row = client.query_actual_cost(scope, window_start, window_end)
    return CostAmount(
        amount=float(row["amount"]),
        currency=str(row.get("currency", "CHF")),
        window_start=window_start,
        window_end=window_end,
    )


# ---------------------------------------------------------------------------
# Sprint 41 WS-RET Task RET.4: real Azure Cost Management client.
#
# Deviates from the plan's sample in two ways, verified against the real
# environment/code before writing:
#
# 1. ``azure-mgmt-costmanagement`` is not an installed dependency here
#    (verified: ``ModuleNotFoundError: No module named 'azure.mgmt'`` -
#    same finding ``liveproof/azure_clients.py`` already documented for
#    ``azure-mgmt-resourcegraph``) - the Cost Management Query REST API
#    is called directly instead, matching the injectable
#    ``_ResourceGraphQueryClient`` transport pattern that module
#    established for this repo.
# 2. The plan's sample handed a raw SDK ``CostManagementClient`` straight
#    to ``get_effective_prod_cost`` above, but that function calls
#    ``client.query_actual_cost(scope, start, end) -> {amount,
#    currency}`` - a narrower read-only surface than any SDK client
#    exposes. The client below implements exactly that method, so it is
#    a drop-in for the same fake ``cost/tests/test_feeds.py`` already
#    exercises.
# ---------------------------------------------------------------------------

_COST_MGMT_SCOPE = "https://management.azure.com/.default"
_COST_MGMT_API_VERSION = "2023-11-01"


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def _token_provider(scope: str):
    """Lazily-evaluated bearer-token provider (no network at construction
    time - only when the returned callable is invoked)."""

    def _get_token() -> str:
        from azure.identity import DefaultAzureCredential

        return DefaultAzureCredential().get_token(scope).token

    return _get_token


def _as_datetime(value: str) -> str:
    if len(value) == 10:  # YYYY-MM-DD
        return f"{value}T00:00:00Z"
    return value


class _CostManagementQueryClient:
    """Read-only Azure Cost Management client exposing only
    ``query_actual_cost(scope, start, end)`` (see module deviations note)."""

    def __init__(
        self,
        default_scope: str = None,
        token_provider: Any = None,
        http_request: Any = None,
        timeout: int = 10,
        api_version: str = _COST_MGMT_API_VERSION,
    ) -> None:
        self.default_scope = default_scope
        self._token_provider = token_provider or _token_provider(_COST_MGMT_SCOPE)
        self._http_request = http_request or _default_http_request
        self._timeout = timeout
        self._api_version = api_version

    def query_actual_cost(self, scope: str, start: str, end: str) -> dict[str, Any]:
        url = (
            f"https://management.azure.com{scope}/providers/Microsoft.CostManagement/"
            f"query?api-version={self._api_version}"
        )
        headers = {
            "Authorization": f"Bearer {self._token_provider()}",
            "Content-Type": "application/json",
        }
        body = {
            "type": "ActualCost",
            "timeframe": "Custom",
            "timePeriod": {"from": _as_datetime(start), "to": _as_datetime(end)},
            "dataset": {
                "granularity": "None",
                "aggregation": {"totalCost": {"name": "Cost", "function": "Sum"}},
            },
        }
        resp = self._http_request("POST", url, headers=headers, json=body, timeout=self._timeout)
        resp.raise_for_status()
        properties = resp.json().get("properties", {})
        columns = [c.get("name") for c in properties.get("columns", [])]
        rows = properties.get("rows", [])
        if not rows:
            return {"amount": 0.0, "currency": "USD"}
        row = rows[0]
        cost_idx = columns.index("Cost") if "Cost" in columns else 0
        currency_idx = columns.index("Currency") if "Currency" in columns else None
        return {
            "amount": float(row[cost_idx]),
            "currency": str(row[currency_idx]) if currency_idx is not None else "USD",
        }


def build_production_client(subscription_id: str) -> _CostManagementQueryClient:
    """Build the real Class C Azure Cost Management client.

    ``subscription_id`` fixes the default query scope
    (``/subscriptions/{subscription_id}``, exposed as ``.default_scope``)
    for callers (``runtime/app.py``'s ``get_tools()``) that need a scope
    without re-deriving it; ``query_actual_cost`` itself still takes an
    explicit ``scope`` so a caller/test that needs a narrower scope
    (resource group, management group) keeps working unchanged.
    """

    return _CostManagementQueryClient(default_scope=f"/subscriptions/{subscription_id}")
