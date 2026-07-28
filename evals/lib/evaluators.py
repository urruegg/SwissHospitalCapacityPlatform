"""Shared, agent-agnostic evaluator library (Sprint 30 M3).

Defined once, reused by the offline batch regression gate (this milestone) and
the future online continuous-eval sampler (M4) — design §7. Every evaluator is a
pure function over a ``DC-AGENT-INTERACTION-v1`` record (``dict``) plus an
optional ``expected`` label block from the golden dataset, returning a structured
:class:`EvalResult`. All seed evaluators are **deterministic** (no LLM, no
network) so the gate runs in CI without model access; LLM-as-judge groundedness /
voice is a later hardening pass.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class EvalResult:
    """One evaluator's verdict on one interaction record."""

    evaluator: str
    score: float
    passed: bool
    detail: str = ""


Record = dict[str, Any]
Expected = Optional[dict[str, Any]]


# --- shared helpers ---------------------------------------------------------

# Boilerplate the runtime prepends/appends; stripped before deciding whether an
# answer still makes an *uncited* substantive claim (ported from the PO-agent
# harness, `evals/product-owner-agent/run_evals.py`).
_BOILERPLATE = (
    "Advisory only.",
    "Nur zur Beratung.",
    "This is a partial, transparently-degraded answer: insufficient "
    "high-confidence grounded sources were available.",
    "Dies ist eine teilweise, transparent abgestufte Antwort: es lagen "
    "nicht genug hoch-vertrauenswuerdige belegte Quellen vor.",
)


def _answer(record: Record) -> str:
    return (record.get("response") or {}).get("answerRedacted", "") or ""


def _is_refused(record: Record) -> bool:
    return bool((record.get("response") or {}).get("refused", False))


def _strip_boilerplate(answer: str) -> str:
    out = answer
    for phrase in _BOILERPLATE:
        out = out.replace(phrase, "")
    return out.strip()


def _passfail(evaluator: str, ok: bool, detail: str = "") -> EvalResult:
    return EvalResult(evaluator=evaluator, score=1.0 if ok else 0.0, passed=ok, detail=detail)


# --- citation coverage ------------------------------------------------------

def citation_coverage(record: Record, expected: Expected = None) -> EvalResult:
    """Every substantive answer carries a citation (inline ``[...]`` or a
    non-empty ``response.citations`` array). Refusals / pure partials carry no
    claim and pass vacuously.
    """
    name = "citation_coverage"
    if _is_refused(record):
        return _passfail(name, True, "refusal — no substantive claim")

    residual = _strip_boilerplate(_answer(record))
    if not residual:
        return _passfail(name, True, "no substantive claim")

    citations = (record.get("response") or {}).get("citations") or []
    if citations or "[" in residual:
        return _passfail(name, True, "claim is cited")
    return _passfail(name, False, "substantive claim without a citation")
