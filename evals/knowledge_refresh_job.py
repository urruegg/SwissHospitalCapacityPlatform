"""Knowledge-refresh job (Sprint 30 M8).

Walking skeleton of the Improve - knowledge step (design section 8 / M8). It reads
recent **scored** ``agent_interactions`` for the lead agent through the same
source seam the online-eval, curation, and prompt-optimize jobs use
(:mod:`lib.online_store`), derives the uncited-claim gaps via the curator, and
produces an **advisory** knowledge-refresh proposal for ``ooa-agent``: the
grounding sources to review, targeted refresh actions per knowledge metric, the
gap lineage, and the offline-regression-gate verdict as a promotion guardrail.

Advisory-only (NFR-LEARN-003): this job **emits a proposal**. It never writes a
grounding source, ontology file, ``AGENT.md``, or any file, opens an issue, or
mutates a knowledge source / model. A human reviews the proposal and refreshes the
grounding only after the offline regression suite passes **and** an explicit
``approved-to-apply``.

PHI-safety (ADR-0016 / NFR-LEARN-001): the proposal carries only metric names,
interaction ids, grounding-source names, and refresh actions - never raw prompt or
answer content from a trace.
"""

from __future__ import annotations

import json
from pathlib import Path

from lib import knowledge_refresh, online_store

AGENT = "ooa-agent"
REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_DATASET = REPO_ROOT / "evals" / AGENT / "datasets" / "v1" / "interactions.jsonl"
DEFAULT_LIMIT = 500

# The lead agent's declared grounding sources (agents/ooa-agent/AGENT.md
# section 4 "Grounding sources"). Named, PHI-free identifiers only.
OOA_GROUNDING_SOURCES = [
    "gold.encounter",
    "gold.bed_assignment",
    "gold.seasonality",
    "docs/ontology/reference-layer.ttl",
    "fabric-data-agent:DC-INSIGHT-v1",
]


def main(argv: list[str] | None = None) -> int:
    """Entrypoint. Uses the Cosmos store when configured, else an empty store."""
    source = online_store.build_store_from_env()
    if source is None:
        source = online_store.InMemoryStore([])
    records = source.read_recent(agent=AGENT, limit=DEFAULT_LIMIT)

    proposal = knowledge_refresh.run_knowledge_refresh(
        agent=AGENT,
        scored_records=records,
        grounding_sources=OOA_GROUNDING_SOURCES,
        gate_dataset_path=GATE_DATASET,
    )

    # Print an advisory digest (gap metrics, refresh actions, gate verdict).
    digest = {
        "agent": proposal["agent"],
        "knowledgeMetrics": proposal["knowledgeMetrics"],
        "sourceInteractionIds": proposal["sourceInteractionIds"],
        "groundingSources": proposal["groundingSources"],
        "refreshActions": proposal["refreshActions"],
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
