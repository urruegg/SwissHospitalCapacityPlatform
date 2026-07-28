"""T2 — build_candidate_instructions (Sprint 30 M7).

Pure, in-memory string transform: base instructions + an appended advisory
directives block. Writes nothing to disk; idempotent; preserves base verbatim.
"""

from lib import prompt_optimize as po

BASE = "# ooa-agent\n\nYou are the Occupancy Copilot.\n\n## 1. Identity\n\nAdvisory only.\n"

DIRECTIVES = [
    po.DIRECTIVE_LIBRARY["citation_coverage"],
    po.DIRECTIVE_LIBRARY["advisory_voice"],
]

HEADING = "## Optimization directives (advisory, Sprint 30 M7)"


def test_base_is_preserved_verbatim_above_the_block():
    candidate = po.build_candidate_instructions(BASE, DIRECTIVES)
    assert candidate.startswith(BASE)


def test_directives_appear_in_the_appended_block():
    candidate = po.build_candidate_instructions(BASE, DIRECTIVES)
    assert HEADING in candidate
    for d in DIRECTIVES:
        assert d in candidate
    # The block comes after the base content.
    assert candidate.index(HEADING) >= len(BASE)


def test_empty_directives_returns_base_unchanged():
    assert po.build_candidate_instructions(BASE, []) == BASE
    assert HEADING not in po.build_candidate_instructions(BASE, [])


def test_idempotent_no_duplicate_block_on_second_pass():
    once = po.build_candidate_instructions(BASE, DIRECTIVES)
    twice = po.build_candidate_instructions(once, DIRECTIVES)
    assert twice == once
    assert twice.count(HEADING) == 1


def test_reoptimizing_replaces_the_block_rather_than_stacking():
    once = po.build_candidate_instructions(BASE, DIRECTIVES)
    new_directives = [po.DIRECTIVE_LIBRARY["phi_leak"]]
    twice = po.build_candidate_instructions(once, new_directives)
    assert twice.count(HEADING) == 1
    assert po.DIRECTIVE_LIBRARY["phi_leak"] in twice
    # The superseded directives are gone; base is still intact.
    assert twice.startswith(BASE)
    assert po.DIRECTIVE_LIBRARY["citation_coverage"] not in twice


def test_writes_nothing_returns_str():
    result = po.build_candidate_instructions(BASE, DIRECTIVES)
    assert isinstance(result, str)
