"""Sprint 16 T5 — pure-function tests for the CSA shock model + simulate()."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

NB_DIR = Path(__file__).resolve().parents[1]
if str(NB_DIR) not in sys.path:
    sys.path.insert(0, str(NB_DIR))

import shock_model  # noqa: E402


def _load_simulate():
    path = NB_DIR / "csa-simulate.py"
    spec = importlib.util.spec_from_file_location("csa_simulate", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestShockModel(unittest.TestCase):
    def test_demand_surge_percent_bumps_occupancy(self) -> None:
        baseline = {"beds": {"capacity": 100, "occupied": 80}}
        shock = {
            "shockVector": "demand-surge",
            "affectedResources": ["beds"],
            "magnitude": {"unit": "percent", "value": 25},
        }
        out = shock_model.apply_shock(baseline, shock)
        self.assertEqual(out["beds"]["occupied"], 100)
        self.assertEqual(out["beds"]["capacity"], 100)

    def test_capacity_loss_reduces_capacity(self) -> None:
        baseline = {"icu-beds": {"capacity": 20, "occupied": 18}}
        shock = {
            "shockVector": "capacity-loss",
            "affectedResources": ["icu-beds"],
            "magnitude": {"unit": "percent", "value": 30},
        }
        out = shock_model.apply_shock(baseline, shock)
        self.assertEqual(out["icu-beds"]["capacity"], 14)

    def test_project_state_reports_utilization_and_shortfall(self) -> None:
        baseline = {"pediatric-beds": {"capacity": 40, "occupied": 30}}
        shock = {
            "shockVector": "demand-surge",
            "affectedResources": ["pediatric-beds"],
            "magnitude": {"unit": "percent", "value": 50},
        }
        state = shock_model.project_state(baseline, shock)
        dim = state["resources"]["pediatric-beds"]
        self.assertAlmostEqual(dim["utilization"], 1.125, places=3)
        self.assertEqual(dim["shortfall"], 5)


class TestSimulateGolden(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_simulate()

    def test_rsv_surge_canonical_is_tier2_with_kpi_band(self) -> None:
        baseline = {"pediatric-beds": {"capacity": 40, "occupied": 30}}
        scenario = {
            "scenarioId": "rsv-surge",
            "shockVector": "demand-surge",
            "affectedResources": ["pediatric-beds"],
            "magnitude": {"unit": "percent", "value": 50},
        }
        run = self.mod.simulate(baseline, scenario, run_id="run-rsv-1", requested_by="crisis.manager")
        self.assertEqual(run["tier"], 2)
        # KPI band: a modest pediatric bed shortfall, single dimension over threshold.
        self.assertGreaterEqual(run["kpis"]["totalShortfall"], 3)
        self.assertLessEqual(run["kpis"]["totalShortfall"], 8)
        self.assertEqual(run["kpis"]["resourcesOverThreshold"], 1)
        self.assertEqual(run["status"], "succeeded")
        self.assertEqual(run["resultRef"], "DC-SIM-RESULT/run-rsv-1")

    def test_cyberattack_capacity_loss_escalates_to_tier3(self) -> None:
        baseline = {"icu-beds": {"capacity": 20, "occupied": 18}}
        scenario = {
            "scenarioId": "cyberattack-hospital-services",
            "shockVector": "capacity-loss",
            "affectedResources": ["icu-beds"],
            "magnitude": {"unit": "percent", "value": 30},
        }
        run = self.mod.simulate(baseline, scenario, run_id="run-cyber-1", requested_by="crisis.manager")
        self.assertEqual(run["tier"], 3)
        self.assertTrue(run["result"]["tierReasons"])

    def test_run_document_has_rules_version(self) -> None:
        baseline = {"beds": {"capacity": 100, "occupied": 50}}
        scenario = {
            "scenarioId": "quiet",
            "shockVector": "demand-surge",
            "affectedResources": ["beds"],
            "magnitude": {"unit": "percent", "value": 5},
        }
        run = self.mod.simulate(baseline, scenario, run_id="run-quiet-1", requested_by="ops.lead")
        self.assertEqual(run["tier"], 1)
        self.assertIn("rulesVersion", run["result"])


if __name__ == "__main__":
    unittest.main()
