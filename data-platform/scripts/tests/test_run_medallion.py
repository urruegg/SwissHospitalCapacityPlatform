"""Unit tests for the pure (network-free) parts of run_medallion.py.

The live Fabric REST calls (create/update/run/poll) are deploy-class and are
not exercised here; only payload construction, ordering, and arg-parsing are
tested, so this module imports cleanly without ``requests`` installed (the BVA
generator self-test discovers this directory without that dependency).
"""
import base64
import importlib.util
import sys
import unittest
from pathlib import Path

_SCRIPT = (Path(__file__).resolve().parents[1] / "fabric" / "run_medallion.py")


def _load():
    spec = importlib.util.spec_from_file_location("run_medallion", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclass hint resolution needs this
    spec.loader.exec_module(mod)
    return mod


rm = _load()


class OrderingTests(unittest.TestCase):
    def test_medallion_order_is_dependency_correct(self):
        names = [n.display_name for n in rm.ordered_notebooks()]
        self.assertEqual(
            names,
            [
                "01_bronze_master_data",
                "02_silver_master_data",
                "03_gold_master_data",
                "04_load_or_samples",
                "03_gold_eventstream",
            ],
        )

    def test_every_notebook_path_exists(self):
        for nb in rm.ordered_notebooks():
            self.assertTrue(nb.path.exists(), f"missing {nb.path}")


class PayloadTests(unittest.TestCase):
    def test_ipynb_to_base64_roundtrips(self):
        raw = b'{"cells": [], "metadata": {}}'
        b64 = rm.ipynb_to_base64(raw)
        self.assertEqual(base64.b64decode(b64), raw)

    def test_definition_body_shape(self):
        body = rm.build_definition("QkFTRTY0")
        parts = body["definition"]["parts"]
        self.assertEqual(body["definition"]["format"], "ipynb")
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0]["path"], "notebook-content.ipynb")
        self.assertEqual(parts[0]["payload"], "QkFTRTY0")
        self.assertEqual(parts[0]["payloadType"], "InlineBase64")

    def test_create_body_includes_display_name(self):
        body = rm.build_create_body("01_bronze_master_data", "QQ==")
        self.assertEqual(body["displayName"], "01_bronze_master_data")
        self.assertIn("definition", body)

    def test_run_config_binds_default_lakehouse(self):
        cfg = rm.build_run_config("lh_ihzhhpf_sit", "lh-id", "ws-id")
        dl = cfg["executionData"]["configuration"]["defaultLakehouse"]
        self.assertEqual(dl["name"], "lh_ihzhhpf_sit")
        self.assertEqual(dl["id"], "lh-id")
        self.assertEqual(dl["workspaceId"], "ws-id")


class ArgTests(unittest.TestCase):
    def test_requires_environment(self):
        with self.assertRaises(SystemExit):
            rm.parse_args([])

    def test_parses_sit(self):
        ns = rm.parse_args(["--environment", "SIT"])
        self.assertEqual(ns.environment, "SIT")
        self.assertFalse(ns.apply)  # plan-first: apply is opt-in

    def test_apply_flag(self):
        ns = rm.parse_args(["--environment", "PROD", "--apply"])
        self.assertTrue(ns.apply)


if __name__ == "__main__":
    unittest.main()
