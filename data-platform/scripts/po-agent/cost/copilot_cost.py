"""WS-C Class C cost: GitHub Copilot token/usage cost feed (read-only).

Converts a GitHub Copilot usage feed (turns / premium requests) over a
bounded window into a cost figure. The live usage client is injected;
CI supplies a fake. Read-only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CopilotCost:
    amount: float
    currency: str
    turns: int
    window_start: str
    window_end: str


def get_copilot_cost(
    client: Any,
    window_start: str,
    window_end: str,
    currency: str = "CHF",
) -> CopilotCost:
    """Measure GitHub Copilot usage cost over the window.

    ``client`` must expose a read-only ``get_usage(start, end) ->
    {turns, cost}``. Read-only: no entitlement or seat is mutated.
    """

    usage = client.get_usage(window_start, window_end)
    return CopilotCost(
        amount=float(usage["cost"]),
        currency=str(usage.get("currency", currency)),
        turns=int(usage.get("turns", 0)),
        window_start=window_start,
        window_end=window_end,
    )


# ---------------------------------------------------------------------------
# Sprint 41 WS-RET Task RET.4: real GitHub Copilot usage client.
#
# ``session_store_reader``/``SessionStoreClient`` (the plan's sample
# import) do NOT exist anywhere in this repo - verified:
# ``grep -r "session_store_reader\|SessionStoreClient"`` returns no hits.
# The GitHub Copilot CLI/VS Code session store that produced
# ``docs/BVA.md`` section 3.3 and ``docs/agent_cost.md``'s weekly
# AIU/token tables is a chat-environment-only construct (queried in this
# environment only via the ``copilot_sessionStoreSql``/chronicle tool,
# itself backed by a local SQLite file the VS Code extension manages) -
# it has no stable path or schema this repo can commit to, and it is not
# reachable at all from a deployed Azure Container App (there is no VS
# Code extension host running there). Inventing an import for it would
# violate this task's "do not invent" instruction.
#
# ``docs/agent_cost.md``'s own "How to get authoritative cost" section
# names the real, network-reachable, production-usable alternative: the
# GitHub REST Billing Usage API (``gh api
# /users/<user>/settings/billing/usage?year=<yyyy>``) - the same
# authoritative source that section says is required to turn the
# session-store AIU estimate into a real bill. That is what is wired up
# here, as a raw HTTP call (matching the injectable-transport pattern
# ``liveproof/azure_clients.py`` established for this repo), filtered
# client-side to the requested ``[start, end]`` window and the
# ``copilot`` product line.
# ---------------------------------------------------------------------------

import datetime as _dt

_DEFAULT_BILLING_USER = "urruegg"


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def _token_provider():
    """Lazily-evaluated GitHub token provider (no env/network access at
    construction time - only when the returned callable is invoked)."""

    def _get_token() -> str:
        import os

        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            raise RuntimeError("GITHUB_TOKEN/GH_TOKEN not set for Copilot billing usage")
        return token

    return _get_token


class _GitHubCopilotBillingUsageClient:
    """Read-only GitHub Copilot usage client exposing only
    ``get_usage(start, end)`` (see module deviations note)."""

    def __init__(
        self,
        username: str = None,
        token_provider: Any = None,
        http_request: Any = None,
        timeout: int = 10,
    ) -> None:
        self._username = username or _DEFAULT_BILLING_USER
        self._token_provider = token_provider or _token_provider()
        self._http_request = http_request or _default_http_request
        self._timeout = timeout

    def get_usage(self, start: str, end: str) -> dict[str, Any]:
        start_date = _dt.date.fromisoformat(start)
        end_date = _dt.date.fromisoformat(end)
        headers = {
            "Authorization": f"Bearer {self._token_provider()}",
            "Accept": "application/vnd.github+json",
        }
        turns = 0
        cost = 0.0
        for year in sorted({start_date.year, end_date.year}):
            url = f"https://api.github.com/users/{self._username}/settings/billing/usage?year={year}"
            resp = self._http_request("GET", url, headers=headers, timeout=self._timeout)
            resp.raise_for_status()
            for item in resp.json().get("usageItems", []):
                if str(item.get("product", "")).lower() != "copilot":
                    continue
                try:
                    item_date = _dt.date.fromisoformat(str(item.get("date", ""))[:10])
                except ValueError:
                    continue
                if not (start_date <= item_date <= end_date):
                    continue
                turns += int(item.get("quantity", 0) or 0)
                cost += float(item.get("netAmount", item.get("grossAmount", 0.0)) or 0.0)
        return {"turns": turns, "cost": cost, "currency": "USD"}


def build_production_client() -> _GitHubCopilotBillingUsageClient:
    """Build the real Class C GitHub Copilot usage client.

    ``GITHUB_COPILOT_BILLING_USER`` overrides the billing-usage username
    (defaults to the same account ``docs/agent_cost.md``'s authoritative-
    cost command already targets).
    """

    import os

    return _GitHubCopilotBillingUsageClient(
        username=os.environ.get("GITHUB_COPILOT_BILLING_USER")
    )
