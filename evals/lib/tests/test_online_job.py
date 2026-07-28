"""M4 T3 (RED) — online-eval job: sample -> score -> write-back -> rollup."""

import json

import online_eval_job
from lib import online_store


def _rec(iid, agent, answer="Ward at 92% [gold.occupancy@s1].",
         citations=("gold.occupancy@s1",), refused=False):
    return {
        "contractId": "DC-AGENT-INTERACTION-v1",
        "interactionId": iid,
        "conversationKey": f"oid:{agent}",
        "agent": agent,
        "ts": "2026-07-27T09:00:00Z",
        "request": {"promptHash": "sha256:" + "0" * 64, "promptRedacted": "secretprompt", "lang": "de"},
        "response": {"answerRedacted": answer, "citations": list(citations), "refused": refused, "reco": None},
        "userEvents": [],
        "eval": {"scored": False},
    }


def _fixture_store():
    recs = [_rec(f"AIX-o{i}", "ooa-agent") for i in range(6)]
    recs += [_rec(f"AIX-r{i}", "ooa-agent", answer="REFUSE: out-of-scope", citations=(), refused=True) for i in range(2)]
    recs += [_rec(f"AIX-b{i}", "bmca-agent") for i in range(4)]
    return online_store.InMemoryStore(recs)


def test_run_online_eval_scores_and_writes_back():
    store = _fixture_store()
    report = online_eval_job.run_online_eval(store, store, rate=1.0, seed=1)
    assert report["totalSampled"] == 12
    # every sampled record now has eval.scored=True persisted on the store
    for rec in store.read_recent(agent=None, limit=100):
        assert rec["eval"]["scored"] is True


def test_rollup_reports_per_agent_and_per_evaluator():
    store = _fixture_store()
    report = online_eval_job.run_online_eval(store, store, rate=1.0, seed=1)
    agents = report["agents"]
    assert set(agents.keys()) == {"ooa-agent", "bmca-agent"}
    assert agents["ooa-agent"]["sampled"] == 8
    assert agents["bmca-agent"]["sampled"] == 4
    ooa = agents["ooa-agent"]["byEvaluator"]
    assert set(ooa.keys()) == {
        "citation_coverage", "groundedness", "refusal_correctness",
        "phi_leak", "actionability", "advisory_voice",
    }
    for verdict in ooa.values():
        assert 0.0 <= verdict["passRate"] <= 1.0
        assert verdict["scored"] == 8


def test_empty_source_is_safe():
    store = online_store.InMemoryStore([])
    report = online_eval_job.run_online_eval(store, store, rate=1.0, seed=1)
    assert report["totalSampled"] == 0
    assert report["agents"] == {}


def test_rollup_carries_no_raw_prompt_or_answer_text():
    store = _fixture_store()
    report = online_eval_job.run_online_eval(store, store, rate=1.0, seed=1)
    blob = json.dumps(report)
    assert "secretprompt" not in blob
    assert "Ward at 92%" not in blob


def test_main_returns_zero(monkeypatch):
    # No COSMOS_* env -> empty in-memory source -> clean exit.
    for var in ("COSMOS_ENDPOINT", "COSMOS_DATABASE", "COSMOS_CONTAINER"):
        monkeypatch.delenv(var, raising=False)
    assert online_eval_job.main([]) == 0
