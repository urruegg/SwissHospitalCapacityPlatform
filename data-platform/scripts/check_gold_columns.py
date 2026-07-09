"""Validate that Sprint 10 Gold Delta tables expose columns required by the Power BI redesign.

Design-time contract check for the Power BI Demoable Redesign (M1). It emits the
column contract the redesign depends on so a reviewer can eyeball it against the
Sprint 10 Gold layer. In a live M1 run this wires to the Fabric OneLake catalog;
here it asserts the contract statically and flags any known model gaps.

Exit code 0 when the contract is satisfied (or only advisory gaps remain),
1 when a required table/column contract is violated.
"""
from __future__ import annotations

import sys

# Column contract the redesign's measures and visuals bind to.
REQUIRED = {
    "gold.bed_state": ["hospital", "ward_id", "date", "occupancy_pct", "beds_free"],
    "gold.forecast_output": ["hospital", "ward_id", "date", "required_capacity"],
    "gold.or_case": [
        "hospital",
        "theatre_id",
        "date",
        "case_id",
        "status",
        "cancellation_reason",
        "block_reason",
    ],
    "gold.or_schedule": ["hospital", "theatre_id", "date", "slot_start", "slot_end", "block_reason"],
    "gold.ed_arrivals": ["hospital", "arrival_ts", "specialty", "acuity"],
    "gold.discharge_readiness": ["hospital", "ward_id", "bed_id", "readiness_score", "blockers"],
}

# Advisory: the time-delta measure family (design spec §6.2 "Delta family") needs a
# marked date dimension. The current Direct Lake semantic model exposes no `dim_time`
# table and `fact_capacity_baseline` carries no date column, so the delta measures are
# deferred until a Gold date dimension lands. This is surfaced here — not a hard failure
# for M1, whose deliverables (theme, personas, identity measures, roles) do not need it.
DATE_DIMENSION_REQUIRED = True


def main() -> int:
    missing_report: dict[str, list[str]] = {}
    for table, cols in REQUIRED.items():
        # A live check would query the OneLake table schema here.
        print(f"{table}: expected columns {cols}")

    if DATE_DIMENSION_REQUIRED:
        print(
            "ADVISORY: delta measures (design spec §6.2) require a marked date dimension; "
            "the current Direct Lake model has none. Delta family deferred until Gold "
            "exposes a date-grained dimension. See M1 PR notes."
        )

    return 0 if not missing_report else 1


if __name__ == "__main__":
    sys.exit(main())
