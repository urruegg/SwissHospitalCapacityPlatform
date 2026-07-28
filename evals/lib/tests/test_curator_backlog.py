"""M5 T3 (RED) — curator advisory backlog emitter: agent+metric issue drafts."""

import json

from lib import curator
from test_curator import _scored


def _failed_eval(iid, agent="ooa-agent", metric="groundedness"):
    return _scored(iid, agent=agent, passed_all=False, scores={
        "citation_coverage": {"score": 1.0, "passed": True, "detail": ""},
        metric: {"score": 0.0, "passed": False, "detail": "cited source not real"},
    })


def test_groups_by_agent_and_failing_metric():
    recs = [_failed_eval("AIX-1"), _failed_eval("AIX-2"), _failed_eval("AIX-3", agent="bmca-agent")]
    items = curator.to_backlog_items(curator.select(recs, random_rate=0.0, seed=1))
    keyed = {(it["agent"], it["metric"]): it for it in items}
    assert keyed[("ooa-agent", "groundedness")]["count"] == 2
    assert set(keyed[("ooa-agent", "groundedness")]["interactionIds"]) == {"AIX-1", "AIX-2"}
    assert keyed[("bmca-agent", "groundedness")]["count"] == 1


def test_thumbs_down_maps_to_user_feedback_metric():
    rec = _scored("AIX-td", thumbs="down")
    items = curator.to_backlog_items(curator.select([rec], random_rate=0.0, seed=1))
    assert any(it["metric"] == "user_feedback" and it["agent"] == "ooa-agent" for it in items)


def test_misrefusal_maps_to_refusal_correctness_metric():
    rec = _scored("AIX-mr", refused=True, should_refuse=False)
    items = curator.to_backlog_items(curator.select([rec], random_rate=0.0, seed=1))
    assert any(it["metric"] == "refusal_correctness" for it in items)


def test_pure_random_sample_yields_no_backlog_item():
    clean = [_scored(f"AIX-c{i}") for i in range(10)]
    items = curator.to_backlog_items(curator.select(clean, random_rate=1.0, seed=1))
    assert items == []


def test_backlog_item_labels_and_advisory_marker():
    items = curator.to_backlog_items(curator.select([_failed_eval("AIX-1")], random_rate=0.0, seed=1))
    it = items[0]
    assert "advisory" in it["labels"]
    assert "agent:ooa-agent" in it["labels"]
    assert "metric:groundedness" in it["labels"]
    assert "advisory" in it["body"].lower()


def test_backlog_carries_no_raw_prompt_or_answer_text():
    items = curator.to_backlog_items(curator.select([_failed_eval("AIX-1")], random_rate=0.0, seed=1))
    blob = json.dumps(items)
    assert "secretprompt" not in blob
    assert "Ward at 92%" not in blob


def test_backlog_is_deterministically_ordered():
    recs = [_failed_eval("AIX-1", agent="bmca-agent"), _failed_eval("AIX-2", agent="ooa-agent")]
    a = curator.to_backlog_items(curator.select(recs, random_rate=0.0, seed=1))
    b = curator.to_backlog_items(curator.select(recs, random_rate=0.0, seed=1))
    assert [(i["agent"], i["metric"]) for i in a] == [(i["agent"], i["metric"]) for i in b]


def test_backlog_threshold_agrees_with_selection_threshold():
    # Evaluator passed=True but scores 0.6 -> only a "low_score" under a 0.7 threshold.
    rec = _scored("AIX-soft", scores={
        "citation_coverage": {"score": 0.6, "passed": True, "detail": ""},
    })
    selected = curator.select([rec], random_rate=0.0, seed=1, low_score_threshold=0.7)
    assert selected and "low_score" in selected[0]["reasons"]
    # The backlog must honour the same threshold, not the module default (0.5).
    items = curator.to_backlog_items(selected, low_score_threshold=0.7)
    assert any(it["metric"] == "citation_coverage" for it in items)
