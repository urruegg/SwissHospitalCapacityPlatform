"""Curator: select high-signal traces -> dataset rows + advisory backlog (Sprint 30 M5).

The Learn stage (design §8). A selection policy picks high-signal interactions —
evaluation failures, low scores, thumbs-down, mis-refusals, plus a small random
sample — from already-scored ``DC-AGENT-INTERACTION-v1`` records. Selected traces
become (a) candidate rows for a versioned dataset under
``evals/<agent>/datasets/vN/`` keeping lineage back to their ``interactionId``, and
(b) advisory GitHub-issue drafts grouped by agent + failing metric.

Advisory-only (NFR-LEARN-002): this module emits *drafts*. It never writes a
dataset file, opens an issue, or mutates a prompt / knowledge source / guardrail /
model. A human reviews, signs off, and applies.

PHI-safety (ADR-0016 / NFR-LEARN-001): selection and the backlog read only ids /
counts / scores / flags; no raw prompt or answer text is emitted into a backlog
item.
"""

from __future__ import annotations

import random
from typing import Any

Record = dict[str, Any]
Selection = dict[str, Any]

# Selection reason tags.
EVAL_FAILURE = "eval_failure"
LOW_SCORE = "low_score"
THUMBS_DOWN = "thumbs_down"
MISREFUSAL = "misrefusal"
RANDOM_SAMPLE = "random_sample"

DEFAULT_LOW_SCORE_THRESHOLD = 0.5


def _high_signal_reasons(record: Record, low_score_threshold: float) -> list[str]:
    reasons: list[str] = []
    block = record.get("eval", {})

    if block.get("scored") and block.get("passedAll") is False:
        reasons.append(EVAL_FAILURE)

    scores = block.get("scores", {})
    if any(v.get("score", 1.0) < low_score_threshold for v in scores.values()):
        reasons.append(LOW_SCORE)

    for ev in record.get("userEvents", []):
        if ev.get("type") == "thumbs" and ev.get("value") == "down":
            reasons.append(THUMBS_DOWN)
            break

    expected = record.get("expected")
    if expected is not None and "should_refuse" in expected:
        refused = bool(record.get("response", {}).get("refused", False))
        if refused != bool(expected["should_refuse"]):
            reasons.append(MISREFUSAL)

    return reasons


def select(
    scored_records: list[Record],
    *,
    random_rate: float = 0.1,
    seed: int = 0,
    low_score_threshold: float = DEFAULT_LOW_SCORE_THRESHOLD,
) -> list[Selection]:
    """Return high-signal selections plus a deterministic random sample.

    Each selection is ``{"record": <record>, "reasons": [...]}``. High-signal
    records are chosen by policy; the random sample is a seeded draw over the
    *remaining* (non-high-signal) records only, so it never double-counts.
    """
    random_rate = max(0.0, min(1.0, random_rate))
    selected: list[Selection] = []
    remaining: list[Record] = []

    for rec in scored_records:
        reasons = _high_signal_reasons(rec, low_score_threshold)
        if reasons:
            selected.append({"record": rec, "reasons": reasons})
        else:
            remaining.append(rec)

    if random_rate > 0.0:
        rng = random.Random(seed)
        for rec in remaining:
            if random_rate >= 1.0 or rng.random() < random_rate:
                selected.append({"record": rec, "reasons": [RANDOM_SAMPLE]})

    return selected
