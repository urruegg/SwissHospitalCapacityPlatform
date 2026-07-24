"""Derive supply-stock raw events from gold supply rows."""
from __future__ import annotations


def read(gold: dict) -> dict:
    events = []
    for row in gold.get("fact_supply", []):
        if row["on_hand"] < row["reorder_point"]:
            events.append({
                "eventId": f"supply-{row['hospital']}-{row['item']}-{row['date']}",
                "severity": "Moderate",
                "cantons": ["ZH"],
                "item": row["item"],
                "time": f"{row['date']}T00:00:00Z",
                "expires": None,
                "uri": None,
            })
    return {"events": events}
