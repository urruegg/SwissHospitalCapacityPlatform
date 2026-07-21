import unittest
from tests._util import load_fixture
from connectors.meteoswiss import MeteoSwissConnector
from connectors.sed import SedConnector
from connectors.alertswiss import AlertswissConnector
from connectors.bag import BagConnector


class TestConnectors(unittest.TestCase):
    def test_meteoswiss_maps_heat_to_f8(self):
        recs = MeteoSwissConnector().parse(load_fixture("meteoswiss_heat.json"))
        self.assertEqual(recs[0]["hazardType"], "heat")
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F8")
        self.assertEqual(recs[0]["trustTier"], "A")

    def test_sed_maps_quake_severity_from_magnitude(self):
        recs = SedConnector().parse(load_fixture("sed_quake.json"))
        self.assertEqual(recs[0]["hazardType"], "earthquake")
        self.assertIn(recs[0]["severity"], {"Severe", "Extreme"})

    def test_alertswiss_preserves_cap_identifier(self):
        recs = AlertswissConnector().parse(load_fixture("alertswiss_cap.json"))
        self.assertTrue(recs[0]["capIdentifier"])

    def test_bag_maps_rsv_to_f6(self):
        recs = BagConnector().parse(load_fixture("bag_rsv.json"))
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F6")

    def test_every_record_is_schema_valid(self):
        from tests.test_schema_conformance import SCHEMA  # reuse path
        import json
        doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
        req = set(doc["properties"]["records"]["items"]["required"])
        for conn, fx in [(MeteoSwissConnector(), "meteoswiss_heat.json"),
                         (SedConnector(), "sed_quake.json"),
                         (AlertswissConnector(), "alertswiss_cap.json"),
                         (BagConnector(), "bag_rsv.json")]:
            for rec in conn.parse(load_fixture(fx)):
                self.assertTrue(req <= set(rec), f"{conn} missing {req - set(rec)}")


if __name__ == "__main__":
    unittest.main()
