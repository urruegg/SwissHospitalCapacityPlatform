"""T3 — run_prompt_optimization + job (Sprint 30 M7).

End-to-end deterministic optimizer: curated scored records drive the failing
metrics; the golden dataset validates the candidate through the offline gate.
The proposal is advisory and must never mutate AGENT.md.
"""

import importlib.util
from pathlib import Path

from lib import prompt_optimize as po

REPO_ROOT = Path(__file__).resolve().parents[3]
OOA_DIR = REPO_ROOT / "evals" / "ooa-agent"
GATE_DATASET = OOA_DIR / "datasets" / "v1" / "interactions.jsonl"
INSTRUCTIONS = REPO_ROOT / "agents" / "ooa-agent" / "AGENT.md"


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
            "interactionId": "ix-act-1",
            "agent": "ooa-agent",
            "eval": {
                "scored": True,
                "passedAll": False,
                "scores": {"actionability": {"passed": True, "score": 0.2}},
            },
        },
        {
            "interactionId": "ix-thumbs-1",
            "agent": "ooa-agent",
            "eval": {"scored": True, "passedAll": True, "scores": {}},
            "userEvents": [{"type": "thumbs", "value": "down"}],
        },
        {
            "interactionId": "ix-other-agent",
            "agent": "bmca-agent",
            "eval": {
                "scored": True,
                "passedAll": False,
                "scores": {"phi_leak": {"passed": False, "score": 0.0}},
            },
        },
    ]


def _run():
    return po.run_prompt_optimization(
        agent="ooa-agent",
        scored_records=_scored_records(),
        instructions_path=INSTRUCTIONS,
        gate_dataset_path=GATE_DATASET,
    )


def test_metrics_are_derived_from_the_agents_curated_failures():
    proposal = _run()
    # bmca-agent's phi_leak failure must be excluded (agent scoping).
    assert proposal["sourceMetrics"] == ["actionability", "citation_coverage", "user_feedback"]


def test_directives_match_the_failing_metrics():
    proposal = _run()
    assert proposal["directives"] == po.propose_directives(set(proposal["sourceMetrics"]))
    assert proposal["directives"]


def test_candidate_is_base_plus_advisory_block():
    proposal = _run()
    base = INSTRUCTIONS.read_text(encoding="utf-8")
    assert proposal["candidateInstructions"].startswith(base)
    assert po.DIRECTIVES_HEADING in proposal["candidateInstructions"]


def test_offline_gate_guardrail_runs_and_passes_on_v1():
    proposal = _run()
    assert proposal["offlineGatePassed"] is True


def test_lineage_ids_present_and_scoped():
    proposal = _run()
    assert "ix-cite-1" in proposal["sourceInteractionIds"]
    assert "ix-thumbs-1" in proposal["sourceInteractionIds"]
    assert "ix-other-agent" not in proposal["sourceInteractionIds"]


def test_proposal_is_advisory_and_not_applied():
    proposal = _run()
    assert proposal["advisory"] is True
    assert proposal["applied"] is False
    assert proposal["approvedToApply"] is False


def test_never_writes_agent_md():
    before = INSTRUCTIONS.read_bytes()
    _run()
    assert INSTRUCTIONS.read_bytes() == before


def test_no_failing_metrics_yields_empty_advisory_proposal():
    proposal = po.run_prompt_optimization(
        agent="ooa-agent",
        scored_records=[],
        instructions_path=INSTRUCTIONS,
        gate_dataset_path=GATE_DATASET,
    )
    assert proposal["sourceMetrics"] == []
    assert proposal["directives"] == []
    # With no directives the candidate equals the base (no empty block).
    assert proposal["candidateInstructions"] == INSTRUCTIONS.read_text(encoding="utf-8")
    assert proposal["offlineGatePassed"] is True


def _load_job():
    spec = importlib.util.spec_from_file_location(
        "prompt_optimize_job", REPO_ROOT / "evals" / "prompt_optimize_job.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_job_main_returns_zero():
    assert _load_job().main() == 0
