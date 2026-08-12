"""Web-IQ-specific behaviour (Sprint 44, ADR-0060). Trust-B, advisory-only.

Generic discovery/determinism/parse-to-records coverage comes from
test_registry.py + test_simulators.py, which parametrize over every external
provider. This file locks the behaviours unique to the Trust-B web-grounding
channel: trust tier, web citations, low-confidence quarantine, the PHI-query
guard, the gated live binding, and the "never fires a trigger" guarantee.
"""
import os
import unittest
from pathlib import Path
from unittest import mock

import trigger_rules
import normalize
from providers.registry import discover, load_manifest
from providers.runner import run_provider
from providers.webiq import parse, simulator, live


class TestWebIqManifest(unittest.TestCase):
    def test_discovered_as_trust_b_external_simulated(self):
        specs = {s.source_id: s for s in discover()}
        self.assertIn("webiq", specs)
        spec = specs["webiq"]
        self.assertEqual(spec.trust_tier, "B")
        self.assertEqual(spec.channel_kind, "external")
        self.assertEqual(spec.default_mode, "live")


class TestWebIqParse(unittest.TestCase):
    def test_emits_trust_b_record_with_webcitations(self):
        rec = parse.parse(simulator.generate(seed=1))[0]
        self.assertEqual(rec["sourceId"], "webiq")
        self.assertEqual(rec["trustTier"], "B")
        self.assertEqual(rec["hazardType"], "epidemic")
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


class TestWebIqLiveBinding(unittest.TestCase):
    """Live binding fits the runner: real POST when a key is set, else fall back
    to the simulator (the key's presence is the enablement gate)."""

    def _spec(self):
        p = Path(__file__).resolve().parents[1] / "providers" / "webiq" / "provider.yaml"
        return load_manifest(p)

    def test_live_post_maps_webresults_and_marks_live(self):
        def fake_post(url, body, headers):
            self.assertEqual(url, "https://api.microsoft.ai/v3/search/web")
            self.assertIn("query", body)
            return {"webResults": [
                {"title": "Respiratory surge in ZH hospitals", "url": "https://example.invalid/a",
                 "content": "EDs report rising respiratory presentations.", "crawledAt": "2026-08-12T06:00:00Z"},
                {"title": "b", "url": "https://example.invalid/b", "content": "c", "crawledAt": "2026-08-12T05:00:00Z"},
                {"title": "c", "url": "https://example.invalid/c", "content": "d", "crawledAt": "2026-08-12T04:00:00Z"},
            ], "traceId": "0"}
        with mock.patch.dict(os.environ, {"WEBIQ_API_KEY": "test-key"}, clear=False):
            recs = run_provider(self._spec(), transport=fake_post)
        self.assertTrue(recs)
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "live")
        self.assertEqual(recs[0]["trustTier"], "B")
        self.assertIn(recs[0]["hazardType"], {"epidemic", "heat", "mass-casualty", "air-quality"})
        self.assertTrue(recs[0]["webCitations"][0]["uri"].startswith("https://"))

    def test_missing_config_falls_back_to_simulated(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("WEBIQ_API_KEY", None)
            os.environ.pop("WEBIQ_ENTRA_ENABLED", None)
            recs = run_provider(self._spec())  # no transport, no auth config -> fallback
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "simulated")
        self.assertEqual(recs[0]["provenance"]["fellBackFrom"], "live")

    def test_auth_header_prefers_apikey(self):
        with mock.patch.dict(os.environ, {"WEBIQ_API_KEY": "k"}, clear=False):
            hdr = live.LiveBinding("https://x")._auth_header()
        self.assertEqual(hdr["x-apikey"], "k")
        self.assertNotIn("Authorization", hdr)

    def test_auth_header_uses_entra_bearer_when_enabled(self):
        with mock.patch.dict(os.environ, {"WEBIQ_ENTRA_ENABLED": "true"}, clear=False), \
                mock.patch("azure.identity.DefaultAzureCredential") as cred:
            os.environ.pop("WEBIQ_API_KEY", None)
            cred.return_value.get_token.return_value.token = "jwt123"
            hdr = live.LiveBinding("https://x")._auth_header()
        self.assertEqual(hdr["Authorization"], "Bearer jwt123")
        cred.return_value.get_token.assert_called_once_with("https://api.microsoft.ai/.default")

    def test_auth_header_refuses_when_unconfigured(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("WEBIQ_API_KEY", None)
            os.environ.pop("WEBIQ_ENTRA_ENABLED", None)
            with self.assertRaises(RuntimeError):
                live.LiveBinding("https://x")._auth_header()


class TestWebIqTrustBGuard(unittest.TestCase):
    def test_trust_b_never_fires_a_trigger(self):
        rec = parse.parse(simulator.generate(seed=1))[0]
        result = trigger_rules.evaluate(rec, trigger_rules.load_rules())
        self.assertFalse(result.fired)
        self.assertEqual(result.outcome, "trust-tier-not-a")


class TestWebIqChannelReadiness(unittest.TestCase):
    """Sprint 44 M5 (FR-SIG-007): sandbox Channel Readiness Scorecard over the
    curated Web IQ simulator feed - schema conformance, provenance completeness,
    and dedup, as the pre-activation gate the signal-agent runs before any HITL
    activation request. No network I/O."""

    _REQUIRED = ["signalId", "sourceId", "sourceAuthority", "trustTier", "hazardType",
                 "severity", "certainty", "urgency", "region", "onset", "status", "provenance"]
    _PROV_REQUIRED = ["ingestedAt", "connectorVersion", "licence", "rawHash"]

    def _scorecard(self, recs):
        schema_ok = bool(recs) and all(
            all(f in r and r[f] not in (None, "", []) for f in self._REQUIRED) for r in recs
        )
        prov_ok = bool(recs) and all(
            all(r["provenance"].get(f) for f in self._PROV_REQUIRED) for r in recs
        )
        keys = [normalize.dedup_key(r) for r in recs]
        dedup_ok = len(keys) == len(set(keys))
        return {
            "schemaConformant": schema_ok, "provenanceComplete": prov_ok,
            "dedupOk": dedup_ok, "ready": schema_ok and prov_ok and dedup_ok,
            "sampleSize": len(recs),
        }

    def test_webiq_simulator_feed_is_channel_ready(self):
        recs = parse.parse(simulator.generate(seed=3), active_binding="simulated")
        card = self._scorecard(recs)
        self.assertTrue(card["ready"], card)
        self.assertTrue(card["schemaConformant"])
        self.assertTrue(card["provenanceComplete"])
        self.assertTrue(card["dedupOk"])


if __name__ == "__main__":
    unittest.main()
