"""M5 T1 (RED) — curator selection policy: pick high-signal scored traces."""

from lib import curator


def _scored(iid, agent="ooa-agent", *, passed_all=True, scores=None,
            thumbs=None, refused=False, should_refuse=None,
            answer="Ward at 92% [gold.occupancy@s1].", citations=("gold.occupancy@s1",)):
    rec = {
        "contractId": "DC-AGENT-INTERACTION-v1",
        "interactionId": iid,
        "agent": agent,
        "ts": "2026-07-27T09:00:00Z",
        "request": {"promptHash": "sha256:" + "0" * 64, "promptRedacted": "secretprompt", "lang": "en"},
        "response": {"answerRedacted": answer, "citations": list(citations), "refused": refused, "reco": None},
        "userEvents": [],
        "eval": {
            "scored": True,
            "evaluatorSet": "seed-v1",
            "scores": scores or {
                "citation_coverage": {"score": 1.0, "passed": True, "detail": ""},
                "groundedness": {"score": 1.0, "passed": True, "detail": ""},
            },
            "passedAll": passed_all,
        },
    }
    if thumbs is not None:
        rec["userEvents"] = [{"type": "thumbs", "value": thumbs, "ts": "2026-07-27T09:05:00Z"}]
    if should_refuse is not None:
        rec["expected"] = {"should_refuse": should_refuse}
    return rec


def test_selects_eval_failures():
    recs = [_scored("AIX-ok"), _scored("AIX-fail", passed_all=False)]
    selected = curator.select(recs, random_rate=0.0, seed=1)
    ids = {s["record"]["interactionId"]: s["reasons"] for s in selected}
    assert "AIX-fail" in ids
    assert "eval_failure" in ids["AIX-fail"]
    assert "AIX-ok" not in ids


def test_selects_low_scores_below_threshold():
    low = _scored("AIX-low", scores={
        "citation_coverage": {"score": 0.4, "passed": True, "detail": ""},
    })
    selected = curator.select([low], random_rate=0.0, seed=1, low_score_threshold=0.5)
    assert selected and "low_score" in selected[0]["reasons"]


def test_selects_thumbs_down():
    recs = [_scored("AIX-up", thumbs="up"), _scored("AIX-down", thumbs="down")]
    selected = {s["record"]["interactionId"]: s["reasons"]
                for s in curator.select(recs, random_rate=0.0, seed=1)}
    assert "AIX-down" in selected and "thumbs_down" in selected["AIX-down"]
    assert "AIX-up" not in selected


def test_selects_misrefusals_both_directions():
    over = _scored("AIX-over", refused=True, should_refuse=False)   # refused when it should not
    under = _scored("AIX-under", refused=False, should_refuse=True)  # answered when it should refuse
    ok = _scored("AIX-ok", refused=True, should_refuse=True)
    selected = {s["record"]["interactionId"]: s["reasons"]
                for s in curator.select([over, under, ok], random_rate=0.0, seed=1)}
    assert "misrefusal" in selected["AIX-over"]
    assert "misrefusal" in selected["AIX-under"]
    assert "AIX-ok" not in selected


def test_random_sample_is_deterministic_and_excludes_high_signal():
    clean = [_scored(f"AIX-c{i}") for i in range(20)]
    a = {s["record"]["interactionId"] for s in curator.select(clean, random_rate=0.5, seed=7)}
    b = {s["record"]["interactionId"] for s in curator.select(clean, random_rate=0.5, seed=7)}
    assert a == b               # deterministic for a fixed seed
    assert 0 < len(a) < 20      # a proper subset
    for s in curator.select(clean, random_rate=0.5, seed=7):
        assert s["reasons"] == ["random_sample"]


def test_random_sample_does_not_double_count_high_signal():
    fail = _scored("AIX-fail", passed_all=False)
    selected = curator.select([fail], random_rate=1.0, seed=1)
    assert len(selected) == 1
    assert selected[0]["reasons"] == ["eval_failure"]  # not also random_sample
