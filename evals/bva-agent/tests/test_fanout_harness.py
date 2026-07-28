"""Sprint 33 C2: PO-BVA fan-out golden eval harness tests."""

from pathlib import Path

import run_fanout_evals

REPO_ROOT = Path(__file__).resolve().parents[3]
QUESTIONS = REPO_ROOT / "evals" / "bva-agent" / "fanout_questions.yaml"


def test_full_fanout_suite_passes() -> None:
    report = run_fanout_evals.run_suite(QUESTIONS, repo_root=REPO_ROOT)

    assert report["passed"] is True
    assert report["routing_accuracy"] == 1.0
    assert report["citation_coverage"] >= 0.95


def test_onboarding_answer_has_verdict_and_citations() -> None:
    report = run_fanout_evals.run_suite(QUESTIONS, repo_root=REPO_ROOT)

    onboarding = next(r for r in report["runs"] if r["intent"] == "onboarding")
    assert onboarding["result"]["verdict"] in {"go", "no-go", "conditional"}
    assert onboarding["result"]["citations"]


def test_financial_question_routes_to_financial() -> None:
    report = run_fanout_evals.run_suite(QUESTIONS, repo_root=REPO_ROOT)

    financial = next(r for r in report["runs"] if r["id"] == "financial-en-01")
    assert financial["actual_intent"] == "financial"


def test_strategic_question_routes_to_strategic() -> None:
    report = run_fanout_evals.run_suite(QUESTIONS, repo_root=REPO_ROOT)

    strategic = next(r for r in report["runs"] if r["id"] == "strategic-en-01")
    assert strategic["actual_intent"] == "strategic"
