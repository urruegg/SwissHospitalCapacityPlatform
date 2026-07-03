import subprocess
import sys
from pathlib import Path

# Test lives at scripts/ontology/tests/test_contract_existence.py.
# parents[0]=tests, [1]=ontology, [2]=scripts, [3]=repo root.
REPO = Path(__file__).resolve().parents[3]


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
