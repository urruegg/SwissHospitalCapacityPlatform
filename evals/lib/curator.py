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

import copy
import random
from datetime import datetime, timezone
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def to_dataset_rows(selected: list[Selection]) -> list[Record]:
    """Turn selections into candidate versioned-dataset rows with lineage.

    Each row is a deep copy of the source interaction with its ``eval`` reset to
    ``{"scored": false}``, a ``curation`` lineage block added (source id, reasons,
    timestamp, ``signedOff: false``, ``reviewer: null``), and an ``expected`` block
    preserved (or an empty dict for a reviewer to fill). The source record is not
    mutated. Rows are advisory until a human sets ``signedOff`` and commits them.
    """
    rows: list[Record] = []
    for sel in selected:
        record = sel["record"]
        row = copy.deepcopy(record)
        row["eval"] = {"scored": False}
        row.setdefault("expected", {})
        row["curation"] = {
            "sourceInteractionId": record.get("interactionId"),
            "reasons": list(sel["reasons"]),
            "curatedAt": _now_iso(),
            "signedOff": False,
            "reviewer": None,
        }
        rows.append(row)
    return rows


# Metrics synthesised from non-evaluator selection reasons.
_REASON_METRICS = {
    THUMBS_DOWN: "user_feedback",
    MISREFUSAL: "refusal_correctness",
}


def _failing_metrics(record: Record, reasons: list[str]) -> set[str]:
    """Metrics a selection should file a backlog finding against.

    Derived from concrete signals only: evaluators that failed or scored below
    threshold, plus synthetic metrics for thumbs-down and mis-refusal. A pure
    random sample contributes no metric (it feeds the dataset, not the backlog).
    """
    metrics: set[str] = set()
    scores = record.get("eval", {}).get("scores", {})
    for name, verdict in scores.items():
        if verdict.get("passed") is False or verdict.get("score", 1.0) < DEFAULT_LOW_SCORE_THRESHOLD:
            metrics.add(name)
    for reason in reasons:
        if reason in _REASON_METRICS:
            metrics.add(_REASON_METRICS[reason])
    return metrics


def to_backlog_items(selected: list[Selection]) -> list[dict[str, Any]]:
    """Group selections into advisory GitHub-issue drafts by agent + failing metric.

    Advisory-only (NFR-LEARN-002): returns drafts; it never opens an issue. Each
    draft is PHI-safe (NFR-LEARN-001) — it carries the agent, the failing metric,
    a count, and the source interaction ids, never raw prompt or answer text.
    Deterministically ordered by (agent, metric).
    """
    groups: dict[tuple[str, str], list[str]] = {}
    for sel in selected:
        record = sel["record"]
        agent = record.get("agent", "unknown")
        iid = record.get("interactionId")
        for metric in _failing_metrics(record, sel["reasons"]):
            groups.setdefault((agent, metric), []).append(iid)

    items: list[dict[str, Any]] = []
    for (agent, metric), ids in sorted(groups.items()):
        ids_sorted = sorted(ids)
        count = len(ids_sorted)
        id_lines = "\n".join(f"- `{i}`" for i in ids_sorted)
        body = (
            f"**Advisory only** (NFR-LEARN-002). Curated finding for `{agent}` on "
            f"metric **{metric}**: {count} interaction(s) flagged for human review.\n\n"
            f"Source interactions (lineage):\n{id_lines}\n\n"
            "No prompt, knowledge source, guardrail, or model is changed by this "
            "issue. A human reviews the curated dataset rows and applies changes "
            "gated by the offline regression suite + `approved-to-apply`."
        )
        items.append({
            "agent": agent,
            "metric": metric,
            "title": f"[learn][{agent}] {metric}: {count} interaction(s) need review",
            "labels": ["learn", "advisory", f"agent:{agent}", f"metric:{metric}"],
            "count": count,
            "interactionIds": ids_sorted,
            "body": body,
        })
    return items
