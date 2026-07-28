"""Deterministic advisory fine-tune plan builder for the lead agent (Sprint 30 M9).

The **Improve - fine-tune** stage of the closed-loop foundation (design section 8 /
milestone M9). Realises "SFT / DPO (thumbs pairs) / RFT (graders) on the curated
dataset (demo-scope eastus2); checkpoint selection; evaluation-gated deploy" as a
**deterministic, advisory** tool consistent with the repo's no-live-runtime posture
(ADR-0002; Foundry fine-tune is not GA-in-Switzerland, design section 13): given a
curated set of scored interactions for an agent, it classifies the fine-tune
signal into the three methods, counts the per-method examples with lineage, and
records the evaluation-gated-deploy guardrail.

The three methods map to the curated selection signal (curator, M5 seam):

- **SFT** (supervised) - quality-failure examples (eval_failure / low_score /
  misrefusal) that carry a corrected target to imitate.
- **DPO** (preference) - **thumbs pairs**: thumbs-down interactions become
  preference pairs.
- **RFT** (reinforcement) - **graders**: examples the evaluator library can grade
  (records carrying eval scores).

Advisory-only (NFR-LEARN-003): this module emits a *plan*. It never launches a
training job, deploys or registers a model, writes a file, or opens an issue. A
human launches training and the deploy is **evaluation-gated** (the checkpoint must
pass the offline regression suite) **and** requires an explicit ``approved-to-apply``.

PHI-safety (ADR-0016 / NFR-LEARN-001): the plan carries only method names, metric-
derived selection signal, interaction ids, counts, and the demo region - never raw
prompt or answer content from a trace. Fine-tune runs in the demo region
**eastus2** (ADR-0013 region-pin, ADR-0032 Foundry/OpenAI quota); Swiss-region GA
fine-tune follows the Preview-exception path (ADR-0006 / ADR-0042).
"""

from __future__ import annotations

from typing import Any, Iterable

from lib import curator, harness

# Demo region for fine-tune (design section 10 / 13; ADR-0013 + ADR-0032).
DEMO_REGION = "eastus2"

# Canonical method order: supervised, then preference, then reinforcement.
FINETUNE_METHODS: tuple[str, ...] = ("sft", "dpo", "rft")

# Method -> description of the curated data signal it consumes.
METHOD_LIBRARY: dict[str, str] = {
    "sft": (
        "Supervised fine-tuning on quality-failure examples (evaluation failures, "
        "low scores, mis-refusals) that carry a human-corrected target answer to "
        "imitate."
    ),
    "dpo": (
        "Direct preference optimization on thumbs pairs: a thumbs-down interaction "
        "paired with the preferred (corrected) response as the preference signal."
    ),
    "rft": (
        "Reinforcement fine-tuning graded by the evaluator library: the deterministic "
        "evaluators (citation_coverage, groundedness, refusal_correctness, phi_leak, "
        "actionability, advisory_voice) act as reward graders over scored examples."
    ),
}


def propose_methods(methods: Iterable[str]) -> list[str]:
    """Return method descriptions for the feasible ``methods``.

    Deterministically ordered by :data:`FINETUNE_METHODS`. Any name without a
    library entry is ignored, so the output is always a subset of the canonical
    method descriptions in canonical order.
    """
    method_set = set(methods)
    return [
        METHOD_LIBRARY[method]
        for method in FINETUNE_METHODS
        if method in method_set
    ]


# Selection reasons that yield a supervised (SFT) example: a quality failure with
# a human-correctable target answer.
_SFT_REASONS = frozenset({curator.EVAL_FAILURE, curator.LOW_SCORE, curator.MISREFUSAL})


def classify_finetune_examples(selected: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Assign curator selections to the fine-tune method(s) their signal supports.

    ``selected`` is the :func:`curator.select` output (``{"record", "reasons"}``).
    Returns ``{"sft": [...], "dpo": [...], "rft": [...]}`` with per-method
    interaction ids sorted and de-duplicated. A single interaction may feed more
    than one method. Pure and PHI-safe (ids only):

    - **sft** - a quality-failure reason (eval_failure / low_score / misrefusal).
    - **dpo** - a thumbs-down reason (a preference pair).
    - **rft** - the record carries eval scores (gradeable by the evaluator library).

    A pure random sample with no failure signal and no scores feeds no method.
    """
    buckets: dict[str, set[str]] = {method: set() for method in FINETUNE_METHODS}
    for sel in selected:
        record = sel["record"]
        iid = record.get("interactionId")
        reasons = set(sel.get("reasons", []))
        if reasons & _SFT_REASONS:
            buckets["sft"].add(iid)
        if curator.THUMBS_DOWN in reasons:
            buckets["dpo"].add(iid)
        if record.get("eval", {}).get("scores"):
            buckets["rft"].add(iid)
    return {method: sorted(ids) for method, ids in buckets.items()}
