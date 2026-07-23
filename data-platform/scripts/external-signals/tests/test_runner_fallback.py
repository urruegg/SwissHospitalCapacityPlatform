import unittest
from providers.registry import load_manifest
from providers.runner import run_provider
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]


def _spec(source_id):
    return load_manifest(
        SCRIPTS / "providers" / source_id.replace("-", "_") / "provider.yaml"
    )


class TestRunnerFallback(unittest.TestCase):
    def test_live_success_marks_live(self):
        spec = _spec("sed")
        from tests._util import load_fixture
        recs = run_provider(spec, transport=lambda url: load_fixture("sed_quake.json"))
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "live")
        self.assertIsNone(recs[0]["provenance"]["fellBackFrom"])

    def test_live_failure_falls_back_to_simulated(self):
        spec = _spec("sed")
        def boom(url):
            raise TimeoutError("endpoint down")
        recs = run_provider(spec, transport=boom)
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "simulated")
        self.assertEqual(recs[0]["provenance"]["fellBackFrom"], "live")

    def test_simulated_default_marks_simulated(self):
        spec = _spec("bafu")
        recs = run_provider(spec)
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "simulated")

    def test_internal_default_marks_internal(self):
        spec = _spec("occupancy-breach")
        gold = {"fact_bed_state": [
            {"hospital": "USZ", "ward_id": "GER-1", "occupied": 34,
             "capacity": 30, "date": "2026-07-23"}]}
        recs = run_provider(spec, gold=gold)
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "internal")


if __name__ == "__main__":
    unittest.main()
