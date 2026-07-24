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
        self.m = _load("verify_ext_gold.py")

    def test_assert_evidence_passes_on_full_set(self):
        counts = {t: 3 for t in self.m.EXPECTED_TABLES}
        findings = self.m.assert_evidence(counts, ["Live", "Simulated", "Internal"])
        self.assertEqual(findings, [])

    def test_assert_evidence_flags_missing_and_empty_and_bad_mode(self):
        counts = {"ext_fact_signal": 0, "ext_dim_source": 5, "ext_dim_hazard_type": 2}
        findings = self.m.assert_evidence(counts, ["Live", "Bogus"])
        joined = " ".join(findings)
        self.assertIn("ext_dim_region", joined)     # missing table
        self.assertIn("ext_fact_signal", joined)     # empty table
        self.assertIn("Bogus", joined)               # illegal data mode


if __name__ == "__main__":
    unittest.main()
