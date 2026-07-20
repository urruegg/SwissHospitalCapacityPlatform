"""TDD for the deterministic eventstream synthetic seed generator.

The generator produces the envelope corpus that materialises
``Tables/bronze_eventstream_raw`` so the patient-flow lane (encounter +
bed_assignment gold tables) rebuilds reproducibly from git, with no live
Eventstream. The contract the tests below lock down:

* all 7 design-spec eventKinds are present with > 0 rows;
* every envelope carries the 8 canonical columns and a JSON-string payload;
* referential integrity: every encounterId referenced by an FK kind
  (bed.assigned / discharge.scored / discharge.recommended) exists in the
  encounter kinds (silver gate 3 aborts above a 5% orphan share);
* determinism: same seed -> byte-identical corpus;
* PHI-cleanliness: no scanned string value trips the silver gate-2 regex
  catalogue (dob / phone / email / ch_ahv_13).
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "gen_eventstream_seed.py"
spec = importlib.util.spec_from_file_location("gen_eventstream_seed", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["gen_eventstream_seed"] = mod
spec.loader.exec_module(mod)

# Mirror of 02_silver_eventstream.ipynb Gate 2 PHI catalogue.
PHI_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "phone": re.compile(r"\+?\d[\d\s().-]{6,}"),
    "dob": re.compile(r"\d{4}-\d{2}-\d{2}"),
    "ch_ahv_13": re.compile(r"756\.\d{4}\.\d{4}\.\d{2}"),
}
# Columns silver Gate 2 scans: string columns not starting with `_` and not in
# the STRUCTURAL_STRING_ALLOWLIST (which exempts eventId, simRunId, simulatedAt,
# emittedAt). So the corpus must keep PHI patterns out of these three.
SCANNED_COLS = ("eventKind", "hospitalId", "payload")

EXPECTED_KINDS = {
    "encounter.admitted",
    "encounter.transitioned",
    "bed.state_changed",
    "bed.assigned",
    "forecast.published",
    "discharge.scored",
    "discharge.recommended",
}
FK_ENCOUNTER_KINDS = {"bed.assigned", "discharge.scored", "discharge.recommended"}
CANONICAL_COLS = {
    "eventKind", "eventId", "hospitalId", "simulatedAt",
    "emittedAt", "simRunId", "seed", "payload",
}
GOLD_FLATTEN_FIELDS = {
    "encounterId", "status", "admissionType", "class",
    "requestedSpecialtyServiceId", "expectedLOSDays",
}


def _by_kind(envs):
    out = {}
    for e in envs:
        out.setdefault(e["eventKind"], []).append(e)
    return out


def test_all_seven_kinds_present_nonempty():
    envs = mod.build_envelopes(n_encounters=120, seed=42)
    by_kind = _by_kind(envs)
    assert set(by_kind) == EXPECTED_KINDS
    for kind in EXPECTED_KINDS:
        assert len(by_kind[kind]) > 0, f"{kind} produced 0 envelopes"


def test_canonical_columns_and_json_string_payload():
    envs = mod.build_envelopes(n_encounters=40, seed=7)
    for e in envs:
        assert set(e) == CANONICAL_COLS, f"unexpected columns: {set(e)}"
        assert isinstance(e["payload"], str), "payload must be a JSON string"
        assert isinstance(json.loads(e["payload"]), dict)
        assert isinstance(e["seed"], int)


def test_encounter_payloads_carry_gold_flatten_fields():
    envs = mod.build_envelopes(n_encounters=40, seed=7)
    admitted = [json.loads(e["payload"]) for e in envs
                if e["eventKind"] == "encounter.admitted"]
    assert admitted
    for p in admitted:
        assert GOLD_FLATTEN_FIELDS.issubset(p.keys()), f"missing flatten fields: {p}"


def test_fk_integrity_encounter_ids_subset():
    envs = mod.build_envelopes(n_encounters=80, seed=3)
    by_kind = _by_kind(envs)
    encounter_ids = set()
    for kind in ("encounter.admitted", "encounter.transitioned"):
        for e in by_kind.get(kind, []):
            encounter_ids.add(json.loads(e["payload"])["encounterId"])
    for kind in FK_ENCOUNTER_KINDS:
        for e in by_kind.get(kind, []):
            enc = json.loads(e["payload"])["encounterId"]
            assert enc in encounter_ids, f"{kind} references orphan encounterId {enc}"


def test_determinism_same_seed_same_corpus():
    a = mod.build_envelopes(n_encounters=60, seed=99)
    b = mod.build_envelopes(n_encounters=60, seed=99)
    assert a == b


def test_no_phi_in_scanned_columns():
    envs = mod.build_envelopes(n_encounters=120, seed=42)
    for e in envs:
        for col in SCANNED_COLS:
            value = str(e[col])
            for name, pat in PHI_PATTERNS.items():
                assert not pat.search(value), (
                    f"PHI pattern {name} matched in {col}: {value!r}")


def test_main_writes_committed_corpus(tmp_path):
    out = tmp_path / "eventstream_raw.json"
    rc = mod.main(["--out", str(out), "--n-encounters", "50", "--seed", "42"])
    assert rc == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["contractId"] == "DC-EVENTSTREAM-RAW-v1"
    assert isinstance(doc["records"], list) and doc["records"]
    assert {r["eventKind"] for r in doc["records"]} == EXPECTED_KINDS
