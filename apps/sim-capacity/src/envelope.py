"""Shared envelope helper for eventstream generators.

All 6 event generators emit envelopes with the same outer shape (design spec
§4.3): ``eventKind`` + ``eventId`` + ``hospitalId`` + ``simulatedAt`` +
``emittedAt`` + ``simRunId`` + ``seed`` + ``payload``.

The helper builds an envelope from the per-event payload dict + the invariant
metadata carried by the calling generator. ``eventId`` defaults to a UUID4 hex
string (unique per event); ``emittedAt`` defaults to real wall-clock UTC.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _iso_utc(when: datetime) -> str:
    """Return an RFC 3339 UTC string, e.g. ``2027-01-15T10:23:00Z``."""
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    else:
        when = when.astimezone(timezone.utc)
    return when.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_envelope(
    event_kind: str,
    hospital_id: str,
    simulated_at: datetime,
    payload: Dict[str, Any],
    sim_run_id: str,
    seed: int,
    event_id: Optional[str] = None,
    emitted_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Assemble an event envelope per design spec §4.3."""
    return {
        "eventKind": event_kind,
        "eventId": event_id or uuid.uuid4().hex,
        "hospitalId": hospital_id,
        "simulatedAt": _iso_utc(simulated_at),
        "emittedAt": _iso_utc(emitted_at or datetime.now(tz=timezone.utc)),
        "simRunId": sim_run_id,
        "seed": seed,
        "payload": payload,
    }


ENVELOPE_REQUIRED_KEYS = frozenset(
    {
        "eventKind",
        "eventId",
        "hospitalId",
        "simulatedAt",
        "emittedAt",
        "simRunId",
        "seed",
        "payload",
    }
)
