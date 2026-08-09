"""Role worklist builder (Sprint 39 P2). Turns the in-host SimState into a role's
observations + one grounded DC-INSIGHT-style recommendation. Deterministic; the
impact is the deterministic compute_expected_impact on the seeded occupancy (never
an LLM guess). MVP implements dca (the walking skeleton); other roles list
observations + a placeholder recommendation until their effect lands."""
from __future__ import annotations

from typing import Any, Dict

from closedloop.sim_state import SimState, Stage
from impact.compute_expected_impact import compute_expected_impact

from .ward_scope import require_single_ward, ward_of

_CATALOG = [{"lever_id": "DCA-UNBLOCK-BARRIER", "owner_role": "dca", "impact_formula_ref": "unblock_barrier_beds"}]
_BARRIER_TYPE = "transport"
_CITATIONS = ["gold.discharge_candidates", "gold.fact_capacity_baseline"]


def _live_citations(fabric: Any, table: str) -> list[dict[str, Any]]:
    if fabric is None:
        return []
    try:
        return fabric.query(table)
    except Exception:
        # Honest graceful-miss -- mirrors FabricDeltaClient.query()'s existing
        # behavior. A live-grounding hiccup must never break an otherwise
        # successful worklist read.
        return []


def build_worklist(
    role: str, state: SimState, provenance: str = "simulated", fabric: Any = None
) -> Dict[str, Any]:
    # Single-ward MVP: the dca grounding + the hospital-wide barrier effect only
    # stay consistent on one ward (see loop/ward_scope). Fail loudly on multi-ward.
    require_single_ward(state)
    ward = ward_of(state)
    if role == "dca":
        barriers = sorted(state.open_barriers(_BARRIER_TYPE), key=lambda b: b.barrier_id)
        observations = [
            {
                "patient": b.patient_id, "ward": ward, "readiness": "BLOCKED",
                "barrier": b.barrier_type, "aged_h": b.aged_h, "provenance": provenance,
            }
            for b in barriers
        ]
        n = len(barriers)
        live_citations = _live_citations(fabric, _CITATIONS[0])
        if n == 0:
            # n==0 guard: compute_expected_impact raises on n<=0, so short-circuit
            # with an honest zero-impact recommendation rather than 500-ing.
            recommendation = {
                "lever_id": "DCA-UNBLOCK-BARRIER",
                "params": {"barrier_type": _BARRIER_TYPE, "n": 0, "ward": ward},
                "predicted_impact": {"metric": "beds", "value": 0},
                "insight_text": f"No open {_BARRIER_TYPE} barriers on {ward}; nothing to unblock",
                "citations": _CITATIONS,
                "liveGroundingCitations": live_citations,
            }
            return {"role": role, "ward": ward, "observations": observations,
                    "recommendation": recommendation, "provenance": provenance}
        gold_impact = {"forecast": [{"wardId": ward, "horizonH": 72,
                                     "bedCapacity": state.ward(ward).staffed_capacity,
                                     "forecastOccupiedBeds": state.occupancy(ward)}]}
        params = {"barrier_type": _BARRIER_TYPE, "n": n, "ward": ward}
        impact = compute_expected_impact("DCA-UNBLOCK-BARRIER", params, gold_impact, catalog=_CATALOG)
        recommendation = {
            "lever_id": "DCA-UNBLOCK-BARRIER", "params": params,
            "predicted_impact": {"metric": "beds", "value": int(impact["delta"])},
            "insight_text": f"Resolve {n} {_BARRIER_TYPE} barriers to free {impact['delta']} beds on {ward}",
            "citations": _CITATIONS,
            "liveGroundingCitations": live_citations,
        }
        return {"role": role, "ward": ward, "observations": observations,
                "recommendation": recommendation, "provenance": provenance}
    # Non-DCA roles: observations + advisory placeholder (full effect is follow-on).
    ready = [p.patient_id for p in state.patients_in_stage(Stage.DISCHARGE_READY)]
    return {
        "role": role, "ward": ward,
        "observations": [
            {"patient": p, "ward": ward, "readiness": "READY", "provenance": provenance}
            for p in sorted(ready)
        ],
        "recommendation": {
            "lever_id": None,
            "insight_text": "role effect pending (S38 multi-agent enrichment)",
            "citations": _CITATIONS,
            "liveGroundingCitations": _live_citations(fabric, _CITATIONS[0]),
        },
        "provenance": provenance,
    }
