import unittest
from providers.occupancy_breach.internal import read as occ_read
from providers.occupancy_breach.parse import parse as occ_parse
from providers.roster_shortfall.internal import read as ros_read
from providers.roster_shortfall.parse import parse as ros_parse
from providers.supply_stock.internal import read as sup_read
from providers.supply_stock.parse import parse as sup_parse


class TestInternalOccupancy(unittest.TestCase):
    def test_breach_emits_internal_signal(self):
        gold = {"fact_bed_state": [
            {"hospital": "USZ", "ward_id": "GER-1", "occupied": 34,
             "capacity": 30, "date": "2026-07-23"},
            {"hospital": "USZ", "ward_id": "CAR-1", "occupied": 10,
             "capacity": 30, "date": "2026-07-23"},
        ]}
        recs = occ_parse(occ_read(gold))
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["provenance"]["channelKind"], "internal")
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "internal")
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F5")


class TestInternalRoster(unittest.TestCase):
    def test_shortfall_emits_internal_signal(self):
        gold = {"fact_roster": [
            {"hospital": "USZ", "ward_id": "GER-1", "shift": "night",
             "required": 5, "scheduled": 3, "date": "2026-07-23"},
            {"hospital": "USZ", "ward_id": "CAR-1", "shift": "day",
             "required": 4, "scheduled": 4, "date": "2026-07-23"},
        ]}
        recs = ros_parse(ros_read(gold))
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["provenance"]["channelKind"], "internal")
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F5")


class TestInternalSupply(unittest.TestCase):
    def test_low_stock_emits_internal_signal(self):
        gold = {"fact_supply": [
            {"hospital": "USZ", "item": "n95", "on_hand": 10,
             "reorder_point": 50, "date": "2026-07-23"},
            {"hospital": "USZ", "item": "gloves", "on_hand": 900,
             "reorder_point": 200, "date": "2026-07-23"},
        ]}
        recs = sup_parse(sup_read(gold))
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["provenance"]["channelKind"], "internal")
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F5")


if __name__ == "__main__":
    unittest.main()
