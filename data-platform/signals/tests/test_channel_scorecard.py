"""Sprint 32 SGA — Channel Readiness Scorecard tests."""
from __future__ import annotations

from signals.channel_scorecard import score_channel

REQUIRED = ["workId", "issuer", "credentialType", "competencyCodes"]


def test_ready_when_all_checks_pass():
    sample = [{"workId": "WID-abcdef01", "issuer": "NAREG", "credentialType": "ICU-Nursing-Cert",
               "competencyCodes": ["comp.icu.core"], "_provenance": {"sourceAuthority": "NAREG"}}]
    card = score_channel(sample, required_fields=REQUIRED)
    assert card["ready"] is True
    assert card["checks"]["schemaConformant"] is True
    assert card["checks"]["provenanceComplete"] is True
    assert card["checks"]["dedupOk"] is True


def test_not_ready_on_missing_field_or_provenance():
    sample = [{"workId": "WID-abcdef01", "issuer": "NAREG", "credentialType": "ICU"}]  # missing competencyCodes + provenance
    card = score_channel(sample, required_fields=REQUIRED)
    assert card["ready"] is False
    assert card["checks"]["schemaConformant"] is False
    assert card["checks"]["provenanceComplete"] is False


def test_dedup_detects_duplicate_workid_credential():
    row = {"workId": "WID-abcdef01", "issuer": "N", "credentialType": "ICU",
           "competencyCodes": ["c"], "_provenance": {"sourceAuthority": "N"}}
    card = score_channel([row, dict(row)], required_fields=REQUIRED)
    assert card["checks"]["dedupOk"] is False
    assert card["ready"] is False
