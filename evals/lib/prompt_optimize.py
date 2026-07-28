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

from pathlib import Path
from typing import Iterable

from lib import curator, harness

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


# Sentinel heading for the appended advisory block. Kept unique so it can be
# located and replaced (idempotent re-optimization) without touching base text.
DIRECTIVES_HEADING = "## Optimization directives (advisory, Sprint 30 M7)"
_BLOCK_MARKER = "\n" + DIRECTIVES_HEADING


def _strip_directive_block(instructions: str) -> str:
    """Return ``instructions`` with any previously appended directive block removed.

    Idempotent: text without the block is returned unchanged.
    """
    idx = instructions.find(_BLOCK_MARKER)
    return instructions if idx == -1 else instructions[:idx]


def build_candidate_instructions(base_instructions: str, directives: list[str]) -> str:
    """Return a candidate instruction text: base + an appended advisory block.

    Pure, in-memory transform - writes nothing to disk. The base content is
    preserved verbatim above a single ``## Optimization directives`` block.
    Idempotent and replacing: re-running strips any existing block first, so the
    block never stacks and re-optimizing supersedes the previous directives.
    Empty ``directives`` returns the (block-stripped) base with no empty block.
    """
    true_base = _strip_directive_block(base_instructions)
    if not directives:
        return true_base
    body = "\n".join(f"- {d}" for d in directives)
    return f"{true_base}{_BLOCK_MARKER}\n\n{body}\n"


def run_prompt_optimization(
    *,
    agent: str,
    scored_records: list[dict],
    instructions_path,
    gate_dataset_path,
    random_rate: float = 0.0,
    seed: int = 0,
    low_score_threshold: float = curator.DEFAULT_LOW_SCORE_THRESHOLD,
) -> dict:
    """Produce an advisory prompt-optimization proposal for ``agent``.

    Improvement signal: the curated **scored records** for ``agent`` (design M5
    seam) drive the failing metrics via :func:`curator.select` +
    :func:`curator.to_backlog_items`. Guardrail: the candidate is only promotable
    if the **offline regression gate** over ``gate_dataset_path`` passes
    (:mod:`lib.harness`). ``random_rate`` defaults to ``0.0`` so only concrete
    failing metrics - not a random sample - drive directives.

    Returns an advisory proposal dict. This function **never writes**
    ``AGENT.md`` or any file, opens an issue, or mutates a model (NFR-LEARN-003):
    a human applies the candidate only after the offline gate passes **and** an
    explicit ``approved-to-apply``.
    """
    scored_for_agent = [
        r
        for r in scored_records
        if r.get("agent") == agent and r.get("eval", {}).get("scored")
    ]
    selected = curator.select(
        scored_for_agent,
        random_rate=random_rate,
        seed=seed,
        low_score_threshold=low_score_threshold,
    )
    backlog = curator.to_backlog_items(selected, low_score_threshold=low_score_threshold)

    metrics = sorted({item["metric"] for item in backlog})
    source_ids = sorted({iid for item in backlog for iid in item["interactionIds"]})
    directives = propose_directives(set(metrics))

    base = Path(instructions_path).read_text(encoding="utf-8")
    candidate = build_candidate_instructions(base, directives)

    gate = harness.run_dataset(gate_dataset_path)

    rationale = (
        f"{len(source_ids)} interaction(s) across {len(metrics)} metric(s) drove "
        f"{len(directives)} advisory directive(s); offline gate "
        f"{'passed' if gate['passed'] else 'FAILED'}. Advisory only - promotion "
        "requires the offline regression pass plus approved-to-apply."
    )

    return {
        "agent": agent,
        "sourceMetrics": metrics,
        "sourceInteractionIds": source_ids,
        "directives": directives,
        "candidateInstructions": candidate,
        "offlineGatePassed": gate["passed"],
        "advisory": True,
        "applied": False,
        "approvedToApply": False,
        "rationale": rationale,
    }
