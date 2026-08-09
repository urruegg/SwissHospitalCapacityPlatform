"""Sprint 43 WS-7 -- shared role -> lever registry, wiring the Sprint 26 WS-B
lever catalog + formula registry (data-platform/decision/impact/
compute_expected_impact.py) into the Sprint 39 P2 worklist/decisions loop.

Only roles listed here get a REAL, catalog-grounded recommendation; roles not
listed keep the existing honest "role effect pending" placeholder
(build_worklist) or today's non-dca decide() behavior -- no regression.

``has_effect`` distinguishes real SimState actuation (only dca today, via
apps/sim-capacity/src/closedloop/effect.py's DischargeBarrier/set_status
branch) from predicted-impact-only roles (ooa, bmca): their Accept is still a
real, tracked HITL decision on a real number, but never mutates SimState (no
`effect:` block exists yet for these two levers in
data-platform/decision/levers/{ooa,bmca}.yaml).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoleLever:
    lever_id: str
    has_effect: bool


ROLE_LEVERS: dict[str, RoleLever] = {
    "dca": RoleLever(lever_id="DCA-UNBLOCK-BARRIER", has_effect=True),
    "ooa": RoleLever(lever_id="OOA-EXPEDITE-DISCHARGE", has_effect=False),
    "bmca": RoleLever(lever_id="BMCA-REBALANCE-CENSUS", has_effect=False),
}

# BMCA-REBALANCE-CENSUS needs a `to_ward` label; SimState is single-ward MVP
# (see loop/ward_scope), so this is a fixed, documented assumption -- the same
# shape as DCA's own fixed `_BARRIER_TYPE = "transport"` constant.
ASSUMED_SISTER_WARD = "Medicine B"

# OOA-EXPEDITE-DISCHARGE needs a `before` label; no time-of-day concept exists
# in SimState, so this is a fixed, documented assumption.
ASSUMED_EXPEDITE_DEADLINE = "end-of-shift"
