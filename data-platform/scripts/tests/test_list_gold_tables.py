"""Network-free tests for list_gold_tables.parse_table_names."""
import importlib.util
import sys
import unittest
from pathlib import Path

_SCRIPT = (Path(__file__).resolve().parents[1] / "fabric" /
           "list_gold_tables.py")


def _load():
    spec = importlib.util.spec_from_file_location("list_gold_tables", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


lg = _load()


class ParseTests(unittest.TestCase):
    def test_extracts_leaf_names_dirs_only(self):
        payload = {
            "paths": [
                {"name": "lh/Tables/gold/dim_hospital", "isDirectory": "true"},
                {"name": "lh/Tables/gold/or_case", "isDirectory": "true"},
                {"name": "lh/Tables/gold/_delta_log", "isDirectory": "true"},
                {"name": "lh/Tables/gold/readme.txt"},  # file -> skipped
            ]
        }
        self.assertEqual(
            lg.parse_table_names(payload),
            ["_delta_log", "dim_hospital", "or_case"],
        )

    def test_empty(self):
        self.assertEqual(lg.parse_table_names({}), [])

    def test_dedupes_and_sorts(self):
        payload = {"paths": [
            {"name": "lh/Tables/gold/b", "isDirectory": True},
            {"name": "lh/Tables/gold/a", "isDirectory": True},
            {"name": "lh/Tables/gold/a", "isDirectory": True},
        ]}
        self.assertEqual(lg.parse_table_names(payload), ["a", "b"])


if __name__ == "__main__":
    unittest.main()
