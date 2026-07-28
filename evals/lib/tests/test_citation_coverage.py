"""T1 (RED) — citation-coverage evaluator over DC-AGENT-INTERACTION-v1 records."""

from lib import evaluators


def _record(answer: str, citations=None, refused=False):
    return {
        "contractId": "DC-AGENT-INTERACTION-v1",
        "response": {
            "answerRedacted": answer,
            "citations": citations or [],
            "refused": refused,
        },
        "request": {"lang": "en"},
    }


def test_cited_answer_passes():
    rec = _record(
        "Advisory only. Ward 4C peaks at 94% [gold.encounter@s1].",
        citations=["gold.encounter@s1"],
    )
    result = evaluators.citation_coverage(rec)
    assert result.passed is True
    assert result.score == 1.0
    assert result.evaluator == "citation_coverage"


def test_uncited_substantive_claim_fails():
    rec = _record("Advisory only. The forecast is clearly fine.", citations=[])
    result = evaluators.citation_coverage(rec)
    assert result.passed is False
    assert result.score == 0.0


def test_refusal_carries_no_claim_and_passes():
    rec = _record("REFUSE: out-of-scope-region", refused=True)
    result = evaluators.citation_coverage(rec)
    assert result.passed is True


def test_inline_citation_marker_counts_even_without_citations_array():
    rec = _record("The ward is at 94% [gold.bed_assignment@s2].", citations=[])
    result = evaluators.citation_coverage(rec)
    assert result.passed is True
