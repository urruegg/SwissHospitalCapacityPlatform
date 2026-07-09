import unittest

from scripts.evidence.parsers.bom_parser import parse_bom
from scripts.evidence.tests._helpers import (
    FIXED_COMMIT,
    FIXTURE_REPO,
    REPO_ROOT,
    assert_provenance,
    assert_valid,
)


class TestBomParser(unittest.TestCase):
    def setUp(self):
        self.bom_rows, self.dep_rows = parse_bom(
            FIXTURE_REPO / "docs" / "bom.yaml", source_commit=FIXED_COMMIT
        )

    def test_rows_valid_and_provenanced(self):
        assert_valid(self.bom_rows, "bom")
        assert_valid(self.dep_rows, "dependencies")
        assert_provenance(self.bom_rows)
        assert_provenance(self.dep_rows)

    def test_items_and_edges(self):
        self.assertEqual([r["id"] for r in self.bom_rows], ["bom-sample-capacity", "bom-sample-lakehouse"])
        self.assertEqual(self.dep_rows[0]["fromId"], "bom-sample-lakehouse")
        self.assertEqual(self.dep_rows[0]["toId"], "bom-sample-capacity")
        self.assertEqual(self.dep_rows[0]["type"], "hosts")

    def test_real_bom_has_25_items(self):
        bom_rows, dep_rows = parse_bom(REPO_ROOT / "docs" / "bom.yaml", source_commit=FIXED_COMMIT)
        assert_valid(bom_rows, "bom")
        assert_valid(dep_rows, "dependencies")
        self.assertGreaterEqual(len(bom_rows), 25)

    def test_dependency_targets_exist(self):
        bom_rows, dep_rows = parse_bom(REPO_ROOT / "docs" / "bom.yaml", source_commit=FIXED_COMMIT)
        ids = {r["id"] for r in bom_rows}
        for edge in dep_rows:
            self.assertIn(edge["fromId"], ids)
            self.assertIn(edge["toId"], ids, f"dangling dependency target {edge['toId']}")


if __name__ == "__main__":
    unittest.main()
