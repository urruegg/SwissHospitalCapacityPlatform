"""Output-contract conformance tests for the BVA simulation engine."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from bva.models import BvaBaseline, HospitalDelta
from bva.simulate import simulate

_AS_OF = "2026-07-28T00:00:00Z"


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "data" / "synthetic" / "schema").is_dir():
            return parent
    raise AssertionError("could not locate repository root")


def _simulation_schema() -> dict:
    schema_path = _repo_root() / "data" / "synthetic" / "schema" / "bva-simulation-result-v1.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _canonical_acute_what_if() -> dict:
    return simulate(
        BvaBaseline.rom_default(),
        HospitalDelta(
            hospital_name="Hopital de Fribourg",
            archetype="acute",
            beds=320,
            occupancy_target=0.85,
            onboarding_scope="full",
        ),
        language="en",
        as_of=_AS_OF,
    )


def test_canonical_acute_what_if_conforms_to_frozen_simulation_schema() -> None:
    result = _canonical_acute_what_if()

    jsonschema.validate(instance=result, schema=_simulation_schema())

    assert result["currency"] == "CHF"
    assert len(result["chunks"]) >= 1
    for chunk in result["chunks"]:
        assert chunk["classId"] == "C"
        assert chunk["citation"]["sourceRef"]
