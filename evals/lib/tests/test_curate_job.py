"""M5 T3 (RED) — online curation job: read scored -> curate -> advisory summary."""

import json

import curate_job
from lib import online_store
from test_curator import _scored


def _fixture_store():
    recs = [
        _scored("AIX-ok1"),
        _scored("AIX-ok2"),
        _scored("AIX-fail", passed_all=False, scores={
            "groundedness": {"score": 0.0, "passed": False, "detail": "bad"},
        }),
        _scored("AIX-td", thumbs="down"),
        _scored("AIX-unscored"),
    ]
    recs[-1]["eval"] = {"scored": False}   # not yet scored -> must be ignored
    return online_store.InMemoryStore(recs)


def test_run_curation_considers_only_scored_records():
    store = _fixture_store()
    summary = curate_job.run_curation(store, rate=0.0, seed=1)
    assert summary["considered"] == 4   # the unscored record is excluded


def test_run_curation_emits_dataset_rows_with_lineage_and_backlog():
    store = _fixture_store()
    summary = curate_job.run_curation(store, rate=0.0, seed=1)
    ids = {r["curation"]["sourceInteractionId"] for r in summary["datasetRows"]}
    assert "AIX-fail" in ids and "AIX-td" in ids
    metrics = {it["metric"] for it in summary["backlog"]}
    assert "groundedness" in metrics and "user_feedback" in metrics


def test_run_curation_is_empty_safe():
    summary = curate_job.run_curation(online_store.InMemoryStore([]), rate=0.5, seed=1)
    assert summary["selected"] == 0
    assert summary["datasetRows"] == []
    assert summary["backlog"] == []


def test_summary_backlog_has_no_raw_text():
    store = _fixture_store()
    summary = curate_job.run_curation(store, rate=0.0, seed=1)
    assert "secretprompt" not in json.dumps(summary["backlog"])


def test_main_returns_zero(monkeypatch):
    for var in ("COSMOS_ENDPOINT", "COSMOS_DATABASE", "COSMOS_CONTAINER"):
        monkeypatch.delenv(var, raising=False)
    assert curate_job.main([]) == 0
