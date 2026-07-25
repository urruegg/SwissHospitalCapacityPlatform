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
