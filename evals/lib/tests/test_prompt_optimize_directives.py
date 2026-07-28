"""T1 — directive library + propose_directives (Sprint 30 M7).

The deterministic advisory prompt optimizer maps a failing evaluator metric to a
targeted instruction directive. propose_directives is the pure, order-stable
core reused by the end-to-end job.
"""

from lib import prompt_optimize as po


def test_directive_library_covers_every_seed_metric():
    # All six seed evaluators plus the curator's synthetic user_feedback metric
    # must have a targeted directive.
    for metric in (
        "citation_coverage",
        "groundedness",
        "refusal_correctness",
        "phi_leak",
        "actionability",
        "advisory_voice",
        "user_feedback",
    ):
        assert metric in po.DIRECTIVE_LIBRARY
        assert isinstance(po.DIRECTIVE_LIBRARY[metric], str)
        assert po.DIRECTIVE_LIBRARY[metric].strip()


def test_propose_directives_returns_known_directives():
    directives = po.propose_directives({"citation_coverage", "advisory_voice"})
    assert po.DIRECTIVE_LIBRARY["citation_coverage"] in directives
    assert po.DIRECTIVE_LIBRARY["advisory_voice"] in directives
    assert len(directives) == 2


def test_propose_directives_is_deterministically_ordered():
    # Input order / set iteration order must not change the output order.
    a = po.propose_directives({"advisory_voice", "citation_coverage", "phi_leak"})
    b = po.propose_directives({"phi_leak", "citation_coverage", "advisory_voice"})
    assert a == b
    # Ordered by the canonical DIRECTIVE_LIBRARY insertion order.
    order = list(po.DIRECTIVE_LIBRARY)
    idxs = [order.index(m) for m in ("citation_coverage", "phi_leak", "advisory_voice")]
    assert idxs == sorted(idxs)  # sanity: our three metrics keep library order
    assert a == [
        po.DIRECTIVE_LIBRARY["citation_coverage"],
        po.DIRECTIVE_LIBRARY["phi_leak"],
        po.DIRECTIVE_LIBRARY["advisory_voice"],
    ]


def test_unknown_metric_maps_to_single_generic_directive():
    directives = po.propose_directives({"some_new_metric"})
    assert directives == [po.GENERIC_DIRECTIVE]


def test_unknown_metric_does_not_duplicate_generic():
    directives = po.propose_directives({"unknown_a", "unknown_b"})
    assert directives.count(po.GENERIC_DIRECTIVE) == 1


def test_empty_metrics_yields_no_directives():
    assert po.propose_directives(set()) == []
