import importlib.util
import unittest
from pathlib import Path

NB = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), NB / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestBadgePropagation(unittest.TestCase):
    def test_active_binding_maps_to_data_mode(self):
        gold = _load("build_gold_signals.py")
        self.assertEqual(gold.data_mode_for("live"), "Live")
        self.assertEqual(gold.data_mode_for("simulated"), "Simulated")
        self.assertEqual(gold.data_mode_for("internal"), "Internal")

    def test_source_dim_row_carries_data_mode(self):
        gold = _load("build_gold_signals.py")
        rec = {"sourceId": "sed", "sourceAuthority": "SED-ETH", "trustTier": "A",
               "provenance": {"activeBinding": "simulated", "fellBackFrom": "live",
                              "ingestedAt": "2026-07-23T00:00:00Z"}}
        row = gold.ext_dim_source_row(rec)
        self.assertEqual(row["ext_data_mode"], "Simulated")
        self.assertEqual(row["ext_fell_back_from"], "live")
        self.assertEqual(row["ext_trust_tier"], "A")
        self.assertEqual(row["ext_source_id"], "sed")

    def test_dims_source_rows_have_data_mode(self):
        gold = _load("build_gold_signals.py")
        recs = [
            {"sourceId": "sed", "sourceAuthority": "SED-ETH", "trustTier": "A",
             "hazardType": "earthquake", "mappedScenarioTemplate": "F1",
             "defaultLageTier": 3, "region": {"cantons": ["VS"]},
             "provenance": {"activeBinding": "live", "fellBackFrom": None,
                            "ingestedAt": "2026-07-23T01:00:00Z"}},
            {"sourceId": "occupancy-breach", "sourceAuthority": "Curavias-internal",
             "trustTier": "A", "hazardType": "capacity-breach",
             "mappedScenarioTemplate": "F5", "defaultLageTier": 1,
             "region": {"cantons": ["ZH"]},
             "provenance": {"activeBinding": "internal", "fellBackFrom": None}},
        ]
        dims = gold.to_gold_dims(recs)
        by_id = {r["ext_source_id"]: r for r in dims["ext_dim_source"]}
        self.assertEqual(by_id["sed"]["ext_data_mode"], "Live")
        self.assertEqual(by_id["sed"]["ext_last_live_at"], "2026-07-23T01:00:00Z")
        self.assertEqual(by_id["occupancy-breach"]["ext_data_mode"], "Internal")


if __name__ == "__main__":
    unittest.main()
