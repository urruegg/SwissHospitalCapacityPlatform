import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), HERE / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestAssertEvidence(unittest.TestCase):
    def setUp(self):
        self.m = _load("verify_forecast_gold.py")

    def _full_counts(self, forecast=73):
        return {
            "fact_occupancy_forecast": forecast,
            "fact_forecast_driver": forecast * 4,
            "fact_signal": 4,
        }

    def test_assert_evidence_passes_on_full_set(self):
        findings = self.m.assert_evidence(self._full_counts(), ["A"], 4)
        self.assertEqual(findings, [])

    def test_flags_missing_and_empty(self):
        counts = {"fact_occupancy_forecast": 0, "fact_forecast_driver": 8}
        findings = self.m.assert_evidence(counts, ["A"], 4)
        joined = " ".join(findings)
        self.assertIn("fact_signal", joined)               # missing table
        self.assertIn("fact_occupancy_forecast", joined)   # empty table

    def test_flags_driver_not_four_times_forecast(self):
        counts = {
            "fact_occupancy_forecast": 73,
            "fact_forecast_driver": 100,  # not 4x
            "fact_signal": 4,
        }
        findings = self.m.assert_evidence(counts, ["A"], 4)
        self.assertTrue(any("4x forecast" in f for f in findings))

    def test_flags_wrong_factor_count(self):
        findings = self.m.assert_evidence(self._full_counts(), ["A"], 3)
        self.assertTrue(any("4 distinct driver factors" in f for f in findings))

    def test_flags_non_trust_a_signal(self):
        findings = self.m.assert_evidence(self._full_counts(), ["A", "B"], 4)
        self.assertTrue(any("non-Trust-A" in f for f in findings))


if __name__ == "__main__":
    unittest.main()
