"""Sprint 16 T6 — seeded-scenario validation + lever cross-reference tests.

Skipped when PyYAML is not importable so local `unittest` stays green without
extra deps; the csa-checks workflow installs pyyaml so these run in CI.
"""
from __future__ import annotations

import unittest

from _util import load_script

try:
    import yaml  # noqa: F401

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


@unittest.skipUnless(_HAS_YAML, "PyYAML not installed")
class TestSeededScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seed = load_script("csa-seed-scenarios.py")
        cls.levers_mod = load_script("csa-seed-response-levers.py")
        cls.scenarios = cls.seed.build_scenarios()
        cls.lever_ids = {lever["leverId"] for lever in cls.levers_mod.build_response_levers()}

    def test_exactly_eight_scenarios(self) -> None:
        self.assertEqual(len(self.scenarios), 8)

    def test_scenarios_validate_against_schema(self) -> None:
        errors = self.seed.validate_all(self.scenarios)
        self.assertEqual(errors, [], msg="\n".join(errors))

    def test_scenario_ids_unique(self) -> None:
        ids = [s["scenarioId"] for s in self.scenarios]
        self.assertEqual(len(ids), len(set(ids)))

    def test_three_mvp_required(self) -> None:
        mvp = [s["scenarioId"] for s in self.scenarios if s.get("mvpRequired")]
        self.assertEqual(len(mvp), 3)
        self.assertIn("cyberattack-hospital-services", mvp)
        self.assertIn("pediatric-virus-surge-rsv", mvp)
        self.assertIn("summer-heatwave-demand-surge", mvp)

    def test_all_referenced_levers_exist(self) -> None:
        for scenario in self.scenarios:
            for lever_id in scenario["responseLevers"]:
                self.assertIn(
                    lever_id,
                    self.lever_ids,
                    msg=f"{scenario['scenarioId']} references unknown lever {lever_id}",
                )

    def test_families_are_f1_to_f8(self) -> None:
        families = sorted(s["family"] for s in self.scenarios)
        self.assertEqual(families, [f"F{i}" for i in range(1, 9)])


if __name__ == "__main__":
    unittest.main()
