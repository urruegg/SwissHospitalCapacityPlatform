"""Online continuous-eval sampler + scorer (Sprint 30 M4).

The online half of the Evaluate stage (design §7). A scheduled job samples
recent ``DC-AGENT-INTERACTION-v1`` records (rate-limited), scores each with the
**same** shared evaluator library used by the offline gate (:mod:`lib.harness`),
and annotates the record's ``eval`` block. Deterministic + dependency-free: the
sample is seeded and the evaluators are pure (no LLM, no network), so the job is
fully reproducible in CI.

PHI-safety (ADR-0016 / NFR-LEARN-001): scoring reads only the already-redacted
record fields; the annotated ``eval`` block carries scores / booleans / ids, never
raw prompt or answer text.
"""

from __future__ import annotations

import copy
import random
from datetime import datetime, timezone
from typing import Any

from lib.harness import EVALUATORS, score_interaction

Record = dict[str, Any]

EVALUATOR_SET = "seed-v1"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sample(records: list[Record], *, rate: float, seed: int) -> list[Record]:
    """Return a deterministic, rate-limited subset of ``records``.

    ``rate`` is clamped to ``[0, 1]``. The selection is reproducible for a fixed
    ``seed`` (Bernoulli draw per record, preserving input order) so the same
    scheduled window yields the same sample on a re-run.
    """
    rate = max(0.0, min(1.0, rate))
    if rate == 0.0:
        return []
    if rate == 1.0:
        return list(records)
    rng = random.Random(seed)
    return [rec for rec in records if rng.random() < rate]


def score_and_annotate(record: Record) -> Record:
    """Score one record and return a copy with a populated ``eval`` block.

    The input record is not mutated. The ``expected`` labels are unknown online,
    so evaluators that need a label (refusal correctness) fall back to their
    vacuous-pass behaviour.
    """
    results = score_interaction(record, None)
    scores = {
        r.evaluator: {"score": r.score, "passed": r.passed, "detail": r.detail}
        for r in results
    }
    annotated = copy.deepcopy(record)
    annotated["eval"] = {
        "scored": True,
        "evaluatorSet": EVALUATOR_SET,
        "sampledAt": _now_iso(),
        "scores": scores,
        "passedAll": all(r.passed for r in results),
    }
    return annotated


# The six evaluator names, in report order (for rollups / dashboards).
EVALUATOR_NAMES = tuple(ev.__name__ for ev in EVALUATORS)
