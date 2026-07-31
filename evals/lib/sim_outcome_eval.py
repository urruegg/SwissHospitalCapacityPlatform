"""Sim-outcome evaluation + calibration gate (Sprint 38 M5).

Closes the LEARNING loop on top of the operational loop: scores DC-SIM-OUTCOME-v1
records (predicted-vs-realised divergence), asserts the simulator is internally
consistent (calibration gate), and drafts an advisory backlog of high-divergence
journeys as an agent-optimisation signal. Reuses the Sprint 30 EvalResult and the
curator's advisory-only + PHI-safe posture: this module emits drafts and reports;
it never mutates a prompt / model / dataset. All checks are deterministic (no LLM,
no network) so they run in CI. Realises FR-CLP-003.
"""
from __future__ import annotations

from typing import Any, Optional

from lib.evaluators import EvalResult

Record = dict[str, Any]

# An outcome whose predicted and realised impact diverge by more than this is a
# high-signal calibration/optimisation lead (normalised gap, 0..1).
DEFAULT_DIVERGENCE_THRESHOLD = 0.2


def outcome_divergence(record: Record, expected: Optional[dict] = None) -> EvalResult:
    """Score one DC-SIM-OUTCOME-v1 record: passed iff divergence <= threshold.

    ``expected.divergence_threshold`` overrides the default. Score is
    ``1 - divergence`` clamped to [0, 1] — the agent's predicted impact matching
    the simulator's realised impact is the signal."""
    name = "outcome_divergence"
    threshold = float((expected or {}).get("divergence_threshold", DEFAULT_DIVERGENCE_THRESHOLD))
    divergence = float(record.get("divergence", 0.0))
    score = max(0.0, min(1.0, 1.0 - divergence))
    passed = divergence <= threshold
    return EvalResult(
        evaluator=name, score=round(score, 4), passed=passed,
        detail=f"divergence={divergence:.4f} threshold={threshold:.4f}",
    )


def calibration_consistency(record: Record) -> EvalResult:
    """Assert one DC-SIM-OUTCOME-v1 record is internally consistent (the
    'simulator is working' check): realised value equals the freed-bed count,
    divergence is non-negative, and provenance is 'simulated'."""
    name = "calibration_consistency"
    if record.get("provenance") != "simulated":
        return EvalResult(name, 0.0, False, f"provenance={record.get('provenance')!r} (expected 'simulated')")
    if float(record.get("divergence", 0.0)) < 0:
        return EvalResult(name, 0.0, False, "negative divergence")
    realised = int((record.get("realised_impact") or {}).get("value", 0))
    freed = (record.get("state_delta") or {}).get("beds_freed") or []
    if realised != len(freed):
        return EvalResult(name, 0.0, False, f"realised value {realised} != freed-bed count {len(freed)}")
    return EvalResult(name, 1.0, True, "internally consistent")


def run_calibration_gate(records: list[Record], *, threshold: float = DEFAULT_DIVERGENCE_THRESHOLD) -> dict[str, Any]:
    """Batch calibration gate over DC-SIM-OUTCOME-v1 records.

    Hard gate: every record must pass ``calibration_consistency`` (the simulator
    must be internally consistent). Also rolls up the divergence distribution as
    the agent-optimisation signal. ``passed`` is the gate (calibration only —
    high divergence is an advisory signal, not a hard failure)."""
    n = len(records)
    calibration_failures: list[dict[str, Any]] = []
    divergences: list[float] = []
    over = 0
    for idx, rec in enumerate(records):
        verdict = calibration_consistency(rec)
        if not verdict.passed:
            calibration_failures.append(
                {"index": idx, "golden_thread": rec.get("golden_thread"), "detail": verdict.detail}
            )
        d = float(rec.get("divergence", 0.0))
        divergences.append(d)
        if d > threshold:
            over += 1
    return {
        "n": n,
        "calibration_failures": calibration_failures,
        "mean_divergence": round(sum(divergences) / n, 4) if n else 0.0,
        "max_divergence": round(max(divergences), 4) if divergences else 0.0,
        "over_threshold": over,
        "threshold": threshold,
        "passed": not calibration_failures,
    }


def select_high_divergence(records: list[Record], *, threshold: float = DEFAULT_DIVERGENCE_THRESHOLD) -> list[dict[str, Any]]:
    """Advisory backlog: draft one item per high-divergence outcome as an
    agent-optimisation lead. PHI-safe (ids / levers / numbers only — never raw
    bed/patient content) and advisory-only (drafts, never applied), mirroring the
    Sprint 30 curator posture (NFR-LEARN-003 / ADR-0016)."""
    drafts: list[dict[str, Any]] = []
    for rec in records:
        d = float(rec.get("divergence", 0.0))
        if d > threshold:
            drafts.append({
                "kind": "outcome_divergence_lead",
                "golden_thread": rec.get("golden_thread"),
                "plan_id": rec.get("plan_id"),
                "lever_id": rec.get("lever_id"),
                "divergence": round(d, 4),
                "predicted": (rec.get("predicted_impact") or {}).get("value"),
                "realised": (rec.get("realised_impact") or {}).get("value"),
                "advisory": "review lever calibration; human-gated, no auto-apply",
            })
    drafts.sort(key=lambda x: (-x["divergence"], str(x.get("golden_thread"))))
    return drafts
