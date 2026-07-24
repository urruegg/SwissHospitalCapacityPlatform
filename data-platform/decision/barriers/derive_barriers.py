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


def _require_utc_clears_at(candidate: Dict[str, Any]) -> Optional[str]:
    clears_at = candidate.get("clears_at")
    if clears_at is None:
        return None
    if not isinstance(clears_at, str) or not clears_at.endswith("Z"):
        raise ValueError(
            f"candidate clears_at must be a UTC ISO-8601 string ending in 'Z', "
            f"got {clears_at!r} (candidate_key={candidate.get('candidate_key')!r})"
        )
    return clears_at


def derive_barriers(
    candidates: List[Dict[str, Any]],
    owner_map: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Collapse ``candidates`` (flat discharge-blocked patient rows) into a
    ranked list of systemic barrier dicts, grouped by ``barrier_type``.

    Each candidate dict may contain: ``candidate_key`` (opaque str),
    ``ward`` (ontology ward ID), ``barrier_type`` (required), ``aged_h``
    (hours blocked), ``clears_at`` (UTC ISO-8601 str ending in "Z" --
    required precondition, see below), ``bed_impact`` (positive int,
    defaults to 1). The input list/dicts are never mutated.

    Precondition: ``clears_at``, when present, must be a UTC ISO-8601 string
    ending in "Z". The "latest clears_at" aggregation below uses a lexical
    string max, which is only correct when every timestamp shares the same
    (UTC) offset -- a mixed-offset input (e.g. "+02:00" vs "Z") would
    otherwise silently produce a wrong "latest" value. Any candidate whose
    ``clears_at`` doesn't end in "Z" raises ``ValueError``.

    Aggregation per barrier_type:
      - ``candidate_count``: number of member candidates.
      - ``bed_impact``: sum of member ``bed_impact`` values.
      - ``aged_h``: MAX member ``aged_h`` -- the worst-aged candidate drives
        urgency for the whole barrier.
      - ``clears_at``: the LATEST (max) member ``clears_at`` -- the barrier
        is only fully cleared once its slowest member clears.
      - ``wards``: sorted unique list of member wards.
      - ``owner_role``: looked up from ``owner_map`` when given (unlisted
        barrier_types fall back to ``"dca"`` directly -- ``DEFAULT_OWNER_MAP``
        is not consulted in that case); when ``owner_map`` is omitted,
        ``DEFAULT_OWNER_MAP`` is used instead, with the same ``"dca"``
        fallback for barrier_types it doesn't list.

    Ranking is deterministic: ``bed_impact`` DESC, then ``aged_h`` DESC,
    then ``barrier_type`` ASC as a stable tiebreak.

    Raises ``ValueError`` if any candidate is missing ``barrier_type``, has
    an invalid ``bed_impact`` (missing/zero/negative/bool are all rejected
    except "missing", which defaults to 1), or has a non-UTC ``clears_at``.
    """
    effective_owner_map = owner_map if owner_map is not None else DEFAULT_OWNER_MAP

    groups: Dict[str, Dict[str, Any]] = {}
    for candidate in candidates:
        barrier_type = _require_barrier_type(candidate)
        bed_impact = _require_bed_impact(candidate)
        aged_h = candidate.get("aged_h")
        clears_at = _require_utc_clears_at(candidate)
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
