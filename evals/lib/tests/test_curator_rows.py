"""M5 T2 (RED) — curator dataset-row builder: candidate vN rows with lineage."""

import copy

from lib import curator
from test_curator import _scored


def test_dataset_row_keeps_lineage_to_interaction_id():
    sel = curator.select([_scored("AIX-fail", passed_all=False)], random_rate=0.0, seed=1)
    rows = curator.to_dataset_rows(sel)
    assert len(rows) == 1
    row = rows[0]
    assert row["curation"]["sourceInteractionId"] == "AIX-fail"
    assert row["curation"]["reasons"] == ["eval_failure"]
    assert row["curation"]["signedOff"] is False
    assert row["curation"]["reviewer"] is None
    assert "curatedAt" in row["curation"]


def test_dataset_row_resets_eval_and_preserves_expected():
    rec = _scored("AIX-under", refused=False, should_refuse=True)
    rows = curator.to_dataset_rows(curator.select([rec], random_rate=0.0, seed=1))
    row = rows[0]
    assert row["eval"] == {"scored": False}
    assert row["expected"] == {"should_refuse": True}
    # still a valid interaction record shape
    assert row["contractId"] == "DC-AGENT-INTERACTION-v1"
    assert row["interactionId"] == "AIX-under"


def test_dataset_row_adds_empty_expected_when_absent():
    rec = _scored("AIX-fail", passed_all=False)   # no expected block
    rows = curator.to_dataset_rows(curator.select([rec], random_rate=0.0, seed=1))
    assert rows[0]["expected"] == {}


def test_to_dataset_rows_does_not_mutate_source_record():
    rec = _scored("AIX-fail", passed_all=False)
    before = copy.deepcopy(rec)
    sel = curator.select([rec], random_rate=0.0, seed=1)
    curator.to_dataset_rows(sel)
    assert rec == before   # original untouched (eval still scored, no curation block)
    assert "curation" not in rec
