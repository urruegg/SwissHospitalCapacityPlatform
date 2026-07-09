import unittest

from scripts.evidence.parsers.adr_parser import parse_adrs
from scripts.evidence.tests._helpers import (
    FIXED_COMMIT,
    FIXTURE_REPO,
    REPO_ROOT,
    assert_provenance,
    assert_valid,
)


class TestAdrParser(unittest.TestCase):
    def setUp(self):
        self.adr_rows, self.map_rows = parse_adrs(
            FIXTURE_REPO / "docs" / "adr", source_commit=FIXED_COMMIT
        )

    def test_rows_valid_and_provenanced(self):
        assert_valid(self.adr_rows, "adrs")
        assert_valid(self.map_rows, "req_adr_map")
        assert_provenance(self.adr_rows)
        assert_provenance(self.map_rows)

    def test_bullet_and_table_status_parsed(self):
        by_id = {r["id"]: r for r in self.adr_rows}
        self.assertEqual(by_id["ADR-0001"]["status"], "Accepted")
        self.assertEqual(by_id["ADR-0002"]["status"], "Superseded")
        self.assertEqual(by_id["ADR-0002"]["supersededBy"], ["ADR-0001"])

    def test_decision_summary_extracted(self):
        by_id = {r["id"]: r for r in self.adr_rows}
        self.assertIn("accept the sample decision", by_id["ADR-0001"]["decisionSummary"])

    def test_req_adr_edges(self):
        edges = {(r["requirementId"], r["adrId"]) for r in self.map_rows}
        self.assertIn(("FR-OM-001", "ADR-0001"), edges)
        self.assertIn(("FR-DATA-001", "ADR-0002"), edges)

    def test_real_adrs_parse(self):
        adr_rows, map_rows = parse_adrs(REPO_ROOT / "docs" / "adr", source_commit=FIXED_COMMIT)
        assert_valid(adr_rows, "adrs")
        assert_valid(map_rows, "req_adr_map")
        self.assertGreaterEqual(len(adr_rows), 10)


if __name__ == "__main__":
    unittest.main()
