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
