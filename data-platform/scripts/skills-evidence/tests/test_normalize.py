import unittest

from normalize import (
    CONTRACT_ID,
    CONTRACT_VERSION,
    build_record,
    dedup_key,
    envelope,
    raw_hash,
)


class TestNormalize(unittest.TestCase):
    def test_raw_hash_is_stable_sha256(self):
        self.assertEqual(raw_hash(b"abc"), raw_hash(b"abc"))
        self.assertEqual(len(raw_hash(b"abc")), 64)

    def test_dedup_key_is_person_skill_system(self):
        base = dict(externalSystem="lms", externalPersonRef="p-1",
                    externalSkillCode="BLS")
        self.assertEqual(dedup_key(base), dedup_key({**base, "externalSkillLabel": "x"}))
        self.assertNotEqual(dedup_key(base), dedup_key({**base, "externalSkillCode": "ACLS"}))

    def test_build_record_carries_badge_and_provenance(self):
        rec = build_record(
            evidence_id="ev-1", external_system="lms", source_mode="simulated",
            trust_tier="A", external_person_ref="p-1", external_skill_code="BLS",
            external_skill_label="Basic Life Support",
            self_or_confirmed="employer_confirmed", captured_at="2026-07-01",
            connector_version="lms-1.0.0", licence="synthetic", raw={"x": 1},
            worker_gln=None, external_level="proficient", consent_scope=None,
        )
        self.assertEqual(rec["sourceMode"], "simulated")
        self.assertEqual(rec["trustTier"], "A")
        self.assertEqual(rec["selfOrConfirmed"], "employer_confirmed")
        self.assertEqual(rec["externalSystem"], "lms")
        self.assertEqual(rec["provenance"]["connectorVersion"], "lms-1.0.0")
        self.assertEqual(len(rec["provenance"]["rawHash"]), 64)

    def test_build_record_defaults(self):
        rec = build_record(
            evidence_id="ev-2", external_system="work_id", source_mode="simulated",
            external_person_ref="p-2", external_skill_code="ANAES",
            external_skill_label="Anaesthesia", self_or_confirmed="self",
            captured_at="2026-07-02", connector_version="work_id-1.0.0",
            licence="synthetic", raw=b"{}",
        )
        self.assertEqual(rec["trustTier"], "A")
        self.assertIsNone(rec["workerGln"])
        self.assertIsNone(rec["consentScope"])
        self.assertIsNone(rec["externalLevel"])


class TestEnvelope(unittest.TestCase):
    def test_envelope_sets_contract_id_and_version(self):
        env = envelope([], dataset_id="DS-SKILL-EVIDENCE-test")
        self.assertEqual(env["contractId"], CONTRACT_ID)
        self.assertEqual(env["contractVersion"], CONTRACT_VERSION)
        self.assertEqual(env["classification"], "personal-synthetic")
        self.assertEqual(env["datasetId"], "DS-SKILL-EVIDENCE-test")


if __name__ == "__main__":
    unittest.main()
