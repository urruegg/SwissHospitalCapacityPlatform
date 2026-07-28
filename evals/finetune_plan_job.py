"""Fine-tune planning job (Sprint 30 M9).

Walking skeleton of the Improve - fine-tune step (design section 8 / M9). It reads
recent **scored** ``agent_interactions`` for the lead agent through the same source
seam the online-eval, curation, prompt-optimize, and knowledge-refresh jobs use
(:mod:`lib.online_store`), classifies the curated signal into SFT / DPO / RFT
examples, and produces an **advisory** fine-tune plan for ``ooa-agent``: per-method
feasibility + example counts + lineage, the demo region, and the offline-
regression-gate baseline as the evaluation-gated-deploy / checkpoint-selection
guardrail.

Advisory-only (NFR-LEARN-003): this job **emits a plan**. It never launches a
training job, deploys or registers a model, writes a file, or opens an issue. A
human launches training and the deploy is evaluation-gated (the checkpoint must
pass the offline regression suite) **and** requires an explicit ``approved-to-apply``.

PHI-safety (ADR-0016 / NFR-LEARN-001): the plan carries only method names,
interaction ids, counts, and the demo region - never raw prompt or answer content
from a trace. Fine-tune runs in the demo region eastus2 (ADR-0013 / ADR-0032);
Swiss-region GA fine-tune follows the Preview-exception path (ADR-0006 / ADR-0042).
"""

from __future__ import annotations

import json
from pathlib import Path

from lib import finetune_plan, online_store

AGENT = "ooa-agent"
REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_DATASET = REPO_ROOT / "evals" / AGENT / "datasets" / "v1" / "interactions.jsonl"
DEFAULT_LIMIT = 500


def main(argv: list[str] | None = None) -> int:
    """Entrypoint. Uses the Cosmos store when configured, else an empty store."""
    source = online_store.build_store_from_env()
    if source is None:
        source = online_store.InMemoryStore([])
    records = source.read_recent(agent=AGENT, limit=DEFAULT_LIMIT)

    plan = finetune_plan.build_finetune_plan(
        agent=AGENT,
        scored_records=records,
        gate_dataset_path=GATE_DATASET,
    )

    # Print an advisory digest (per-method counts + gate verdict), not raw content.
    digest = {
        "agent": plan["agent"],
        "region": plan["region"],
        "feasibleMethods": plan["feasibleMethods"],
        "methods": [
            {
                "method": m["method"],
                "feasible": m["feasible"],
                "exampleCount": m["exampleCount"],
            }
            for m in plan["methods"]
        ],
        "sourceInteractionIds": plan["sourceInteractionIds"],
        "checkpointSelection": plan["checkpointSelection"],
        "evaluationGatedDeploy": plan["evaluationGatedDeploy"],
        "offlineGatePassed": plan["offlineGatePassed"],
        "advisory": plan["advisory"],
        "applied": plan["applied"],
        "approvedToApply": plan["approvedToApply"],
        "rationale": plan["rationale"],
    }
    print(json.dumps(digest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
