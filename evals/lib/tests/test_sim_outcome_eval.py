from lib.sim_outcome_eval import (
    outcome_divergence,
    calibration_consistency,
    run_calibration_gate,
    select_high_divergence,
)


def _outcome(divergence=0.0, freed_beds=("BED-C3-01", "BED-C3-02"), realised=None,
             provenance="simulated", golden_thread="gt-1", lever="DCA-UNBLOCK-BARRIER"):
    freed = list(freed_beds)
    realised_val = len(freed) if realised is None else realised
    return {
        "contract": "DC-SIM-OUTCOME-v1", "cosmos_id": "a0", "plan_id": "plan-ep1",
        "golden_thread": golden_thread, "lever_id": lever, "applied_ts": "1970-01-01T00:00:00Z",
        "predicted_impact": {"metric": "beds", "value": realised_val},
        "realised_impact": {"metric": "beds_freed", "value": realised_val},
        "state_delta": {"beds_freed": freed}, "divergence": divergence, "provenance": provenance,
    }


def test_outcome_divergence_passes_when_aligned():
    r = outcome_divergence(_outcome(divergence=0.0))
    assert r.passed and r.score == 1.0


def test_outcome_divergence_fails_above_threshold():
    r = outcome_divergence(_outcome(divergence=0.5, freed_beds=("BED-C3-01",)))
    assert not r.passed and r.score == 0.5


def test_calibration_consistency_detects_value_vs_freed_mismatch():
    r = calibration_consistency(_outcome(freed_beds=("BED-C3-01",), realised=2))
    assert not r.passed


def test_calibration_consistency_flags_non_simulated_provenance():
    r = calibration_consistency(_outcome(provenance="live"))
    assert not r.passed


def test_calibration_gate_passes_on_consistent_batch():
    recs = [_outcome(0.0), _outcome(0.0, freed_beds=("BED-C3-05",))]
    report = run_calibration_gate(recs)
    assert report["passed"] and report["n"] == 2 and report["mean_divergence"] == 0.0


def test_calibration_gate_fails_on_inconsistent_record():
    recs = [_outcome(freed_beds=("BED-C3-01",), realised=2)]  # value 2 but 1 freed
    report = run_calibration_gate(recs)
    assert not report["passed"] and report["calibration_failures"]


def test_calibration_gate_counts_over_threshold_without_failing():
    # High divergence is an advisory signal, not a calibration failure.
    recs = [_outcome(divergence=0.6, freed_beds=("BED-C3-01",))]
    report = run_calibration_gate(recs)
    assert report["passed"] and report["over_threshold"] == 1


def test_high_divergence_backlog_is_phi_safe_and_sorted():
    recs = [
        _outcome(divergence=0.6, freed_beds=("BED-C3-01",), golden_thread="gt-hi"),
        _outcome(divergence=0.0, golden_thread="gt-ok"),
    ]
    drafts = select_high_divergence(recs)
    assert len(drafts) == 1 and drafts[0]["golden_thread"] == "gt-hi"
    # PHI-safe: no bed ids / raw state leak into the backlog — ids + numbers only.
    assert "BED-" not in str(drafts)
