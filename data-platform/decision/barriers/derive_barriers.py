"""Runtime-derived DCA barrier model (Sprint 26 WS-B, design Sec 3.3 item 3).

Collapses a flat list of discharge-blocked candidates into a ranked list of
SYSTEMIC barriers (the DCA "8 candidates collapse into 5 barriers" pattern
from the prototype). ``derive_barriers`` is a PURE, DETERMINISTIC function:
no randomness, no LLM, no I/O, no Fabric/gold table read or write. Per the
Slice-1 design decision (open item Q), the barrier model is runtime-derived
from candidate rows the caller already holds -- it is never persisted as a
new gold table.

Candidates must carry only SYNTHETIC/opaque fields (no PHI: no names, no
MRN) -- an opaque ``candidate_key``, an ontology ward ID, a ``barrier_type``,
an age in hours, an expected clear timestamp, and an optional bed impact.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

# DCA owns discharge barriers in Slice 1 (design Sec 3.3 item 3): every known
# barrier_type maps to "dca" today. Kept as a named, easily extensible
# constant so future slices (e.g. a barrier_type owned by another role) can
# add rows without touching the aggregation logic below.
DEFAULT_OWNER_MAP: Dict[str, str] = {
    "pharmacy": "dca",
    "transport": "dca",
    "social_placement": "dca",
    "imaging": "dca",
    "consult": "dca",
}

_FALLBACK_OWNER_ROLE = "dca"


def _require_barrier_type(candidate: Dict[str, Any]) -> str:
    barrier_type = candidate.get("barrier_type")
    if not isinstance(barrier_type, str) or not barrier_type.strip():
        raise ValueError(f"candidate missing barrier_type: {candidate!r}")
    return barrier_type


def _require_bed_impact(candidate: Dict[str, Any]) -> int:
    if "bed_impact" not in candidate:
        return 1
    value = candidate["bed_impact"]
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(
            f"candidate bed_impact must be a positive int, got {value!r} "
            f"(candidate_key={candidate.get('candidate_key')!r})"
        )
    return value


def derive_barriers(
    candidates: List[Dict[str, Any]],
    owner_map: Optional[Dict[str, str]] = None,
    now_h: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Collapse ``candidates`` (flat discharge-blocked patient rows) into a
    ranked list of systemic barrier dicts, grouped by ``barrier_type``.

    Each candidate dict may contain: ``candidate_key`` (opaque str),
    ``ward`` (ontology ward ID), ``barrier_type`` (required), ``aged_h``
    (hours blocked), ``clears_at`` (ISO-8601 str), ``bed_impact`` (positive
    int, defaults to 1). The input list/dicts are never mutated.

    ``now_h`` is accepted for API symmetry with other decision-tier tools
    (e.g. a future "as of" cutoff) but is not currently used by the pure
    aggregation below -- there is no clock read inside this function.

    Aggregation per barrier_type:
      - ``candidate_count``: number of member candidates.
      - ``bed_impact``: sum of member ``bed_impact`` values.
      - ``aged_h``: MAX member ``aged_h`` -- the worst-aged candidate drives
        urgency for the whole barrier.
      - ``clears_at``: the LATEST (max) member ``clears_at`` -- the barrier
        is only fully cleared once its slowest member clears.
      - ``wards``: sorted unique list of member wards.
      - ``owner_role``: looked up from ``owner_map`` (falling back to
        ``DEFAULT_OWNER_MAP``, then to ``"dca"`` for unmapped types).

    Ranking is deterministic: ``bed_impact`` DESC, then ``aged_h`` DESC,
    then ``barrier_type`` ASC as a stable tiebreak.

    Raises ``ValueError`` if any candidate is missing ``barrier_type`` or
    has an invalid ``bed_impact`` (missing/zero/negative/bool are all
    rejected except "missing", which defaults to 1).
    """
    effective_owner_map = owner_map if owner_map is not None else DEFAULT_OWNER_MAP

    groups: Dict[str, Dict[str, Any]] = {}
    for candidate in candidates:
        barrier_type = _require_barrier_type(candidate)
        bed_impact = _require_bed_impact(candidate)
        aged_h = candidate.get("aged_h")
        clears_at = candidate.get("clears_at")
        ward = candidate.get("ward")

        group = groups.setdefault(
            barrier_type,
            {
                "barrier_type": barrier_type,
                "candidate_count": 0,
                "bed_impact": 0,
                "aged_h": None,
                "clears_at": None,
                "wards": set(),
            },
        )
        group["candidate_count"] += 1
        group["bed_impact"] += bed_impact
        if aged_h is not None and (group["aged_h"] is None or aged_h > group["aged_h"]):
            group["aged_h"] = aged_h
        if clears_at is not None and (group["clears_at"] is None or clears_at > group["clears_at"]):
            group["clears_at"] = clears_at
        if ward is not None:
            group["wards"].add(ward)

    barriers: List[Dict[str, Any]] = []
    for barrier_type, group in groups.items():
        owner_role = effective_owner_map.get(barrier_type, _FALLBACK_OWNER_ROLE)
        barriers.append(
            {
                "barrier_type": barrier_type,
                "owner_role": owner_role,
                "candidate_count": group["candidate_count"],
                "bed_impact": group["bed_impact"],
                "aged_h": group["aged_h"],
                "clears_at": group["clears_at"],
                "wards": sorted(group["wards"]),
            }
        )

    barriers.sort(key=lambda b: (-b["bed_impact"], -(b["aged_h"] or 0), b["barrier_type"]))
    return barriers
