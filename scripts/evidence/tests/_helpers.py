"""Shared test helpers for the evidence parser suite.

Tests use stdlib ``unittest`` so they run dependency-free via
``python -m unittest`` and also under ``pytest`` (per the plan).
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_REPO = Path(__file__).resolve().parent / "fixtures" / "sample_repo"
SCHEMA_DIR = REPO_ROOT / "data" / "evidence" / "schema"
FIXED_COMMIT = "FIXEDCOMMIT0000000000000000000000000000"

PROVENANCE_KEYS = ("sourcePath", "sourceCommit")


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))


def assert_valid(rows: list[dict], schema_name: str) -> None:
    validate(rows, load_schema(schema_name))


def assert_provenance(rows: list[dict], keys=PROVENANCE_KEYS) -> None:
    for row in rows:
        for key in keys:
            assert row.get(key), f"missing provenance {key!r} on row {row!r}"
