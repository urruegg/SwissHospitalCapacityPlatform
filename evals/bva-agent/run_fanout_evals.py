"""Sprint 33 C2: PO-BVA fan-out golden eval harness.

Runs the pure fan-out router/composer over ``fanout_questions.yaml`` and
scores:

* routing correctness - every question must classify to the expected intent.
* verdict-present gate - composed onboarding answers must include a valid
  go/no-go/conditional verdict.
* citation coverage - composed onboarding answers must not contain uncited
  substantive claims. Pass gate: >= 0.95.

Usage::

    python evals/bva-agent/run_fanout_evals.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = REPO_ROOT / "data-platform" / "scripts" / "po-agent" / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import bva_fanout  # noqa: E402  (path set above)
from authz import CallerContext  # noqa: E402

CITATION_COVERAGE_GATE = 0.95
VALID_VERDICTS = {"go", "no-go", "conditional"}

_BOILERPLATE = (
    "Advisory only.",
    "Nur zur Beratung.",
    "This is a partial, transparently-degraded answer: insufficient "
    "high-confidence grounded sources were available.",
    "Dies ist eine teilweise, transparent abgestufte Antwort: es lagen "
    "nicht genug hoch-vertrauenswuerdige belegte Quellen vor.",
)
_SOURCE_LANG_PATTERNS = (
    r"Some sources are in .*? answered in \w+\.",
    r"Einige Quellen sind in .*? beantwortet auf \w+\.",
)


def _strip_boilerplate(answer: str) -> str:
    out = answer
    for phrase in _BOILERPLATE:
        out = out.replace(phrase, "")
    for pattern in _SOURCE_LANG_PATTERNS:
        out = re.sub(pattern, "", out)
    return out.strip()


def _substantive_sentences(answer: str) -> list[str]:
    residual = _strip_boilerplate(answer)
    if not residual:
        return []
    return [s.strip() for s in re.split(r"(?<=\.)\s+", residual) if s.strip()]


def has_uncited_claim(answer: str) -> bool:
    """True if any substantive sentence lacks a [citation] marker."""

    return any("[" not in sentence or "]" not in sentence for sentence in _substantive_sentences(answer))


def load_questions(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return data.get("questions", [])


def _load_bva_result(entry: dict[str, Any], questions_path: Path) -> dict[str, Any]:
    if "bva_result" in entry:
        return dict(entry["bva_result"])
    fixture = entry.get("bva_result_fixture")
    if not fixture:
        return {}
    return json.loads((questions_path.parent / fixture).read_text(encoding="utf-8"))


def _caller_for(entry: dict[str, Any]) -> CallerContext:
    return CallerContext(
        identity=entry.get("caller_identity", "fanout-eval@curavias"),
        tier=entry.get("tier", "internal"),
        language=entry.get("language", "en"),
    )


def evaluate(runs: list[dict[str, Any]]) -> dict[str, Any]:
    routed = [r for r in runs if r["actual_intent"] == r["intent"]]
    routing_accuracy = (len(routed) / len(runs)) if runs else 1.0

    answer_runs = [r for r in runs if r.get("expect") == "answer"]
    cited = 0
    verdict_failures = []
    for run in answer_runs:
        result = run.get("result", {})
        verdict = result.get("verdict")
        if verdict not in VALID_VERDICTS:
            verdict_failures.append({"id": run["id"], "verdict": verdict})
        if not has_uncited_claim(result.get("answer", "")):
            cited += 1

    citation_coverage = (cited / len(answer_runs)) if answer_runs else 1.0
    passed = (
        routing_accuracy == 1.0
        and citation_coverage >= CITATION_COVERAGE_GATE
        and not verdict_failures
    )
    return {
        "routing_accuracy": round(routing_accuracy, 4),
        "citation_coverage": round(citation_coverage, 4),
        "verdict_failures": verdict_failures,
        "answer_count": len(answer_runs),
        "runs": runs,
        "passed": passed,
    }


def run_suite(
    questions_path: Path = REPO_ROOT / "evals" / "bva-agent" / "fanout_questions.yaml",
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Run every fan-out golden question through the router/composer."""

    del repo_root
    runs = []
    for entry in load_questions(questions_path):
        actual_intent = bva_fanout.classify_intent(entry["question"])
        result = None
        if entry.get("expect") == "answer":
            result = bva_fanout.compose_onboarding_answer(
                entry["question"],
                _load_bva_result(entry, questions_path),
                entry.get("po_verdict"),
                _caller_for(entry),
            )
        runs.append(
            {
                "id": entry["id"],
                "question": entry["question"],
                "intent": entry["intent"],
                "actual_intent": actual_intent,
                "language": entry.get("language", "en"),
                "expect": entry.get("expect", "route-only"),
                "result": result,
            }
        )
    return evaluate(runs)


def main() -> int:
    report = run_suite()
    print(f"routing accuracy  : {report['routing_accuracy']:.2%}")
    print(f"citation coverage : {report['citation_coverage']:.2%}")
    print(f"answers           : {report['answer_count']}")
    print(f"verdict failures  : {len(report['verdict_failures'])}")
    print(f"PASSED            : {report['passed']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
