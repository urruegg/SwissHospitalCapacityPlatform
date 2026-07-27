import subprocess
import sys
from pathlib import Path

# Test lives at scripts/ontology/tests/test_contract_existence.py.
# parents[0]=tests, [1]=ontology, [2]=scripts, [3]=repo root.
REPO = Path(__file__).resolve().parents[3]

TTL = REPO / "docs/ontology/reference-layer.ttl"
CROSSWALK = REPO / "docs/ontology/crosswalk.md"


def test_check_flags_missing_contract(tmp_path, monkeypatch):
    # Temporarily rename a real contract so the check sees it as missing.
    contract = REPO / "data/synthetic/schema/dc-match-recommendation-v1.schema.json"
    backup = contract.with_suffix(".bak")
    contract.rename(backup)
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(REPO / "scripts/ontology/check_crosswalk_conformance.py"),
                "--strict",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "DC-MATCH-RECOMMENDATION-v1" in result.stdout
    finally:
        backup.rename(contract)


# --- Sprint 26 WS-C: Decision-tier prescriptive terms (hcp:Recommendation / hcp:Lever) ---


def test_recommendation_and_lever_classes_declared():
    """Both prescriptive-tier ICE classes + the recommendsLever relation exist in the TTL."""
    ttl = TTL.read_text(encoding="utf-8")
    assert "hcp:Recommendation a owl:Class" in ttl
    assert "hcp:Lever a owl:Class" in ttl
    assert "hcp:recommendsLever a owl:ObjectProperty" in ttl


def test_discharge_recommendation_is_a_recommendation():
    """hcp:DischargeRecommendation is re-parented under hcp:Recommendation (still an ICE transitively)."""
    ttl = TTL.read_text(encoding="utf-8")
    block = ttl.split("hcp:DischargeRecommendation a owl:Class", 1)[1].split(" .", 1)[0]
    assert "rdfs:subClassOf hcp:Recommendation" in block
    assert "rdfs:subClassOf hcp:InformationContent" not in block


def test_recommendation_and_lever_have_crosswalk_rows():
    """Both classes have MVO crosswalk rows; Recommendation maps to the DC-INSIGHT-v1 contract."""
    md = CROSSWALK.read_text(encoding="utf-8")
    rec_rows = [ln for ln in md.splitlines() if ln.startswith("| `hcp:Recommendation`")]
    lever_rows = [ln for ln in md.splitlines() if ln.startswith("| `hcp:Lever`")]
    assert len(rec_rows) == 1, rec_rows
    assert len(lever_rows) == 1, lever_rows
    assert "DC-INSIGHT-v1" in rec_rows[0]
    # hcp:Lever is a git-owned config artefact — no DC-* contract binding.
    assert "DC-" not in lever_rows[0]


def test_strict_conformance_passes_with_new_terms():
    """Adding the two classes keeps the STRICT two-layer crosswalk gate green (exit 0)."""
    result = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts/ontology/check_crosswalk_conformance.py"),
            "--strict",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 WARN, 0 FAIL" in result.stdout
