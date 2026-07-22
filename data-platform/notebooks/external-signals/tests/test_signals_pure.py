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


if __name__ == "__main__":
    unittest.main()
