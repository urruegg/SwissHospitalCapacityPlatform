"""Sprint 41 WS-EVAL Task EVAL.1: `--live` mode for the golden-question harness.

`answer_question(question, persona, tier, live=False, ...)` is the extracted
single entry point the harness now uses for every question:

* ``live=False`` (default) preserves the EXACT current behaviour -- the
  question's yaml-declared ``chunks`` are fed straight to
  ``orchestrator.answer()`` (no network I/O).
* ``live=True`` POSTs to ``PO_AGENT_SERVICE_URL`` using the frozen
  ``POST /answer`` contract (2026-07-25 PO Agent contracts, section 6) and
  maps the response onto a shape compatible with the existing
  citation-coverage / zero-hallucination / refusal-correctness scoring in
  ``evaluate()`` (``answer``/``chunks``/``status``/``language``), while also
  exposing the raw ``citations`` list directly.
"""

from unittest.mock import patch

import pytest

import run_evals


def test_default_mode_does_not_call_the_live_service():
    """live=False (default) must never touch the network."""

    with patch("run_evals.requests.post") as post:
        result = run_evals.answer_question(
            "What is the strategic value case for the Curavias MVP?",
            persona="CEO",
            tier="internal",
            chunks=[
                {
                    "classId": "A",
                    "text": "The MVP targets patient-flow and capacity optimisation.",
                    "sourceRef": "docs/PRD.md#vision",
                    "confidence": 0.9,
                    "status": "verified",
                    "language": "en",
                }
            ],
        )
        post.assert_not_called()
    assert "[docs/PRD.md#vision]" in result["answer"]
    assert result["chunks"]


def test_live_mode_calls_the_real_service_url(monkeypatch):
    monkeypatch.setenv("PO_AGENT_SERVICE_URL", "https://po.example.test")
    with patch("run_evals.requests.post") as post:
        post.return_value.json.return_value = {
            "read": "Answer",
            "citations": ["docs/PRD.md#vision"],
            "refused": False,
        }
        result = run_evals.answer_question(
            "What is the value case?", persona="CEO", tier="internal", live=True
        )
        assert post.call_args.args[0] == "https://po.example.test/answer"
        assert result["citations"]


def test_live_mode_posts_the_frozen_answer_contract_shape(monkeypatch):
    monkeypatch.setenv("PO_AGENT_SERVICE_URL", "https://po.example.test")
    with patch("run_evals.requests.post") as post:
        post.return_value.json.return_value = {
            "read": "Advisory only. Answer [docs/PRD.md#vision]",
            "citations": ["docs/PRD.md#vision"],
            "refused": False,
        }
        run_evals.answer_question(
            "What is the value case?",
            persona="CFO",
            tier="partner",
            language="de",
            live=True,
        )
        body = post.call_args.kwargs["json"]
        assert body == {
            "question": "What is the value case?",
            "caller": {"persona": "CFO", "tier": "partner"},
            "language": "de",
        }


def test_live_mode_maps_refused_response_to_partial_status(monkeypatch):
    monkeypatch.setenv("PO_AGENT_SERVICE_URL", "https://po.example.test")
    with patch("run_evals.requests.post") as post:
        post.return_value.json.return_value = {
            "read": "Advisory only. This is a partial, transparently-degraded answer.",
            "citations": [],
            "refused": True,
        }
        result = run_evals.answer_question(
            "What is the internal three-year TCO?",
            persona="Partner",
            tier="partner",
            live=True,
        )
    assert result["status"] == "partial"
    assert result["chunks"] == []


def test_live_mode_requires_service_url(monkeypatch):
    monkeypatch.delenv("PO_AGENT_SERVICE_URL", raising=False)
    with pytest.raises(RuntimeError):
        run_evals.answer_question("Q", persona="CEO", tier="internal", live=True)


def test_main_live_flag_runs_suite_in_live_mode():
    """The `--live` CLI flag must flow through to `run_suite(..., live=True)`."""

    with patch("run_evals.run_suite") as run_suite:
        run_suite.return_value = {
            "citation_coverage": 1.0,
            "answer_count": 1,
            "refusal_count": 0,
            "hallucination_failures": [],
            "refusal_failures": [],
            "relevancy_failures": [],
            "passed": True,
        }
        run_evals.main(["--live"])
        assert run_suite.call_args.kwargs["live"] is True


def test_main_defaults_to_non_live():
    with patch("run_evals.run_suite") as run_suite:
        run_suite.return_value = {
            "citation_coverage": 1.0,
            "answer_count": 1,
            "refusal_count": 0,
            "hallucination_failures": [],
            "refusal_failures": [],
            "relevancy_failures": [],
            "passed": True,
        }
        run_evals.main([])
        assert run_suite.call_args.kwargs["live"] is False
