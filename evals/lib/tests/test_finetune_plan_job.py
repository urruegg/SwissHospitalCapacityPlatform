"""T3 - build_finetune_plan + job (Sprint 30 M9).

End-to-end deterministic fine-tune planner: curated scored records classify into
SFT / DPO / RFT examples; the golden dataset validates the current baseline
through the offline gate (the evaluation-gated-deploy / checkpoint-selection
guardrail). The plan is advisory and must never launch training or deploy a model.
"""

import importlib.util
from pathlib import Path

from lib import finetune_plan as ft

REPO_ROOT = Path(__file__).resolve().parents[3]
OOA_DIR = REPO_ROOT / "evals" / "ooa-agent"
GATE_DATASET = OOA_DIR / "datasets" / "v1" / "interactions.jsonl"


def _scored_records():
    return [
        {
            "interactionId": "ix-fail-1",
            "agent": "ooa-agent",
            "eval": {
                "scored": True,
                "passedAll": False,
                "scores": {"citation_coverage": {"passed": False, "score": 0.0}},
            },
        },
        {
            "interactionId": "ix-thumbs-1",
            "agent": "ooa-agent",
            "eval": {"scored": True, "passedAll": True, "scores": {}},
            "userEvents": [{"type": "thumbs", "value": "down"}],
        },
        {
            "interactionId": "ix-low-1",
            "agent": "ooa-agent",
            "eval": {
                "scored": True,
                "passedAll": False,
                "scores": {"actionability": {"passed": True, "score": 0.2}},
            },
        },
        {
            "interactionId": "ix-other-agent",  # different agent -> excluded by scoping
            "agent": "bmca-agent",
            "eval": {
                "scored": True,
                "passedAll": False,
                "scores": {"phi_leak": {"passed": False, "score": 0.0}},
            },
        },
    ]


def _run():
    return ft.build_finetune_plan(
        agent="ooa-agent",
        scored_records=_scored_records(),
        gate_dataset_path=GATE_DATASET,
    )


def _method(plan, name):
    return next(m for m in plan["methods"] if m["method"] == name)


def test_examples_classified_per_method_and_scoped():
    plan = _run()
    assert _method(plan, "sft")["interactionIds"] == ["ix-fail-1", "ix-low-1"]
    assert _method(plan, "dpo")["interactionIds"] == ["ix-thumbs-1"]
    assert _method(plan, "rft")["interactionIds"] == ["ix-fail-1", "ix-low-1"]
    # bmca record excluded from every method (agent scoping).
    for m in plan["methods"]:
        assert "ix-other-agent" not in m["interactionIds"]


def test_feasible_methods_in_canonical_order():
    plan = _run()
    assert plan["feasibleMethods"] == ["sft", "dpo", "rft"]


def test_method_plans_carry_counts_and_descriptions():
    plan = _run()
    sft = _method(plan, "sft")
    assert sft["feasible"] is True
    assert sft["exampleCount"] == 2
    assert sft["description"] == ft.METHOD_LIBRARY["sft"]


def test_region_is_demo_eastus2():
    plan = _run()
    assert plan["region"] == "eastus2"
    assert plan["region"] == ft.DEMO_REGION


def test_lineage_ids_present_and_scoped():
    plan = _run()
    assert plan["sourceInteractionIds"] == ["ix-fail-1", "ix-low-1", "ix-thumbs-1"]
    assert "ix-other-agent" not in plan["sourceInteractionIds"]


def test_deploy_is_evaluation_gated_by_offline_suite():
    plan = _run()
    assert plan["evaluationGatedDeploy"] is True
    assert plan["checkpointSelection"] == "offline-regression-gate"
    assert plan["offlineGatePassed"] is True


def test_plan_is_advisory_and_not_applied():
    plan = _run()
    assert plan["advisory"] is True
    assert plan["applied"] is False
    assert plan["approvedToApply"] is False


def test_no_signal_yields_empty_advisory_plan():
    plan = ft.build_finetune_plan(
        agent="ooa-agent",
        scored_records=[],
        gate_dataset_path=GATE_DATASET,
    )
    assert plan["feasibleMethods"] == []
    assert plan["sourceInteractionIds"] == []
    for m in plan["methods"]:
        assert m["feasible"] is False
        assert m["exampleCount"] == 0
    # The evaluation-gated-deploy guardrail still runs on the baseline.
    assert plan["offlineGatePassed"] is True


def _load_job():
    spec = importlib.util.spec_from_file_location(
        "finetune_plan_job", REPO_ROOT / "evals" / "finetune_plan_job.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_job_main_returns_zero():
    assert _load_job().main() == 0
