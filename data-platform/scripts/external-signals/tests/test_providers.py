import unittest
from tests._util import load_fixture
from providers.sed.parse import parse as sed_parse
from providers.meteoswiss.parse import parse as meteo_parse
from providers.alertswiss.parse import parse as alert_parse
from providers.bag.parse import parse as bag_parse


class TestSedProvider(unittest.TestCase):
    def test_sed_maps_quake_and_stamps_channel_kind(self):
        recs = sed_parse(load_fixture("sed_quake.json"))
        self.assertEqual(recs[0]["hazardType"], "earthquake")
        self.assertIn(recs[0]["severity"], {"Severe", "Extreme"})
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F1")
        self.assertEqual(recs[0]["provenance"]["channelKind"], "external")


class TestExternalProviders(unittest.TestCase):
    def test_meteoswiss_heat_f8(self):
        recs = meteo_parse(load_fixture("meteoswiss_heat.json"))
        self.assertEqual(recs[0]["hazardType"], "heat")
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F8")

    def test_alertswiss_preserves_cap_identifier(self):
        recs = alert_parse(load_fixture("alertswiss_cap.json"))
        self.assertTrue(recs[0]["capIdentifier"])

    def test_bag_rsv_f6(self):
        recs = bag_parse(load_fixture("bag_rsv.json"))
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F6")


class TestLiveBindings(unittest.TestCase):
    def test_sed_live_uses_injected_transport(self):
        from providers.sed.live import LiveBinding
        sample = load_fixture("sed_quake.json")
        binding = LiveBinding(endpoint="https://example.invalid")
        raw = binding.poll(transport=lambda url: sample)
        self.assertEqual(raw, sample)

    def test_alertswiss_live_uses_injected_transport(self):
        from providers.alertswiss.live import LiveBinding
        sample = load_fixture("alertswiss_cap.json")
        binding = LiveBinding(endpoint="https://example.invalid")
        raw = binding.poll(transport=lambda url: sample)
        self.assertEqual(raw, sample)


if __name__ == "__main__":
    unittest.main()
