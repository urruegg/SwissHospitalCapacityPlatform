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
                "05_gold_org_skills",
                "04_load_or_samples",
                "00_seed_eventstream_raw",
                "01_bronze_eventstream",
                "02_silver_eventstream",
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
        body = rm.build_definition("QkFTRTY0", "UExBVA==")
        parts = body["definition"]["parts"]
        self.assertEqual(body["definition"]["format"], "ipynb")
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0]["path"], "notebook-content.ipynb")
        self.assertEqual(parts[0]["payload"], "QkFTRTY0")
        self.assertEqual(parts[0]["payloadType"], "InlineBase64")
        self.assertEqual(parts[1]["path"], ".platform")
        self.assertEqual(parts[1]["payload"], "UExBVA==")

    def test_create_body_includes_display_name(self):
        body = rm.build_create_body("01_bronze_master_data", "QQ==", "Ug==")
        self.assertEqual(body["displayName"], "01_bronze_master_data")
        self.assertIn("definition", body)

    def test_inject_lakehouse_binds_default(self):
        raw = b'{"cells": [], "metadata": {"language_info": {"name": "python"}}}'
        out = rm.inject_lakehouse(raw, "lh-id", "lh_name", "ws-id")
        import json as _j
        dep = _j.loads(out)["metadata"]["dependencies"]["lakehouse"]
        self.assertEqual(dep["default_lakehouse"], "lh-id")
        self.assertEqual(dep["default_lakehouse_name"], "lh_name")
        self.assertEqual(dep["default_lakehouse_workspace_id"], "ws-id")

    def test_platform_part_has_display_name(self):
        import json as _j
        p = _j.loads(rm.build_platform_part("03_gold_master_data", "x/y.ipynb"))
        self.assertEqual(p["metadata"]["displayName"], "03_gold_master_data")
        self.assertEqual(p["metadata"]["type"], "Notebook")

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
