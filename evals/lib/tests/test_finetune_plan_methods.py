"""T1 - fine-tune method library (Sprint 30 M9).

The deterministic advisory fine-tune plan builder maps the three fine-tune methods
(SFT / DPO / RFT) to the curated data signal each consumes. propose_methods is the
pure, order-stable core reused by the end-to-end job.
"""

from lib import finetune_plan as ft


def test_methods_are_sft_dpo_rft_in_canonical_order():
    assert ft.FINETUNE_METHODS == ("sft", "dpo", "rft")


def test_method_library_covers_every_method():
    for method in ft.FINETUNE_METHODS:
        assert method in ft.METHOD_LIBRARY
        assert isinstance(ft.METHOD_LIBRARY[method], str)
        assert ft.METHOD_LIBRARY[method].strip()


def test_propose_methods_returns_known_descriptions():
    descriptions = ft.propose_methods({"sft", "dpo"})
    assert ft.METHOD_LIBRARY["sft"] in descriptions
    assert ft.METHOD_LIBRARY["dpo"] in descriptions
    assert len(descriptions) == 2


def test_propose_methods_is_deterministically_ordered():
    a = ft.propose_methods({"rft", "sft"})
    b = ft.propose_methods({"sft", "rft"})
    assert a == b
    # Ordered by the canonical FINETUNE_METHODS order (sft before rft).
    assert a == [ft.METHOD_LIBRARY["sft"], ft.METHOD_LIBRARY["rft"]]


def test_unknown_method_is_ignored():
    assert ft.propose_methods({"sft", "not_a_method"}) == [ft.METHOD_LIBRARY["sft"]]


def test_empty_methods_yields_no_descriptions():
    assert ft.propose_methods(set()) == []
