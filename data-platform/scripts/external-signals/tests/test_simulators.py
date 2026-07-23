import importlib
import unittest
from providers.registry import discover


class TestSimulators(unittest.TestCase):
    def test_every_external_provider_has_deterministic_simulator(self):
        for spec in discover():
            if spec.channel_kind != "external":
                continue
            sim = importlib.import_module(f"providers.{spec.source_id}.simulator")
            a = sim.generate(seed=1)
            b = sim.generate(seed=1)
            self.assertEqual(a, b, f"{spec.source_id} simulator not deterministic")

    def test_simulated_payload_parses_to_valid_records(self):
        import json
        from pathlib import Path
        scripts = Path(__file__).resolve().parents[1]
        schema = json.loads(
            (scripts / "providers" / "_schema" / "provider.schema.json").read_text()
        )
        self.assertTrue(schema)
        for spec in discover():
            if spec.channel_kind != "external":
                continue
            sim = importlib.import_module(f"providers.{spec.source_id}.simulator")
            parse = importlib.import_module(f"providers.{spec.source_id}.parse").parse
            recs = parse(sim.generate(seed=2), active_binding="simulated")
            self.assertTrue(recs)
            self.assertEqual(recs[0]["provenance"]["activeBinding"], "simulated")


if __name__ == "__main__":
    unittest.main()
