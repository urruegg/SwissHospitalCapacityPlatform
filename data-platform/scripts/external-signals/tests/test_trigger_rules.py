import unittest
from trigger_rules import load_rules, evaluate, arbitrate


class TestTriggerRules(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules()

    def test_severe_actual_a_triggers(self):
        ev = {"hazardType": "heat", "severity": "Severe", "defaultLageTier": 2,
              "status": "Actual", "trustTier": "A"}
        self.assertTrue(evaluate(ev, self.rules).fired)

    def test_below_threshold_no_trigger(self):
        ev = {"hazardType": "heat", "severity": "Minor", "defaultLageTier": 1,
              "status": "Actual", "trustTier": "A"}
        r = evaluate(ev, self.rules)
        self.assertFalse(r.fired)
        self.assertEqual(r.outcome, "evaluated-no-trigger")

    def test_arbitration_prefers_higher_lage_tier(self):
        events = [{"hazardType": "heat", "severity": "Severe", "defaultLageTier": 2,
                   "mappedScenarioTemplate": "F8"},
                  {"hazardType": "earthquake", "severity": "Severe", "defaultLageTier": 3,
                   "mappedScenarioTemplate": "F1"}]
        primary, secondaries = arbitrate(events)
        self.assertEqual(primary["mappedScenarioTemplate"], "F1")
        self.assertEqual(len(secondaries), 1)


if __name__ == "__main__":
    unittest.main()
