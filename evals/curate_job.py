"""Online curation job (Sprint 30 M5).

Walking skeleton of the scheduled Curate step (design §8). It reads recent
**scored** ``agent_interactions`` through the same source seam the online-eval
job uses (:mod:`lib.online_store`), applies the curator selection policy, and
returns an advisory summary: candidate versioned-dataset rows (with lineage) and
a GitHub-issue backlog grouped by agent + failing metric.

Advisory-only (NFR-LEARN-002): this job **emits drafts**. It never writes a
dataset file, opens an issue, or mutates any agent asset. A human reviews the
returned rows / backlog, signs off, and applies changes gated by the offline
regression suite + ``approved-to-apply``.

PHI-safety (ADR-0016 / NFR-LEARN-001): the backlog carries only ids / counts /
metrics. Dataset rows carry the already-redacted record fields (the eval
fixtures), never new PHI.
"""

from __future__ import annotations

import json
from typing import Any

from lib import curator, online_store

Record = dict[str, Any]

DEFAULT_RATE = 0.1
DEFAULT_SEED = 0
DEFAULT_LIMIT = 500


def run_curation(
    source: online_store.InteractionSource,
    *,
    rate: float = DEFAULT_RATE,
    seed: int = DEFAULT_SEED,
    agent: str | None = None,
    limit: int = DEFAULT_LIMIT,
    low_score_threshold: float = curator.DEFAULT_LOW_SCORE_THRESHOLD,
) -> dict[str, Any]:
    """Read scored records, curate, and return an advisory summary."""
    records = source.read_recent(agent=agent, limit=limit)
    scored = [r for r in records if r.get("eval", {}).get("scored")]
    selected = curator.select(
        scored, random_rate=rate, seed=seed, low_score_threshold=low_score_threshold
    )
    by_reason: dict[str, int] = {}
    for sel in selected:
        for reason in sel["reasons"]:
            by_reason[reason] = by_reason.get(reason, 0) + 1
    return {
        "considered": len(scored),
        "selected": len(selected),
        "datasetRows": curator.to_dataset_rows(selected),
        "backlog": curator.to_backlog_items(selected),
        "byReason": by_reason,
    }


def main(argv: list[str] | None = None) -> int:
    """Entrypoint. Uses the Cosmos store when configured, else an empty store."""
    source = online_store.build_store_from_env()
    if source is None:
        source = online_store.InMemoryStore([])
    summary = run_curation(source, rate=DEFAULT_RATE, seed=DEFAULT_SEED)
    # Print an advisory digest (counts + backlog), not the full dataset rows.
    digest = {
        "considered": summary["considered"],
        "selected": summary["selected"],
        "byReason": summary["byReason"],
        "backlog": summary["backlog"],
    }
    print(json.dumps(digest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
