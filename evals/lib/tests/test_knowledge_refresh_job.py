"""T3 - run_knowledge_refresh + job (Sprint 30 M8).

End-to-end deterministic knowledge-refresh: curated scored records drive the
uncited-claim gaps (knowledge metrics only); the golden dataset validates the
current grounding through the offline gate. The proposal is advisory and must
never mutate a grounding source or AGENT.md.
"""

import importlib.util
from pathlib import Path

from lib import knowledge_refresh as kr

REPO_ROOT = Path(__file__).resolve().parents[3]
OOA_DIR = REPO_ROOT / "evals" / "ooa-agent"
GATE_DATASET = OOA_DIR / "datasets" / "v1" / "interactions.jsonl"
INSTRUCTIONS = REPO_ROOT / "agents" / "ooa-agent" / "AGENT.md"

GROUNDING = ["gold.encounter", "gold.bed_assignment", "reference-layer.ttl"]


def _scored_records():
    return [
        {
            "interactionId": "ix-cite-1",
            "agent": "ooa-agent",
            "eval": {
                "scored": True,
                "passedAll": False,
                "scores": {"citation_coverage": {"passed": False, "score": 0.0}},
            },
        },
        {
            "interactionId": "ix-act-1",  # prompt-lane failure -> excluded from knowledge gaps
            "agent": "ooa-agent",
            "eval": {
                "scored": True,
                "passedAll": False,
                "scores": {"actionability": {"passed": True, "score": 0.2}},
            },
        },
        {
            "interactionId": "ix-ground-1",
            "agent": "ooa-agent",
            "eval": {
                "scored": True,
                "passedAll": False,
                "scores": {"groundedness": {"passed": False, "score": 0.1}},
            },
        },
        {
            "interactionId": "ix-other-agent",  # different agent -> excluded by scoping
            "agent": "bmca-agent",
            "eval": {
                "scored": True,
                "passedAll": False,
                "scores": {"citation_coverage": {"passed": False, "score": 0.0}},
            },
        },
    ]


def _run():
    return kr.run_knowledge_refresh(
        agent="ooa-agent",
        scored_records=_scored_records(),
        grounding_sources=GROUNDING,
        gate_dataset_path=GATE_DATASET,
    )


def test_knowledge_metrics_are_only_the_grounding_gaps():
    proposal = _run()
    # actionability (prompt-lane) and bmca's citation_coverage (scoping) excluded.
    assert proposal["knowledgeMetrics"] == ["citation_coverage", "groundedness"]


def test_refresh_actions_match_the_knowledge_metrics():
    proposal = _run()
    assert proposal["refreshActions"] == kr.propose_refresh_actions(
        set(proposal["knowledgeMetrics"])
    )
    assert proposal["refreshActions"]


def test_gaps_carry_grounding_sources_and_lineage():
    proposal = _run()
    metrics = [g["metric"] for g in proposal["gaps"]]
    assert metrics == ["citation_coverage", "groundedness"]
    for gap in proposal["gaps"]:
        assert gap["groundingSources"] == GROUNDING
        assert gap["interactionIds"]


def test_lineage_ids_present_and_scoped():
    proposal = _run()
    assert proposal["sourceInteractionIds"] == ["ix-cite-1", "ix-ground-1"]
    assert "ix-act-1" not in proposal["sourceInteractionIds"]
    assert "ix-other-agent" not in proposal["sourceInteractionIds"]


def test_offline_gate_guardrail_runs_and_passes_on_v1():
    proposal = _run()
    assert proposal["offlineGatePassed"] is True


def test_grounding_sources_echoed_on_proposal():
    proposal = _run()
    assert proposal["groundingSources"] == GROUNDING


def test_proposal_is_advisory_and_not_applied():
    proposal = _run()
    assert proposal["advisory"] is True
    assert proposal["applied"] is False
    assert proposal["approvedToApply"] is False


def test_never_writes_agent_md_or_grounding():
    before = INSTRUCTIONS.read_bytes()
    _run()
    assert INSTRUCTIONS.read_bytes() == before


def test_no_knowledge_gaps_yields_empty_advisory_proposal():
    proposal = kr.run_knowledge_refresh(
        agent="ooa-agent",
        scored_records=[],
        grounding_sources=GROUNDING,
        gate_dataset_path=GATE_DATASET,
    )
    assert proposal["knowledgeMetrics"] == []
    assert proposal["refreshActions"] == []
    assert proposal["gaps"] == []
    assert proposal["offlineGatePassed"] is True


def _load_job():
    spec = importlib.util.spec_from_file_location(
        "knowledge_refresh_job", REPO_ROOT / "evals" / "knowledge_refresh_job.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_job_main_returns_zero():
    assert _load_job().main() == 0
