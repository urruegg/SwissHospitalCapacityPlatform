"""Spark-free unit tests for the skills-events medallion pure functions.

Covers the Bronze path convention, the Silver PHI/consent gate (deny-by-default
quarantine + the consent-revocation invariant + credential-expiry validity), and
the Gold projection badge propagation. Mirrors
``external-signals/tests/test_signals_pure.py`` / ``test_badge_propagation.py``.
"""
import importlib.util
import unittest
from pathlib import Path

NB = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name[:-3].replace("-", "_"), NB / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bronze = _load("ingest_bronze_skill_events.py")
silver = _load("build_silver_skill_events.py")
gold = _load("build_gold_skill_events.py")


def _revoke(**over):
    rec = {
        "eventId": "wid-evt-001", "eventKind": "consent-grant-or-revoke",
        "externalSystem": "work_id", "sourceMode": "simulated", "trustTier": "C",
        "externalPersonRef": "WID-ANON-3001", "externalSkillCode": "NURS-ICU",
        "effectiveAt": "2026-07-23T09:00:00Z", "consentAction": "revoke",
        "workerGln": "7601190000010", "consentScope": "capacity-planning",
    }
    rec.update(over)
    return rec


def _grant(**over):
    rec = {
        "eventId": "wid-evt-002", "eventKind": "consent-grant-or-revoke",
        "externalSystem": "work_id", "sourceMode": "simulated", "trustTier": "C",
        "externalPersonRef": "WID-ANON-3004", "externalSkillCode": "ANAES",
        "effectiveAt": "2026-07-23T10:30:00Z", "consentAction": "grant",
        "workerGln": "7601190000027", "consentScope": "capacity-planning",
    }
    rec.update(over)
    return rec


def _expiry(**over):
    rec = {
        "eventId": "lms-cred-001", "eventKind": "credential-expiry",
        "externalSystem": "lms", "sourceMode": "simulated", "trustTier": "A",
        "externalPersonRef": "SF-EMP-1001", "externalSkillCode": "BLS",
        "effectiveAt": "2026-07-20T06:00:00Z", "credentialValid": False,
    }
    rec.update(over)
    return rec


class TestBronzePath(unittest.TestCase):
    def test_path_by_kind_and_date(self):
        self.assertEqual(
            bronze.bronze_path("credential-expiry", "2026-07-23"),
            "Files/bronze/skills-events/credential-expiry/2026-07-23",
        )

    def test_requires_kind_and_date(self):
        with self.assertRaises(ValueError):
            bronze.bronze_path("", "2026-07-23")
        with self.assertRaises(ValueError):
            bronze.bronze_path("credential-expiry", "")


class TestSilverGate(unittest.TestCase):
    def test_valid_events_are_kept(self):
        kept, quar = silver.split_quarantine([_grant(), _expiry()])
        self.assertEqual(len(kept), 2)
        self.assertEqual(quar, [])

    def test_bad_event_kind_is_quarantined(self):
        kept, quar = silver.split_quarantine([_expiry(eventKind="not-a-kind")])
        self.assertEqual(kept, [])
        self.assertEqual(len(quar), 1)

    def test_missing_required_field_is_quarantined(self):
        kept, quar = silver.split_quarantine([_expiry(externalPersonRef=None)])
        self.assertEqual(kept, [])
        self.assertEqual(len(quar), 1)

    def test_grant_missing_gln_is_quarantined(self):
        kept, quar = silver.split_quarantine([_grant(workerGln=None)])
        self.assertEqual(kept, [])
        self.assertEqual(len(quar), 1)

    def test_non_consent_event_with_action_is_quarantined(self):
        kept, quar = silver.split_quarantine([_expiry(consentAction="grant")])
        self.assertEqual(kept, [])
        self.assertEqual(len(quar), 1)

    def test_revoke_clears_gln_promotion(self):
        kept, _ = silver.split_quarantine([_revoke()])
        self.assertEqual(len(kept), 1)
        self.assertIsNone(kept[0]["workerGln"])
        self.assertIsNone(kept[0]["consentScope"])

    def test_grant_retains_gln_promotion(self):
        kept, _ = silver.split_quarantine([_grant()])
        self.assertEqual(kept[0]["workerGln"], "7601190000027")
        self.assertEqual(kept[0]["consentScope"], "capacity-planning")

    def test_enforce_consent_gate_is_noop_for_non_revoke(self):
        g = _grant()
        self.assertEqual(silver.enforce_consent_gate(g), g)


class TestGoldProjection(unittest.TestCase):
    def test_data_mode_badge(self):
        self.assertEqual(gold.data_mode_for("simulated"), "Simulated")
        self.assertEqual(gold.data_mode_for("live"), "Live")

    def test_fact_carries_badge_and_kind(self):
        row = gold.to_gold_event(_expiry())
        self.assertEqual(row["skillevt_data_mode"], "Simulated")
        self.assertEqual(row["skillevt_kind"], "credential-expiry")
        self.assertFalse(row["skillevt_credential_valid"])

    def test_dims_are_deduped_and_sorted(self):
        tables = gold.gold_tables([_grant(), _revoke(), _expiry()])
        systems = [r["skillevt_external_system"] for r in tables["skillevt_dim_source"]]
        self.assertEqual(systems, sorted(set(systems)))
        kinds = [r["skillevt_kind"] for r in tables["skillevt_dim_kind"]]
        self.assertEqual(set(kinds), {"consent-grant-or-revoke", "credential-expiry"})

    def test_fact_row_per_event(self):
        tables = gold.gold_tables([_grant(), _revoke(), _expiry()])
        self.assertEqual(len(tables["skillevt_fact_event"]), 3)


if __name__ == "__main__":
    unittest.main()
