"""M4 T1 (RED) — online continuous-eval sampler + scorer.

Reuses the M3 evaluator library (a metric is defined once). Deterministic +
dependency-free: sampling is seeded, scoring is the same pure evaluators used by
the offline gate.
"""

from lib import online


def _record(interaction_id, agent="ooa-agent", answer="Ward at 92% [gold.occupancy@s1].",
            citations=("gold.occupancy@s1",), refused=False):
    return {
        "contractId": "DC-AGENT-INTERACTION-v1",
        "interactionId": interaction_id,
        "conversationKey": f"oid:{agent}",
        "agent": agent,
        "ts": "2026-07-27T09:00:00Z",
        "request": {"promptHash": "sha256:" + "0" * 64, "promptRedacted": "wie ist die auslastung", "lang": "de"},
        "response": {"answerRedacted": answer, "citations": list(citations), "refused": refused, "reco": None},
        "userEvents": [],
        "eval": {"scored": False},
    }


def test_sample_is_deterministic_for_a_fixed_seed():
    records = [_record(f"AIX-{i:04x}") for i in range(100)]
    a = online.sample(records, rate=0.2, seed=42)
    b = online.sample(records, rate=0.2, seed=42)
    assert [r["interactionId"] for r in a] == [r["interactionId"] for r in b]
    # ~20% of 100, and a strict subset
    assert 15 <= len(a) <= 25
    ids = {r["interactionId"] for r in records}
    assert all(r["interactionId"] in ids for r in a)


def test_sample_rate_zero_and_one():
    records = [_record(f"AIX-{i:04x}") for i in range(10)]
    assert online.sample(records, rate=0.0, seed=1) == []
    assert len(online.sample(records, rate=1.0, seed=1)) == 10


def test_score_and_annotate_populates_eval_block():
    rec = _record("AIX-0001")
    scored = online.score_and_annotate(rec)
    ev = scored["eval"]
    assert ev["scored"] is True
    assert ev["evaluatorSet"] == "seed-v1"
    assert "sampledAt" in ev
    # all six seed evaluators present
    assert set(ev["scores"].keys()) == {
        "citation_coverage", "groundedness", "refusal_correctness",
        "phi_leak", "actionability", "advisory_voice",
    }
    for verdict in ev["scores"].values():
        assert "passed" in verdict and "score" in verdict
    assert isinstance(ev["passedAll"], bool)


def test_score_and_annotate_does_not_mutate_original():
    rec = _record("AIX-0002")
    online.score_and_annotate(rec)
    assert rec["eval"] == {"scored": False}


def test_refusal_record_scores_without_error():
    rec = _record("AIX-0003", answer="REFUSE: out-of-scope-region", citations=(), refused=True)
    scored = online.score_and_annotate(rec)
    assert scored["eval"]["scored"] is True
    assert scored["eval"]["passedAll"] is True
