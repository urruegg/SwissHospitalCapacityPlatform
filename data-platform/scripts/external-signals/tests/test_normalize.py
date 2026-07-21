import unittest
from normalize import raw_hash, dedup_key, build_record, CONTRACT_VERSION


class TestNormalize(unittest.TestCase):
    def test_raw_hash_is_stable_sha256(self):
        self.assertEqual(raw_hash(b"abc"), raw_hash(b"abc"))
        self.assertEqual(len(raw_hash(b"abc")), 64)

    def test_dedup_key_ignores_publish_noise(self):
        base = dict(sourceId="meteoswiss", capIdentifier="cap-1",
                    hazardType="heat", region={"cantons": ["ZH"]},
                    onset="2026-07-17T12:00:00Z")
        self.assertEqual(dedup_key(base), dedup_key({**base, "capIdentifier": "cap-1"}))
        self.assertNotEqual(dedup_key(base), dedup_key({**base, "hazardType": "flood"}))

    def test_build_record_fills_provenance_and_defaults(self):
        rec = build_record(
            signal_id="s1", source_id="sed", source_authority="SED-ETH",
            hazard_type="earthquake", severity="Severe", certainty="Observed",
            urgency="Immediate", region={"cantons": ["VS"]},
            onset="2026-07-17T10:00:00Z", status="Actual",
            connector_version="sed-1.0.0", licence="ETH-open", raw=b"{}",
        )
        self.assertEqual(rec["trustTier"], "A")
        self.assertEqual(rec["provenance"]["connectorVersion"], "sed-1.0.0")
        self.assertEqual(len(rec["provenance"]["rawHash"]), 64)


if __name__ == "__main__":
    unittest.main()
