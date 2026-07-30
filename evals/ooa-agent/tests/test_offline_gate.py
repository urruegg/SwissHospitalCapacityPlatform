"""T6 — the ooa-agent v1 golden dataset passes the offline regression gate."""

import importlib.util
from pathlib import Path

from lib import harness

REPO_ROOT = Path(__file__).resolve().parents[3]
OOA_DIR = REPO_ROOT / "evals" / "ooa-agent"
DATASET = OOA_DIR / "datasets" / "v1" / "interactions.jsonl"


def _load_runner():
    # Load by explicit path to avoid colliding with the product-owner-agent
    # module of the same name (`evals/product-owner-agent/run_evals.py`).
    spec = importlib.util.spec_from_file_location("ooa_run_evals", OOA_DIR / "run_evals.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_offline_gate_passes_on_v1_dataset():
    report = harness.run_dataset(DATASET)
    assert report["passed"] is True, report["by_evaluator"]
    assert report["n"] == 6
    assert report["by_evaluator"]["citation_coverage"]["pass_rate"] >= 0.95
    assert report["by_evaluator"]["phi_leak"]["failures"] == []
    assert report["by_evaluator"]["refusal_correctness"]["failures"] == []
    assert report["by_evaluator"]["advisory_voice"]["failures"] == []


def test_reco_row_is_actionable():
    report = harness.run_dataset(DATASET)
    assert report["by_evaluator"]["actionability"]["failures"] == []


def test_run_evals_main_returns_zero_on_pass():
    assert _load_runner().main() == 0
