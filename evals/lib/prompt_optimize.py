"""Deterministic advisory prompt optimizer for the lead agent (Sprint 30 M7).

The **Improve - prompts** stage of the closed-loop foundation (design section 8 /
milestone M7). Realises the Foundry "Agent Optimizer / prompt_optimize" concept
as a **deterministic, advisory** tool consistent with the repo's no-live-runtime
posture (ADR-0002): given a curated backlog of failing evaluator metrics for an
agent, it proposes targeted instruction directives, builds a candidate
instruction text in memory, and validates it against the offline regression gate.

Advisory-only (NFR-LEARN-003): this module emits a *proposal*. It never writes
``AGENT.md`` or any file, opens an issue, or mutates a prompt / knowledge source /
guardrail / model. A human reviews the proposal and applies it only after the
offline regression suite passes **and** an explicit ``approved-to-apply``.

PHI-safety (ADR-0016 / NFR-LEARN-001): the optimizer reads only metric names,
interaction ids, and the agent's own instruction text - never raw prompt or
answer content from a trace.
"""

from __future__ import annotations

from typing import Iterable

# Metric -> targeted advisory instruction directive. Insertion order is the
# canonical directive order (Python dicts preserve insertion order), matching the
# harness EVALUATORS report order, then the curator synthetic metrics.
DIRECTIVE_LIBRARY: dict[str, str] = {
    "citation_coverage": (
        "Always include at least one `Grounded on:` citation line naming the "
        "gold snapshot(s) used (e.g. `Grounded on: gold.encounter@<snapshot>, "
        "gold.bed_assignment@<snapshot>`)."
    ),
    "groundedness": (
        "State no figure, forecast, or classification that is not present in or "
        "directly derived from the grounded rows; never fill gaps from memory."
    ),
    "refusal_correctness": (
        "Apply the section 5 refusal triggers exactly: refuse out-of-scope-region, "
        "phi-in-output, direct-mutation, fabricated-impact, and self-approval "
        "requests rather than answering them."
    ),
    "phi_leak": (
        "Never emit a patient name, MRN, DOB, or clinical note; emit only "
        "ward/aggregate figures and reference-layer concepts."
    ),
    "actionability": (
        "For a breach query, always emit a ranked recommendation with a concrete "
        "`lever_id`, `params`, and the deterministic `compute_expected_impact` "
        "value - never a guessed impact and never an empty recommendation."
    ),
    "advisory_voice": (
        "Always label the reply **advisory** and name the HITL-05 downstream gate; "
        "never phrase a forecast as an instruction to act."
    ),
    "user_feedback": (
        "Review thumbs-down interactions for tone and clarity: lead with the "
        "pressure classification, keep the forecast block scannable, and state the "
        "advisory framing up front."
    ),
}

# Fallback directive for a metric with no library entry (e.g. a new evaluator
# added before its directive). A single generic directive is emitted regardless
# of how many unknown metrics are present.
GENERIC_DIRECTIVE = (
    "Review the flagged interactions for this metric and add a targeted "
    "instruction directive; no library directive exists yet."
)


def propose_directives(metrics: Iterable[str]) -> list[str]:
    """Return advisory directives for the failing ``metrics``.

    Deterministically ordered by the canonical :data:`DIRECTIVE_LIBRARY` order;
    any metric without a library entry collapses to a single
    :data:`GENERIC_DIRECTIVE` appended at the end. Order-stable regardless of the
    input iteration order.
    """
    metric_set = set(metrics)
    directives: list[str] = [
        directive
        for metric, directive in DIRECTIVE_LIBRARY.items()
        if metric in metric_set
    ]
    if any(m not in DIRECTIVE_LIBRARY for m in metric_set):
        directives.append(GENERIC_DIRECTIVE)
    return directives
