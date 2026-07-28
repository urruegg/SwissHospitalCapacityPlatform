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
