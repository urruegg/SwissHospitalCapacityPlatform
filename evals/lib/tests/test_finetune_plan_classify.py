"""T2 - classify_finetune_examples (Sprint 30 M9).

Given the curator's selections (record + selection reasons), assign each curated
interaction to the fine-tune method(s) its signal supports: SFT (quality
failures), DPO (thumbs pairs), RFT (gradeable / scored). Pure, deterministic, and
PHI-safe (ids only). A single interaction may feed more than one method.
"""

from lib import curator, finetune_plan as ft


def _sel(iid, reasons, scores=None):
    return {
        "record": {
            "interactionId": iid,
            "agent": "ooa-agent",
            "eval": {"scored": True, "scores": scores or {}},
        },
        "reasons": list(reasons),
    }


def test_eval_failure_feeds_sft_and_rft():
    selected = [_sel("ix-1", [curator.EVAL_FAILURE], {"citation_coverage": {"passed": False, "score": 0.0}})]
    examples = ft.classify_finetune_examples(selected)
    assert examples["sft"] == ["ix-1"]
    assert examples["rft"] == ["ix-1"]  # has scores -> gradeable
    assert examples["dpo"] == []


def test_thumbs_down_feeds_dpo_only_when_no_scores():
    selected = [_sel("ix-2", [curator.THUMBS_DOWN], {})]
    examples = ft.classify_finetune_examples(selected)
    assert examples["dpo"] == ["ix-2"]
    assert examples["sft"] == []
    assert examples["rft"] == []  # no scores -> not gradeable


def test_low_score_feeds_sft_and_rft():
    selected = [_sel("ix-3", [curator.LOW_SCORE], {"actionability": {"passed": True, "score": 0.2}})]
    examples = ft.classify_finetune_examples(selected)
    assert examples["sft"] == ["ix-3"]
    assert examples["rft"] == ["ix-3"]


def test_misrefusal_feeds_sft():
    selected = [_sel("ix-4", [curator.MISREFUSAL], {})]
    examples = ft.classify_finetune_examples(selected)
    assert examples["sft"] == ["ix-4"]


def test_random_sample_alone_feeds_no_method():
    # A pure random-sample selection with no failure signal and no scores does
    # not become a fine-tune example.
    selected = [_sel("ix-5", [curator.RANDOM_SAMPLE], {})]
    examples = ft.classify_finetune_examples(selected)
    assert examples == {"sft": [], "dpo": [], "rft": []}


def test_ids_are_sorted_and_deduped_per_method():
    selected = [
        _sel("ix-b", [curator.EVAL_FAILURE], {"m": {"passed": False, "score": 0.0}}),
        _sel("ix-a", [curator.LOW_SCORE], {"m": {"passed": True, "score": 0.1}}),
    ]
    examples = ft.classify_finetune_examples(selected)
    assert examples["sft"] == ["ix-a", "ix-b"]
    assert examples["rft"] == ["ix-a", "ix-b"]


def test_thumbs_plus_score_feeds_dpo_and_rft():
    selected = [_sel("ix-6", [curator.THUMBS_DOWN], {"advisory_voice": {"passed": True, "score": 0.9}})]
    examples = ft.classify_finetune_examples(selected)
    assert examples["dpo"] == ["ix-6"]
    assert examples["rft"] == ["ix-6"]
    assert examples["sft"] == []


def test_empty_selection_yields_empty_methods():
    assert ft.classify_finetune_examples([]) == {"sft": [], "dpo": [], "rft": []}
