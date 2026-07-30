"""T2 - extract_knowledge_gaps (Sprint 30 M8).

Given the curator's advisory backlog items (agent + failing metric + lineage),
extract only the uncited-claim gaps (knowledge metrics), attaching the agent's
grounding sources and the targeted refresh action. Pure, deterministic, and
PHI-safe (ids + metric names only).
"""

from lib import knowledge_refresh as kr

GROUNDING = ["gold.encounter", "gold.bed_assignment", "reference-layer.ttl"]


def _backlog(agent, metric, ids):
    # Minimal shape of a curator.to_backlog_items entry.
    return {
        "agent": agent,
        "metric": metric,
        "title": f"[learn][{agent}] {metric}",
        "labels": ["learn", "advisory", f"agent:{agent}", f"metric:{metric}"],
        "count": len(ids),
        "interactionIds": list(ids),
        "body": "advisory",
    }


def test_extracts_only_knowledge_metric_items():
    items = [
        _backlog("ooa-agent", "citation_coverage", ["ix-1", "ix-2"]),
        _backlog("ooa-agent", "actionability", ["ix-3"]),  # prompt-lane -> excluded
        _backlog("ooa-agent", "groundedness", ["ix-4"]),
    ]
    gaps = kr.extract_knowledge_gaps(items, GROUNDING)
    metrics = [g["metric"] for g in gaps]
    assert metrics == ["citation_coverage", "groundedness"]


def test_gap_carries_lineage_action_and_grounding_sources():
    items = [_backlog("ooa-agent", "citation_coverage", ["ix-2", "ix-1"])]
    gaps = kr.extract_knowledge_gaps(items, GROUNDING)
    assert len(gaps) == 1
    gap = gaps[0]
    assert gap["metric"] == "citation_coverage"
    assert gap["count"] == 2
    assert gap["interactionIds"] == ["ix-1", "ix-2"]  # sorted
    assert gap["groundingSources"] == GROUNDING
    assert gap["action"] == kr.REFRESH_ACTION_LIBRARY["citation_coverage"]


def test_gaps_ordered_by_canonical_knowledge_metric_order():
    items = [
        _backlog("ooa-agent", "groundedness", ["ix-4"]),
        _backlog("ooa-agent", "citation_coverage", ["ix-1"]),
    ]
    gaps = kr.extract_knowledge_gaps(items, GROUNDING)
    assert [g["metric"] for g in gaps] == ["citation_coverage", "groundedness"]


def test_no_knowledge_items_yields_no_gaps():
    items = [
        _backlog("ooa-agent", "actionability", ["ix-3"]),
        _backlog("ooa-agent", "user_feedback", ["ix-5"]),
    ]
    assert kr.extract_knowledge_gaps(items, GROUNDING) == []


def test_empty_backlog_yields_no_gaps():
    assert kr.extract_knowledge_gaps([], GROUNDING) == []


def test_grounding_sources_are_copied_not_aliased():
    items = [_backlog("ooa-agent", "groundedness", ["ix-4"])]
    gaps = kr.extract_knowledge_gaps(items, GROUNDING)
    gaps[0]["groundingSources"].append("mutated")
    assert "mutated" not in GROUNDING
