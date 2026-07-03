"""Discharge recommender generator — ``discharge.recommended`` events.

Consumes ``discharge.scored`` events, groups them by simulated hour, and
emits the top-K ranked recommendations per hour.

Recommendation buckets by score band (deterministic):

    score >= 0.9  → ``discharge-today``
    0.75 ≤ score < 0.9  → ``discharge-tomorrow``
    0.5  ≤ score < 0.75 → ``no-action``
    score < 0.5        → ``no-action``

A subset of high-scoring recommendations is flipped to ``discharge-blocked``
or ``escalate`` with mock blockers, to give downstream consumers a realistic
distribution of ``recommendedAction`` values.

Rate target: ~10/hr aggregate — parameterised as ``top_k_per_hour``.

Design spec: §4.3 (event kinds) + §3 (``hcp:DischargeRecommendation``).
"""

from __future__ import annotations

import random
from typing import Iterable, Iterator, List, Optional

from calibration.hospital_presets import HospitalPreset
from envelope import build_envelope

_MODEL_RUN_ID = "discharge-recommender-v0.1"

_ACTIONS_HIGH = ("discharge-today", "discharge-tomorrow", "discharge-blocked")
_ACTION_ESCALATE = "escalate"
_ACTION_NO_ACTION = "no-action"

_BLOCKER_POOL = (
    "awaiting-social-work",
    "awaiting-transport",
    "pending-med-reconciliation",
    "awaiting-family-consent",
    "awaiting-rehab-slot",
    "outstanding-lab-results",
)


def _action_for(score: float) -> str:
    if score >= 0.9:
        return "discharge-today"
    if score >= 0.75:
        return "discharge-tomorrow"
    return _ACTION_NO_ACTION


def generate_discharge_recommendations(
    preset: HospitalPreset,
    scored_events: Iterable[dict],
    sim_run_id: str,
    seed: int,
    hospital_id: Optional[str] = None,
    top_k_per_hour: int = 10,
    blocker_ratio: float = 0.2,
    escalate_ratio: float = 0.1,
) -> Iterator[dict]:
    """Yield ``discharge.recommended`` envelopes ranked top-K per hour."""
    hid = hospital_id or preset.hospital_id

    # Bucket scored events by simulated hour (YYYY-MM-DDTHH).
    buckets: dict[str, List[dict]] = {}
    for e in scored_events:
        if e.get("eventKind") != "discharge.scored":
            continue
        hour_key = e["simulatedAt"][:13]
        buckets.setdefault(hour_key, []).append(e)

    rng = random.Random(seed)

    for hour_key in sorted(buckets.keys()):
        candidates = buckets[hour_key]
        # Rank by score descending; tie-break on encounterId for determinism.
        ranked = sorted(
            candidates,
            key=lambda ev: (-ev["payload"]["score"], ev["payload"]["encounterId"]),
        )[:top_k_per_hour]

        for rank, scored in enumerate(ranked, start=1):
            score = scored["payload"]["score"]
            base_action = _action_for(score)
            blockers: List[str] = []
            action = base_action

            if base_action in {"discharge-today", "discharge-tomorrow"}:
                roll = rng.random()
                if roll < blocker_ratio:
                    action = "discharge-blocked"
                    n_blockers = rng.randint(1, 3)
                    blockers = rng.sample(_BLOCKER_POOL, k=n_blockers)
                elif roll < blocker_ratio + escalate_ratio:
                    action = _ACTION_ESCALATE
                    blockers = [rng.choice(_BLOCKER_POOL)]

            rec_id = f"DREC-{scored['payload']['encounterId']}-{hour_key.replace(':', '').replace('-', '')}"
            payload = {
                "recommendationId": rec_id,
                "encounterId": scored["payload"]["encounterId"],
                "rank": rank,
                "basedOnScoreId": scored["payload"]["scoreId"],
                "score": score,
                "recommendedAction": action,
                "blockers": blockers,
                "producedByModelRunId": _MODEL_RUN_ID,
                "producedAt": scored["simulatedAt"],
                "explanationTokens": scored["payload"].get("explanationTokens", []),
                "purposeTag": "bed-management",
            }
            # Reuse the scored event's simulated time as the recommendation time.
            from envelope import _iso_utc  # local import to keep public surface small
            from datetime import datetime

            when = datetime.fromisoformat(scored["simulatedAt"].replace("Z", "+00:00"))
            if when.tzinfo is not None:
                when = when.replace(tzinfo=None)
            yield build_envelope(
                event_kind="discharge.recommended",
                hospital_id=hid,
                simulated_at=when,
                payload=payload,
                sim_run_id=sim_run_id,
                seed=seed,
            )
