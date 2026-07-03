"""Discharge scorer generator — ``discharge.scored`` events.

For every active encounter (i.e. between ``encounter.admitted`` and the
matching ``encounter.transitioned`` with ``status='finished'``), emit a
discharge-readiness score once per hour.

Formula (deterministic, no jitter):

    score = min(1.0, days_since_admission / expected_LOS_days)

Design spec: §4.3 (event kinds) + §3 (``hcp:DischargeReadinessScore``).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Iterator, List, Optional

from calibration.hospital_presets import HospitalPreset
from envelope import build_envelope, _iso_utc

_MODEL_RUN_ID = "discharge-scorer-v0.1"


def _parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 string; strip tz so we can compare against naive ``start_time``."""
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


def _extract_active_encounters(events: Iterable[dict]) -> List[dict]:
    """Return per-encounter metadata: admittedAt + expectedLOSDays + finishedAt."""
    admits: dict[str, dict] = {}
    for e in events:
        kind = e.get("eventKind")
        payload = e.get("payload") or {}
        enc_id = payload.get("encounterId")
        if not enc_id:
            continue
        if kind == "encounter.admitted":
            admits[enc_id] = {
                "encounterId": enc_id,
                "admittedAt": _parse_iso(e["simulatedAt"]),
                "expectedLOSDays": payload.get("expectedLOSDays") or 5,
                "finishedAt": None,
                "requestedSpecialtyId": payload.get("requestedSpecialtyServiceId"),
            }
        elif kind == "encounter.transitioned" and payload.get("status") == "finished":
            if enc_id in admits:
                admits[enc_id]["finishedAt"] = _parse_iso(e["simulatedAt"])
    return list(admits.values())


def generate_discharge_scores(
    preset: HospitalPreset,
    encounter_events: Iterable[dict],
    sim_run_id: str,
    seed: int,
    start_time: datetime,
    duration_hours: int,
    hospital_id: Optional[str] = None,
) -> Iterator[dict]:
    """Yield ``discharge.scored`` envelopes, one per active encounter per hour."""
    hid = hospital_id or preset.hospital_id
    encounters = _extract_active_encounters(encounter_events)
    if not encounters:
        return

    end_time = start_time + timedelta(hours=duration_hours)

    for hour_offset in range(duration_hours):
        tick = start_time + timedelta(hours=hour_offset)
        for enc in encounters:
            admitted_at = enc["admittedAt"]
            finished_at = enc["finishedAt"]
            if tick < admitted_at:
                continue
            if finished_at is not None and tick >= finished_at:
                continue
            if tick >= end_time:
                continue

            elapsed_hours = (tick - admitted_at).total_seconds() / 3600.0
            days_since = elapsed_hours / 24.0
            expected_los = max(1, int(enc["expectedLOSDays"]))
            score = min(1.0, days_since / expected_los)
            score = round(max(0.0, score), 4)

            score_id = (
                f"DSCORE-{enc['encounterId']}-{tick.strftime('%Y%m%dT%H')}"
            )
            explanation = [
                f"days-since-admission={days_since:.2f}",
                f"expected-LOS-days={expected_los}",
            ]
            payload = {
                "scoreId": score_id,
                "encounterId": enc["encounterId"],
                "score": score,
                "assessedAt": _iso_utc(tick),
                "daysSinceAdmission": round(days_since, 3),
                "expectedLOSDays": expected_los,
                "producedByModelRunId": _MODEL_RUN_ID,
                "explanationTokens": explanation,
                "purposeTag": "bed-management",
            }
            yield build_envelope(
                event_kind="discharge.scored",
                hospital_id=hid,
                simulated_at=tick,
                payload=payload,
                sim_run_id=sim_run_id,
                seed=seed,
            )
