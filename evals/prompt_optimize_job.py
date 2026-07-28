"""Prompt-optimization job (Sprint 30 M7).

Walking skeleton of the Improve - prompts step (design section 8 / M7). It reads
recent **scored** ``agent_interactions`` for the lead agent through the same
source seam the online-eval and curation jobs use (:mod:`lib.online_store`),
derives the failing metrics via the curator, and produces an **advisory**
prompt-optimization proposal for ``ooa-agent``: targeted instruction directives,
a candidate instruction text (in memory), and the offline-regression-gate
verdict as a promotion guardrail.

Advisory-only (NFR-LEARN-003): this job **emits a proposal**. It never writes
``AGENT.md`` or any file, opens an issue, or mutates a prompt / knowledge source /
guardrail / model. A human reviews the proposal and applies the candidate only
after the offline regression suite passes **and** an explicit
``approved-to-apply``.

PHI-safety (ADR-0016 / NFR-LEARN-001): the proposal carries only metric names,
interaction ids, directives, and the agent's own instruction text - never raw
prompt or answer content from a trace.
"""

from __future__ import annotations

import json
from pathlib import Path

from lib import online_store, prompt_optimize

AGENT = "ooa-agent"
REPO_ROOT = Path(__file__).resolve().parents[1]
INSTRUCTIONS = REPO_ROOT / "agents" / AGENT / "AGENT.md"
GATE_DATASET = REPO_ROOT / "evals" / AGENT / "datasets" / "v1" / "interactions.jsonl"
DEFAULT_LIMIT = 500


def main(argv: list[str] | None = None) -> int:
    """Entrypoint. Uses the Cosmos store when configured, else an empty store."""
    source = online_store.build_store_from_env()
    if source is None:
        source = online_store.InMemoryStore([])
    records = source.read_recent(agent=AGENT, limit=DEFAULT_LIMIT)

    proposal = prompt_optimize.run_prompt_optimization(
        agent=AGENT,
        scored_records=records,
        instructions_path=INSTRUCTIONS,
        gate_dataset_path=GATE_DATASET,
    )

    # Print an advisory digest (metrics, directives, gate verdict) - not the full
    # candidate instruction text.
    digest = {
        "agent": proposal["agent"],
        "sourceMetrics": proposal["sourceMetrics"],
        "sourceInteractionIds": proposal["sourceInteractionIds"],
        "directives": proposal["directives"],
        "offlineGatePassed": proposal["offlineGatePassed"],
        "advisory": proposal["advisory"],
        "applied": proposal["applied"],
        "approvedToApply": proposal["approvedToApply"],
        "rationale": proposal["rationale"],
    }
    print(json.dumps(digest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
