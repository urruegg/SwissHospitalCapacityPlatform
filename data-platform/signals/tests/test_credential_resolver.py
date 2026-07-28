"""Sprint 32 SGA ? credential->competency resolver + skills enrichment."""
from __future__ import annotations

import pytest

from signals.credential_resolver import resolve_competencies, enrich_skill_tags

TAXONOMY = {
    "ICU-Nursing-Cert": ["comp.icu.core", "comp.ventilation"],
    "FMH-Anaesthesia": ["comp.anaesthesia", "comp.airway"],
}


def test_resolve_known_credential():
    assert resolve_competencies("ICU-Nursing-Cert", TAXONOMY) == ["comp.icu.core", "comp.ventilation"]


def test_resolve_unknown_credential_is_empty():
    assert resolve_competencies("Unknown-Cert", TAXONOMY) == []


def test_enrich_skill_tags_by_workid_is_pseudonymous_and_deduped():
    pool = {"WID-abcdef01": ["comp.icu.core"]}
    creds = [
        {"workId": "WID-abcdef01", "credentialType": "ICU-Nursing-Cert"},
        {"workId": "WID-99887766", "credentialType": "FMH-Anaesthesia"},
    ]
    out = enrich_skill_tags(pool, creds, TAXONOMY)
    assert set(out["WID-abcdef01"]) == {"comp.icu.core", "comp.ventilation"}   # merged, deduped
    assert set(out["WID-99887766"]) == {"comp.anaesthesia", "comp.airway"}
    # keys are pseudonymous work-IDs only
    assert all(k.startswith("WID-") for k in out)


def test_enrich_rejects_non_pseudonymous_key():
    with pytest.raises(ValueError):
        enrich_skill_tags({}, [{"workId": "Anna Meier", "credentialType": "ICU-Nursing-Cert"}], TAXONOMY)
