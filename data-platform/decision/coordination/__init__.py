"""Sprint 26 WS-C — coordination runtime (design spec Sec 3.3 / 3.4, decision D5).

Turns an approved recommendation into a live, cross-role coordination ``Plan``:
the "golden thread" where a human-approved OOA expedite-discharge action drives
a ward's forecast occupancy down (e.g. Medicine A 102% -> 94%) and hands off to
DCA. Pure orchestration over an injected :class:`~coordination.store.PlanStore`
and the deterministic :func:`impact.compute_expected_impact.compute_expected_impact`
tool — no randomness, no wall-clock reads, no live Cosmos/network calls.
"""
