"""WS-RT Task RT.2: per-persona golden-question harness + RAI gate tests.

TDD step 1 (RED): the harness must

* **fail** a run with any uncited claim on a CFO/CISO/CLO question
  (zero-hallucination gate), and
* compute **citation coverage** (>= 95% required to pass).

Plus an end-to-end suite run over ``golden_questions.yaml`` that passes.
"""

from pathlib import Path

import run_evals

REPO_ROOT = Path(__file__).resolve().parents[3]
QUESTIONS = REPO_ROOT / "evals" / "product-owner-agent" / "golden_questions.yaml"


def _cited_run(persona="CEO", expect="answer"):
    return {
        "persona": persona,
        "expect": expect,
        "result": {
            "answer": "Advisory only. The MVP scope is X [docs/PRD.md#scope].",
            "chunks": [{"citation": {"sourceRef": "docs/PRD.md#scope"}}],
            "status": "verified",
            "confidence": 0.9,
            "language": "en",
        },
    }


def _uncited_run(persona="CFO"):
    return {
        "persona": persona,
        "expect": "answer",
        "result": {
            "answer": "Advisory only. The three-year TCO is clearly affordable.",
            "chunks": [],
            "status": "verified",
            "confidence": 0.9,
            "language": "en",
        },
    }


def test_zero_hallucination_gate_fails_on_uncited_sensitive_claim():
    report = run_evals.evaluate([_cited_run("CEO"), _uncited_run("CFO")])
    assert report["passed"] is False
    assert any(f["persona"] == "CFO" for f in report["hallucination_failures"])


def test_citation_coverage_is_computed():
    report = run_evals.evaluate([_cited_run("CEO"), _cited_run("COO")])
    assert report["citation_coverage"] == 1.0
    assert report["passed"] is True


def test_refusal_is_not_a_hallucination():
    # A transparent partial/refusal carries no substantive claim -> not a failure.
    refusal = {
        "persona": "CISO",
        "expect": "refusal",
        "result": {
            "answer": "Advisory only. This is a partial, transparently-degraded answer: "
            "insufficient high-confidence grounded sources were available.",
            "chunks": [],
            "status": "partial",
            "confidence": 0.0,
            "language": "en",
        },
    }
    report = run_evals.evaluate([refusal])
    assert report["hallucination_failures"] == []


def test_full_suite_passes():
    report = run_evals.run_suite(QUESTIONS, repo_root=REPO_ROOT)
    assert report["citation_coverage"] >= 0.95
    assert report["passed"] is True
    # Every persona class + DE/EN + Partner represented.
    personas = {r["persona"] for r in report["runs"]}
    assert {"CFO", "CISO", "CLO", "Partner"}.issubset(personas)
    langs = {r["language"] for r in report["runs"]}
    assert {"de", "en"}.issubset(langs)
