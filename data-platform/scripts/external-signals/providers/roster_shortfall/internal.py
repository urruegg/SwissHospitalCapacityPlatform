"""Derive roster-shortfall raw events from gold roster rows."""
from __future__ import annotations


def read(gold: dict) -> dict:
    events = []
    for row in gold.get("fact_roster", []):
        if row["scheduled"] < row["required"]:
            events.append({
                "eventId": f"roster-{row['hospital']}-{row['ward_id']}-{row['shift']}-{row['date']}",
                "severity": "Moderate",
                "cantons": ["ZH"],
                "ward": row["ward_id"],
                "time": f"{row['date']}T00:00:00Z",
                "expires": None,
                "uri": None,
            })
    return {"events": events}
