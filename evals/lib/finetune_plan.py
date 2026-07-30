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


def build_finetune_plan(
    *,
    agent: str,
    scored_records: list[dict],
    gate_dataset_path,
    region: str = DEMO_REGION,
    random_rate: float = 0.0,
    seed: int = 0,
    low_score_threshold: float = curator.DEFAULT_LOW_SCORE_THRESHOLD,
) -> dict:
    """Produce an advisory fine-tune plan for ``agent``.

    Improvement signal: the curated **scored records** for ``agent`` (design M5
    seam) are selected by :func:`curator.select` and classified into SFT / DPO /
    RFT examples by :func:`classify_finetune_examples`. Guardrail: the deploy is
    **evaluation-gated** - the checkpoint is only promotable if the **offline
    regression gate** over ``gate_dataset_path`` passes (:mod:`lib.harness`);
    ``offlineGatePassed`` records the baseline verdict. ``random_rate`` defaults to
    ``0.0`` so only concrete failure/preference/grader signal - not a random
    sample - drives the plan.

    Returns an advisory plan dict. This function **never launches** a training job,
    deploys or registers a model, writes a file, or opens an issue
    (NFR-LEARN-003): a human launches training and the deploy requires the offline
    gate pass **and** an explicit ``approved-to-apply``.
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
    examples = classify_finetune_examples(selected)

    method_plans = [
        {
            "method": method,
            "feasible": bool(examples[method]),
            "exampleCount": len(examples[method]),
            "interactionIds": examples[method],
            "description": METHOD_LIBRARY[method],
        }
        for method in FINETUNE_METHODS
    ]
    feasible_methods = [m for m in FINETUNE_METHODS if examples[m]]
    source_ids = sorted({iid for ids in examples.values() for iid in ids})

    gate = harness.run_dataset(gate_dataset_path)

    rationale = (
        f"{len(source_ids)} curated interaction(s) yield {len(feasible_methods)} "
        f"feasible fine-tune method(s) ({', '.join(feasible_methods) or 'none'}) "
        f"in demo region {region}; the baseline offline gate "
        f"{'passed' if gate['passed'] else 'FAILED'}. Advisory only - a human "
        "launches training and the deploy is evaluation-gated (checkpoint must pass "
        "the offline regression suite) plus approved-to-apply. The first checkpoint "
        "is a proof of the loop, not a production model."
    )

    return {
        "agent": agent,
        "region": region,
        "methods": method_plans,
        "feasibleMethods": list(feasible_methods),
        "sourceInteractionIds": source_ids,
        "checkpointSelection": "offline-regression-gate",
        "evaluationGatedDeploy": True,
        "offlineGatePassed": gate["passed"],
        "advisory": True,
        "applied": False,
        "approvedToApply": False,
        "rationale": rationale,
    }
