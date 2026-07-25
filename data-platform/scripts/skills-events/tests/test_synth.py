"""Unit tests for the DC-SKILL-EVENT-v1 synthetic seeder (Spark-free).

Mirrors ``skills-evidence/tests/test_schema_conformance.py``: the seeder must
produce a schema-valid envelope, cover all three event kinds, and enforce the
consent GLN-promotion rule at the source (grant carries the GLN, revoke clears it).
"""
import sys
import unittest
from pathlib import Path

_PKG = Path(__file__).resolve().parents[1]
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

import skill_events_synth as synth  # noqa: E402
from normalize import CONTRACT_ID, EVENT_KINDS, dedup_key  # noqa: E402


class TestSkillEventsSynth(unittest.TestCase):
    def setUp(self):
        self.doc = synth.build_envelope()
        self.records = self.doc["records"]

    def test_envelope_is_schema_valid(self):
        self.assertEqual(synth.validate(self.doc), [])

    def test_contract_identity(self):
        self.assertEqual(self.doc["contractId"], CONTRACT_ID)
        self.assertEqual(self.doc["classification"], "personal-synthetic")
        self.assertEqual(self.doc["residency"], "CH")

    def test_all_three_event_kinds_present(self):
        kinds = {r["eventKind"] for r in self.records}
        self.assertEqual(kinds, set(EVENT_KINDS))

    def test_records_carry_badge(self):
        for r in self.records:
            self.assertEqual(r["sourceMode"], "simulated")
            self.assertIn(r["trustTier"], {"A", "B", "C"})

    def test_grant_carries_gln_revoke_clears_it(self):
        consent = [r for r in self.records if r["eventKind"] == "consent-grant-or-revoke"]
        grants = [r for r in consent if r["consentAction"] == "grant"]
        revokes = [r for r in consent if r["consentAction"] == "revoke"]
        self.assertTrue(grants and revokes)
        for g in grants:
            self.assertIsNotNone(g["workerGln"])
            self.assertIsNotNone(g["consentScope"])
        for rv in revokes:
            self.assertIsNone(rv["workerGln"])
            self.assertIsNone(rv["consentScope"])

    def test_credential_expiry_marks_invalid(self):
        expiries = [r for r in self.records if r["eventKind"] == "credential-expiry"]
        self.assertTrue(expiries)
        for e in expiries:
            self.assertFalse(e["credentialValid"])

    def test_confirmed_assertion_flag(self):
        confs = [r for r in self.records if r["eventKind"] == "newly-confirmed-assertion"]
        self.assertTrue(confs)
        for c in confs:
            self.assertTrue(c["confirmed"])

    def test_dedup_keys_are_unique(self):
        keys = [dedup_key(r) for r in self.records]
        self.assertEqual(len(keys), len(set(keys)))

    def test_provenance_has_raw_hash(self):
        for r in self.records:
            self.assertRegex(r["provenance"]["rawHash"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
