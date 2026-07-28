"""T4 (RED) — groundedness evaluator (inline citations must be real)."""

from lib import evaluators


def _record(answer="", citations=None, refused=False):
    return {
        "response": {"answerRedacted": answer, "citations": citations or [], "refused": refused},
        "request": {"lang": "en"},
    }


def test_inline_citation_backed_by_sources_passes():
    rec = _record("Ward 4C at 94% [gold.encounter@s1].", citations=["gold.encounter@s1"])
    result = evaluators.groundedness(rec)
    assert result.passed is True
    assert result.evaluator == "groundedness"


def test_fabricated_inline_citation_fails():
    rec = _record("Ward 4C at 94% [gold.made_up@s9].", citations=["gold.encounter@s1"])
    result = evaluators.groundedness(rec)
    assert result.passed is False


def test_marker_free_answer_is_not_applicable():
    rec = _record("A plain sentence with no markers.", citations=[])
    assert evaluators.groundedness(rec).passed is True


def test_refusal_is_not_applicable():
    rec = _record("REFUSE: out-of-scope-region", refused=True)
    assert evaluators.groundedness(rec).passed is True


def test_redacted_marker_is_ignored():
    rec = _record("The token [redacted] was masked.", citations=[])
    assert evaluators.groundedness(rec).passed is True
