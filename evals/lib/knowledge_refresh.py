"""Deterministic advisory knowledge-refresh tool for the lead agent (Sprint 30 M8).

The **Improve - knowledge** stage of the closed-loop foundation (design section 8 /
milestone M8). Realises "knowledge refresh for the top uncited-claim gaps (Foundry
IQ / Fabric grounding source)" as a **deterministic, advisory** tool consistent
with the repo's no-live-runtime posture (ADR-0002): given a curated backlog of
grounding-gap metrics for an agent, it names the grounding sources to review and
proposes targeted refresh actions, then validates the current grounding against
the offline regression gate.

An **uncited-claim gap** is exactly an interaction that fails a knowledge metric:
``citation_coverage`` (a claim with no ``Grounded on:`` citation) or
``groundedness`` (a claim not present in / derived from the grounded rows).
Prompt-lane metrics (actionability, advisory_voice, ...) are M7's concern and are
ignored here.

Advisory-only (NFR-LEARN-003): this module emits a *proposal*. It never writes a
grounding source, ontology file, ``AGENT.md``, or any file, opens an issue, or
mutates a knowledge source / model. A human reviews the proposal and refreshes the
grounding only after the offline regression suite passes **and** an explicit
``approved-to-apply``.

PHI-safety (ADR-0016 / NFR-LEARN-001): the tool reads only metric names,
interaction ids, and grounding-source names - never raw prompt or answer content
from a trace.
"""

from __future__ import annotations

from typing import Any, Iterable

from lib import curator, harness

# The metric names that signal an uncited-claim / grounding gap. Ordered as the
# canonical refresh-action order (citation gap first, then the deeper
# groundedness gap).
KNOWLEDGE_METRICS: tuple[str, ...] = ("citation_coverage", "groundedness")

# Knowledge metric -> targeted advisory grounding-source refresh action.
REFRESH_ACTION_LIBRARY: dict[str, str] = {
    "citation_coverage": (
        "Ensure every claimed figure has a retrievable grounding row: verify the "
        "gold snapshots (gold.encounter, gold.bed_assignment) are fresh and "
        "reachable, and surface the missing reference-layer concept through the "
        "Fabric Data Agent DC-INSIGHT-v1 grounding so the `Grounded on:` line can "
        "name a real source."
    ),
    "groundedness": (
        "Close the gap between produced claims and grounded rows: refresh or "
        "expand the grounding source (gold snapshots plus the reference-layer "
        "ontology docs/ontology/reference-layer.ttl) so the facts the answer needs "
        "actually exist to ground it - never let the agent fill the gap from "
        "memory."
    ),
}


def propose_refresh_actions(metrics: Iterable[str]) -> list[str]:
    """Return advisory refresh actions for the failing knowledge ``metrics``.

    Deterministically ordered by :data:`KNOWLEDGE_METRICS`. Non-knowledge metrics
    (prompt-lane failures handled by M7) are ignored, so an input mixing lanes
    yields only the knowledge-lane actions.
    """
    metric_set = set(metrics)
    return [
        REFRESH_ACTION_LIBRARY[metric]
        for metric in KNOWLEDGE_METRICS
        if metric in metric_set
    ]


def extract_knowledge_gaps(
    backlog_items: list[dict[str, Any]], grounding_sources: list[str]
) -> list[dict[str, Any]]:
    """Extract uncited-claim gaps from the curator's advisory ``backlog_items``.

    Keeps only items whose ``metric`` is a knowledge metric
    (:data:`KNOWLEDGE_METRICS`) - prompt-lane items are M7's concern. Each gap
    carries the failing metric, its interaction-id lineage (sorted), the agent's
    grounding sources (copied, not aliased), the interaction count, and the
    targeted refresh action. Gaps are ordered by the canonical
    :data:`KNOWLEDGE_METRICS` order. Pure and PHI-safe: ids + metric names only.
    """
    order = {metric: i for i, metric in enumerate(KNOWLEDGE_METRICS)}
    gaps: list[dict[str, Any]] = []
    for item in backlog_items:
        metric = item.get("metric")
        if metric not in order:
            continue
        ids = sorted(item.get("interactionIds", []))
        gaps.append(
            {
                "metric": metric,
                "count": len(ids),
                "interactionIds": ids,
                "groundingSources": list(grounding_sources),
                "action": REFRESH_ACTION_LIBRARY[metric],
            }
        )
    gaps.sort(key=lambda g: order[g["metric"]])
    return gaps


def run_knowledge_refresh(
    *,
    agent: str,
    scored_records: list[dict],
    grounding_sources: list[str],
    gate_dataset_path,
    random_rate: float = 0.0,
    seed: int = 0,
    low_score_threshold: float = curator.DEFAULT_LOW_SCORE_THRESHOLD,
) -> dict:
    """Produce an advisory knowledge-refresh proposal for ``agent``.

    Improvement signal: the curated **scored records** for ``agent`` (design M5
    seam) drive the failing metrics via :func:`curator.select` +
    :func:`curator.to_backlog_items`; only the knowledge metrics
    (:data:`KNOWLEDGE_METRICS`) become gaps. Guardrail: the current grounding is
    only promotable-after-refresh if the **offline regression gate** over
    ``gate_dataset_path`` passes (:mod:`lib.harness`). ``random_rate`` defaults to
    ``0.0`` so only concrete grounding gaps - not a random sample - drive the
    proposal.

    Returns an advisory proposal dict. This function **never writes** a grounding
    source, ontology file, ``AGENT.md``, or any file, opens an issue, or mutates a
    model (NFR-LEARN-003): a human refreshes the grounding only after the offline
    gate passes **and** an explicit ``approved-to-apply``.
    """
    scored_for_agent = [
        r
        for r in scored_records
        if r.get("agent") == agent and r.get("eval", {}).get("scored")
    ]
    selected = curator.select(
        scored_for_agent,
        random_rate=random_rate,
        seed=seed,
        low_score_threshold=low_score_threshold,
    )
    backlog = curator.to_backlog_items(selected, low_score_threshold=low_score_threshold)

    gaps = extract_knowledge_gaps(backlog, grounding_sources)
    knowledge_metrics = [gap["metric"] for gap in gaps]
    source_ids = sorted({iid for gap in gaps for iid in gap["interactionIds"]})
    refresh_actions = propose_refresh_actions(set(knowledge_metrics))

    gate = harness.run_dataset(gate_dataset_path)

    rationale = (
        f"{len(source_ids)} interaction(s) across {len(knowledge_metrics)} "
        f"knowledge metric(s) flagged uncited-claim gap(s) against "
        f"{len(grounding_sources)} grounding source(s); offline gate "
        f"{'passed' if gate['passed'] else 'FAILED'}. Advisory only - refreshing "
        "the grounding requires the offline regression pass plus approved-to-apply."
    )

    return {
        "agent": agent,
        "knowledgeMetrics": knowledge_metrics,
        "sourceInteractionIds": source_ids,
        "groundingSources": list(grounding_sources),
        "refreshActions": refresh_actions,
        "gaps": gaps,
        "offlineGatePassed": gate["passed"],
        "advisory": True,
        "applied": False,
        "approvedToApply": False,
        "rationale": rationale,
    }
