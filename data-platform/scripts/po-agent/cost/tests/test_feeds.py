"""WS-C Class C cost: read-only feed + combined run-rate tests."""

from pathlib import Path

import azure_cost
import copilot_cost
import reconcile_bva

REPO_ROOT = Path(__file__).resolve().parents[5]

READ_ONLY_METHODS = {"query_actual_cost", "get_usage"}


class _FakeCostMgmt:
    def __init__(self, amount=90_000.0):
        self.amount = amount
        self.calls = []

    def query_actual_cost(self, scope, start, end):
        self.calls.append(("query_actual_cost", scope, start, end))
        return {"amount": self.amount, "currency": "CHF"}

    def __getattr__(self, name):
        raise AttributeError(f"read-only client: {name!r} not permitted")


class _FakeCopilotUsage:
    def __init__(self, cost=12_000.0, turns=240_000):
        self.cost = cost
        self.turns = turns
        self.calls = []

    def get_usage(self, start, end):
        self.calls.append(("get_usage", start, end))
        return {"cost": self.cost, "turns": self.turns, "currency": "CHF"}

    def __getattr__(self, name):
        raise AttributeError(f"read-only client: {name!r} not permitted")


def test_azure_and_copilot_feeds_are_read_only():
    az = _FakeCostMgmt()
    cp = _FakeCopilotUsage()

    a = azure_cost.get_effective_prod_cost(az, "sub-scope", "2026-07-01", "2026-07-31")
    c = copilot_cost.get_copilot_cost(cp, "2026-07-01", "2026-07-31")

    assert a.amount == 90_000.0
    assert c.turns == 240_000
    for call in az.calls + cp.calls:
        assert call[0] in READ_ONLY_METHODS


def test_combined_run_rate_reconciles_within_band():
    az = _FakeCostMgmt(amount=90_000.0)
    cp = _FakeCopilotUsage(cost=12_000.0)
    a = azure_cost.get_effective_prod_cost(az, "sub-scope", "2026-07-01", "2026-07-31")
    c = copilot_cost.get_copilot_cost(cp, "2026-07-01", "2026-07-31")

    obs = reconcile_bva.combined_run_rate(
        a.amount, c.amount, "CHF", "2026-07-01", "2026-07-31", "2026-07-31"
    )
    assert obs.amount == 102_000.0

    chunk = reconcile_bva.reconcile_bva(obs, repo_root=REPO_ROOT)
    assert chunk["classId"] == "C"
    assert chunk["status"] == "verified"


def test_feed_unavailable_degrades_to_snapshot():
    obs = reconcile_bva.CostObservation(
        amount=0.0,
        currency="CHF",
        window_start="2026-07-01",
        window_end="2026-07-31",
        feed="Azure Cost Management + GitHub Copilot usage",
        as_of="2026-07-31",
        ok=False,
    )
    chunk = reconcile_bva.reconcile_bva(obs, repo_root=REPO_ROOT)
    assert chunk["liveness"] == "snapshot"
    assert chunk["status"] == "partial"
    assert "baseline" in chunk["text"].lower()
