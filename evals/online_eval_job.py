"""Online continuous-eval job (Sprint 30 M4).

Walking skeleton of the scheduled Evaluate job (design §7). It samples recent
``agent_interactions``, scores each with the shared M3 evaluator library, writes
the verdict back onto the record, and returns a per-agent / per-evaluator
rollup. The Azure Container Apps *schedule* that invokes ``main`` is a deferred
infra output; the testable job logic and the Cosmos runtime seam live here.

PHI-safety (ADR-0016 / NFR-LEARN-001): the rollup carries only counts / rates /
ids, never raw prompt or answer text.
"""

from __future__ import annotations

import json
from typing import Any

from lib import online, online_store

Record = dict[str, Any]

DEFAULT_RATE = 0.15
DEFAULT_SEED = 1
DEFAULT_LIMIT = 500


def rollup(scored_records: list[Record]) -> dict[str, Any]:
    """Aggregate scored records into a per-agent / per-evaluator quality view.

    Empty-safe: no records yields ``{"agents": {}, "totalSampled": 0}`` with no
    division by zero.
    """
    agents: dict[str, Any] = {}
    for rec in scored_records:
        agent = rec.get("agent", "unknown")
        block = rec.get("eval", {})
        scores = block.get("scores", {})
        bucket = agents.setdefault(
            agent,
            {"sampled": 0, "passedAll": 0, "byEvaluator": {}},
        )
        bucket["sampled"] += 1
        if block.get("passedAll"):
            bucket["passedAll"] += 1
        for name, verdict in scores.items():
            ev = bucket["byEvaluator"].setdefault(name, {"scored": 0, "passed": 0})
            ev["scored"] += 1
            if verdict.get("passed"):
                ev["passed"] += 1

    for bucket in agents.values():
        sampled = bucket["sampled"]
        bucket["passedAllRate"] = bucket["passedAll"] / sampled if sampled else 0.0
        for ev in bucket["byEvaluator"].values():
            ev["passRate"] = ev["passed"] / ev["scored"] if ev["scored"] else 0.0

    return {"agents": agents, "totalSampled": len(scored_records)}


def run_online_eval(
    source: online_store.InteractionSource,
    sink: online_store.InteractionSink,
    *,
    rate: float = DEFAULT_RATE,
    seed: int = DEFAULT_SEED,
    agent: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    """Sample -> score -> write back -> rollup. Returns the rollup report."""
    records = source.read_recent(agent=agent, limit=limit)
    sampled = online.sample(records, rate=rate, seed=seed)
    scored: list[Record] = []
    for rec in sampled:
        annotated = online.score_and_annotate(rec)
        sink.update_eval(annotated["interactionId"], annotated["eval"])
        scored.append(annotated)
    return rollup(scored)


def main(argv: list[str] | None = None) -> int:
    """Entrypoint for the ACA job. Uses the Cosmos store when configured."""
    source = online_store.build_store_from_env()
    if source is None:
        source = online_store.InMemoryStore([])
    report = run_online_eval(source, source, rate=DEFAULT_RATE, seed=DEFAULT_SEED)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
