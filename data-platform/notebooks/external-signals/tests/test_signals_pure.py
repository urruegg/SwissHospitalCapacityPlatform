import importlib.util
import unittest
from pathlib import Path

NB = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), NB / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSilverGoldPure(unittest.TestCase):
    def test_silver_quarantines_non_actual(self):
        silver = _load("build_silver_signals.py")
        recs = [{"signalId": "a", "status": "Actual", "hazardType": "heat",
                 "region": {"cantons": ["ZH"]}, "onset": "t", "sourceId": "m", "severity": "Severe"},
                {"signalId": "b", "status": "Exercise", "hazardType": "heat",
                 "region": {"cantons": ["ZH"]}, "onset": "t", "sourceId": "m", "severity": "Severe"}]
        kept, quarantined = silver.split_quarantine(recs)
        self.assertEqual([r["signalId"] for r in kept], ["a"])
        self.assertEqual([r["signalId"] for r in quarantined], ["b"])

    def test_gold_signal_row_projection(self):
        gold = _load("build_gold_signals.py")
        row = gold.to_gold_signal({"signalId": "a", "sourceId": "sed", "hazardType": "earthquake",
                                   "severity": "Severe", "defaultLageTier": 3,
                                   "mappedScenarioTemplate": "F1", "onset": "t",
                                   "region": {"cantons": ["VS"]}, "status": "Actual"})
        self.assertEqual(row["ext_scenario_template"], "F1")
        self.assertEqual(row["ext_lage_tier"], 3)

    def test_gold_tables_bundles_fact_and_three_dims(self):
        gold = _load("build_gold_signals.py")
        records = [
            {
                "signalId": "sig-001",
                "sourceId": "src-fed",
                "sourceAuthority": "BABS",
                "trustTier": "T1",
                "hazardType": "pandemic",
                "severity": "Severe",
                "mappedScenarioTemplate": "F3",
                "defaultLageTier": 2,
                "onset": "2026-07-01T00:00:00Z",
                "status": "Actual",
                "region": {"cantons": ["ZH", "BE"]},
                "provenance": {
                    "activeBinding": "simulated",
                    "fellBackFrom": "live",
                    "ingestedAt": "2026-07-01T06:00:00Z",
                },
            }
        ]
        result = gold.gold_tables(records)
        # Must return exactly the four expected keys
        self.assertEqual(
            set(result.keys()),
            {"ext_fact_signal", "ext_dim_source", "ext_dim_hazard_type", "ext_dim_region"},
        )
        # Fact row preserves the signalId
        self.assertEqual(result["ext_fact_signal"][0]["ext_signal_id"], "sig-001")
        # Source dim maps "simulated" activeBinding to "Simulated"
        self.assertEqual(result["ext_dim_source"][0]["ext_data_mode"], "Simulated")
        # Region dim has one row per canton
        cantons = {r["ext_canton"] for r in result["ext_dim_region"]}
        self.assertEqual(cantons, {"ZH", "BE"})


    def test_silver_kept_rows_carry_gold_consumer_keys(self):
        silver = _load("build_silver_signals.py")
        actual = {
            "signalId": "cap-2026-heat-zh-1",
            "sourceId": "alertswiss",
            "sourceAuthority": "BABS/FOCP",
            "trustTier": "A",
            "hazardType": "heat",
            "severity": "Severe",
            "certainty": "Likely",
            "urgency": "Immediate",
            "region": {"cantons": ["ZH"]},
            "onset": "2026-07-17T12:00:00Z",
            "status": "Actual",
            "mappedScenarioTemplate": "F8",
            "defaultLageTier": 2,
            "provenance": {
                "ingestedAt": "2026-07-23T12:44:45Z",
                "connectorVersion": "alertswiss-2.0.0",
                "licence": "Alertswiss-CAP-open",
                "activeBinding": "live",
                "fellBackFrom": None,
                "channelKind": "external",
            },
        }
        exercise = {
            "signalId": "test-001",
            "status": "Exercise",
            "hazardType": "heat",
            "region": {"cantons": ["ZH"]},
            "onset": "t",
            "sourceId": "m",
            "severity": "Minor",
        }
        kept, quarantined = silver.split_quarantine([actual, exercise])
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(quarantined), 1)
        self.assertEqual(quarantined[0]["signalId"], "test-001")
        required_top = {
            "signalId", "sourceId", "sourceAuthority", "trustTier", "hazardType",
            "severity", "mappedScenarioTemplate", "defaultLageTier", "onset", "status",
        }
        self.assertTrue(required_top <= set(kept[0]))
        self.assertEqual(kept[0]["region"]["cantons"], ["ZH"])
        prov = kept[0]["provenance"]
        self.assertIn("activeBinding", prov)
        self.assertIn("fellBackFrom", prov)
        self.assertIn("ingestedAt", prov)


if __name__ == "__main__":
    unittest.main()
