"""Derive occupancy-breach raw events from gold bed-state rows."""
from __future__ import annotations


def read(gold: dict) -> dict:
    events = []
    for row in gold.get("fact_bed_state", []):
        if row["occupied"] > row["capacity"]:
            events.append({
                "eventId": f"occ-{row['hospital']}-{row['ward_id']}-{row['date']}",
                "severity": "Moderate",
                "cantons": ["ZH"],
                "ward": row["ward_id"],
                "time": f"{row['date']}T00:00:00Z",
                "expires": None,
                "uri": None,
            })
    return {"events": events}
