"""Contract conformance test for the Sprint 28 PO Agent GroundedChunk shape.

Frozen contract owned by WS-G0 (task G0.2). Validates that every example
GroundedChunk fixture (one per knowledge class A/B/C/D) conforms to
data/synthetic/schema/grounded-chunk-v1.schema.json. Run:

    python -m pytest evals/product-owner-agent/tests/test_grounded_chunk_schema.py -v
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "data" / "synthetic" / "schema" / "grounded-chunk-v1.schema.json"
FIXTURE_DIR = REPO_ROOT / "evals" / "product-owner-agent" / "fixtures"
FIXTURES = ["grounded-chunk-a.json", "grounded-chunk-b.json", "grounded-chunk-c.json", "grounded-chunk-d.json"]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_schema_exists() -> None:
    assert SCHEMA_PATH.is_file(), f"missing frozen schema: {SCHEMA_PATH}"


@pytest.mark.parametrize("fixture_name", FIXTURES)
def test_fixture_validates_against_schema(fixture_name: str) -> None:
    import jsonschema

    schema = _load(SCHEMA_PATH)
    fixture = _load(FIXTURE_DIR / fixture_name)
    jsonschema.validate(instance=fixture, schema=schema)


def test_one_fixture_per_class() -> None:
    class_ids = sorted(_load(FIXTURE_DIR / name)["classId"] for name in FIXTURES)
    assert class_ids == ["A", "B", "C", "D"], f"expected one fixture per class, got {class_ids}"


def test_every_chunk_is_cited() -> None:
    for name in FIXTURES:
        chunk = _load(FIXTURE_DIR / name)
        assert chunk["citation"]["sourceRef"], f"{name} must carry citation.sourceRef"
