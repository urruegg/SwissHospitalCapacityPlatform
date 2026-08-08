"""Sprint 41 WS-EVAL Task EVAL.2: relevancy/groundedness baseline scorer.

Note on the two example chunks below: the plan's inline sample used a
"relevant chunk" example whose own overlap-ratio math does not clear its
stated >= 0.6 gate under the described formula (only "MVP" overlaps out of
5 question content words -> 0.2, not >= 0.6) - verified by hand before
writing this file. The chunk text here is chosen so the arithmetic is
correct and reproducible: 3 of the question's 5 content words
(curavias/mvp/value) recur verbatim -> exactly 3/5 = 0.6.
"""

from relevancy import score_relevancy


def test_relevant_chunk_scores_high():
    score = score_relevancy(
        question="What is the strategic value case for the Curavias MVP?",
        chunks=[
            {
                "text": "The Curavias MVP delivers real value for patient-flow "
                "and capacity teams."
            }
        ],
    )
    assert score >= 0.6


def test_irrelevant_chunk_scores_low():
    score = score_relevancy(
        question="What is the strategic value case for the Curavias MVP?",
        chunks=[{"text": "Marco Weber is a Cloud & AI Solution Engineer."}],
    )
    assert score < 0.3


def test_empty_question_scores_zero():
    assert score_relevancy("", [{"text": "anything at all"}]) == 0.0


def test_no_chunks_scores_zero():
    assert score_relevancy("What is the value case?", []) == 0.0


def test_partial_overlap_is_a_fraction_of_question_content_words():
    score = score_relevancy(
        question="What is the annual run cost against the BVA baseline?",
        chunks=[
            {
                "text": "The effective run cost is presented as a range within "
                "the BVA plus/minus 30 percent band with an as-of stamp."
            }
        ],
    )
    # content words: annual, run, cost, against, bva, baseline (6);
    # overlap: run, cost, bva (3) -> 0.5
    assert score == 0.5
