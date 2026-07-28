"""T5 — every ooa-agent golden-dataset row is a schema-valid
``DC-AGENT-INTERACTION-v1`` record (the ``expected`` sibling is permitted by the
contract's ``additionalProperties: true``).
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "data" / "synthetic" / "schema" / "agent-interaction-v1.schema.json"
DATASET = REPO_ROOT / "evals" / "ooa-agent" / "datasets" / "v1" / "interactions.jsonl"


def _rows() -> list[dict]:
    text = DATASET.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def test_dataset_has_six_rows():
    assert len(_rows()) == 6


@pytest.mark.parametrize("row", _rows(), ids=lambda r: r["interactionId"])
def test_row_is_schema_valid(row):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=row, schema=schema)


def test_every_row_carries_an_expected_label():
    for row in _rows():
        assert "expected" in row
        assert "should_refuse" in row["expected"]


def test_dataset_is_phi_free_of_ahv_tokens():
    import re

    ahv = re.compile(r"\b756\.\d{4}\.\d{4}\.\d{2}\b")
    for row in _rows():
        assert not ahv.search(json.dumps(row))
