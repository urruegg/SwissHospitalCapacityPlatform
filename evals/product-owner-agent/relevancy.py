"""Sprint 41 WS-EVAL Task EVAL.2: does the retrieved chunk set actually answer
the question, not just "is every claim cited"? Baseline: token-overlap ratio
between the question's content words and the chunk text. Deterministic, no
network call, no extra model dependency - good enough to catch "cited but
irrelevant" regressions. Deliberately coarse (see run_evals.RELEVANCY_GATE for
why); an LLM-judge scorer is a tracked follow-up, not this task.
"""
from __future__ import annotations

import re

_STOPWORDS = {"the", "a", "an", "is", "are", "what", "for", "of", "to", "and"}


def _content_words(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in _STOPWORDS}


def score_relevancy(question: str, chunks: list[dict]) -> float:
    """Fraction of the question's content words that also appear somewhere
    in the chunk texts. ``0.0`` when there is no question text or no chunks.
    """

    q_words = _content_words(question)
    if not q_words:
        return 0.0
    chunk_words: set[str] = set()
    for chunk in chunks:
        chunk_words |= _content_words(chunk.get("text", ""))
    overlap = q_words & chunk_words
    return len(overlap) / len(q_words)
