"""T1 - knowledge metrics + refresh-action library (Sprint 30 M8).

The deterministic advisory knowledge-refresh tool maps an uncited-claim gap
metric (citation_coverage / groundedness) to a targeted grounding-source refresh
action. propose_refresh_actions is the pure, order-stable core reused by the
end-to-end job. Non-knowledge metrics (prompt-only failures handled by M7) are
ignored here.
"""

from lib import knowledge_refresh as kr


def test_knowledge_metrics_are_the_grounding_gap_metrics():
    assert kr.KNOWLEDGE_METRICS == ("citation_coverage", "groundedness")


def test_refresh_action_library_covers_every_knowledge_metric():
    for metric in kr.KNOWLEDGE_METRICS:
        assert metric in kr.REFRESH_ACTION_LIBRARY
        assert isinstance(kr.REFRESH_ACTION_LIBRARY[metric], str)
        assert kr.REFRESH_ACTION_LIBRARY[metric].strip()


def test_propose_refresh_actions_returns_known_actions():
    actions = kr.propose_refresh_actions({"citation_coverage", "groundedness"})
    assert kr.REFRESH_ACTION_LIBRARY["citation_coverage"] in actions
    assert kr.REFRESH_ACTION_LIBRARY["groundedness"] in actions
    assert len(actions) == 2


def test_propose_refresh_actions_is_deterministically_ordered():
    a = kr.propose_refresh_actions({"groundedness", "citation_coverage"})
    b = kr.propose_refresh_actions({"citation_coverage", "groundedness"})
    assert a == b
    assert a == [
        kr.REFRESH_ACTION_LIBRARY["citation_coverage"],
        kr.REFRESH_ACTION_LIBRARY["groundedness"],
    ]


def test_non_knowledge_metrics_are_ignored():
    # actionability / advisory_voice / user_feedback are prompt-lane (M7) metrics;
    # a knowledge refresh must not propose actions for them.
    actions = kr.propose_refresh_actions(
        {"citation_coverage", "actionability", "user_feedback"}
    )
    assert actions == [kr.REFRESH_ACTION_LIBRARY["citation_coverage"]]


def test_empty_metrics_yields_no_actions():
    assert kr.propose_refresh_actions(set()) == []


def test_only_non_knowledge_metrics_yields_no_actions():
    assert kr.propose_refresh_actions({"actionability", "phi_leak"}) == []
