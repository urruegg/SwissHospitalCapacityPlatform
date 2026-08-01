"""Ward-scoping helpers (Sprint 39 P2).

The dca walking skeleton grounds exactly one ward, and the Sprint 38 barrier
effect clears open barriers by ``barrier_type`` hospital-wide. Those two only
stay consistent (predicted == realised) on a single-ward snapshot, so the
worklist + decisions endpoints refuse a multi-ward snapshot loudly (ValueError
-> 400) rather than silently attributing another ward's barriers to the first
ward. The committed simulated-MVP snapshot is single-ward, so this never fires
on the demo path; a multi-ward extension is follow-on work.
"""
from __future__ import annotations

from closedloop.sim_state import SimState


def ward_of(state: SimState) -> str:
    """The sole ward id (alphabetically first, deterministic)."""
    return next(iter(sorted(state.wards)))


def require_single_ward(state: SimState) -> None:
    """Enforce the single-ward MVP assumption; raise ValueError otherwise."""
    if len(state.wards) != 1:
        raise ValueError(
            "dca worklist/decisions MVP supports exactly one ward; "
            f"got {len(state.wards)}"
        )
