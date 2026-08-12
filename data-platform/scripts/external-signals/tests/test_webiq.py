"""Web-IQ-specific behaviour (Sprint 44, ADR-0060). Trust-B, advisory-only.

Generic discovery/determinism/parse-to-records coverage comes from
test_registry.py + test_simulators.py, which parametrize over every external
provider. This file locks the behaviours unique to the Trust-B web-grounding
channel: trust tier, web citations, low-confidence quarantine, the PHI-query
guard, the gated live binding, and the "never fires a trigger" guarantee.
"""
import os
import unittest
from unittest import mock

import trigger_rules
from providers.registry import discover
from providers.webiq import parse, simulator, live_adapter


class TestWebIqManifest(unittest.TestCase):
    def test_discovered_as_trust_b_external_simulated(self):
        specs = {s.source_id: s for s in discover()}
        self.assertIn("webiq", specs)
        spec = specs["webiq"]
        self.assertEqual(spec.trust_tier, "B")
        self.assertEqual(spec.channel_kind, "external")
        self.assertEqual(spec.default_mode, "simulated")


class TestWebIqParse(unittest.TestCase):
    def test_emits_trust_b_record_with_webcitations(self):
        rec = parse.parse(simulator.generate(seed=1))[0]
        self.assertEqual(rec["sourceId"], "webiq")
        self.assertEqual(rec["trustTier"], "B")
        self.assertEqual(rec["hazardType"], "outbreak")
        self.assertEqual(rec["status"], "Actual")  # confidence 0.72 >= 0.6
        self.assertTrue(rec["webCitations"])
        self.assertTrue(rec["webCitations"][0]["uri"].startswith("https://"))
        self.assertEqual(rec["provenance"]["licence"], "microsoft-web-iq-preview-terms")

    def test_low_confidence_is_quarantined(self):
        payload = {"results": [{
            "title": "unverified rumour", "uri": "https://example.invalid/x",
            "publishedAt": "2026-08-12T06:00:00Z", "hazard": "outbreak",
            "cantons": ["ZH"], "confidence": 0.3, "snippet": "unconfirmed",
        }]}
        rec = parse.parse(payload)[0]
        self.assertNotEqual(rec["status"], "Actual")  # below threshold -> cannot trigger

    def test_query_builder_rejects_phi_terms(self):
        with self.assertRaises(ValueError):
            parse.build_query(["patient", "AHV 756.1234"])

    def test_query_builder_allows_hazard_terms(self):
        self.assertEqual(parse.build_query(["heat", "Zurich"]), "heat Zurich")


class TestWebIqLiveAdapter(unittest.TestCase):
    def test_disabled_by_default(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("WEBIQ_LIVE_ENABLED", None)
            self.assertFalse(live_adapter.is_enabled())

    def test_fetch_refuses_when_disabled(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("WEBIQ_LIVE_ENABLED", None)
            with self.assertRaises(RuntimeError):
                live_adapter.fetch(["heat", "Zurich"])


class TestWebIqTrustBGuard(unittest.TestCase):
    def test_trust_b_never_fires_a_trigger(self):
        rec = parse.parse(simulator.generate(seed=1))[0]
        result = trigger_rules.evaluate(rec, trigger_rules.load_rules())
        self.assertFalse(result.fired)
        self.assertEqual(result.outcome, "trust-tier-not-a")


if __name__ == "__main__":
    unittest.main()
