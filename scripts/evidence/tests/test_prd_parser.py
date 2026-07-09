import unittest

from scripts.evidence.parsers.prd_parser import parse_prd
from scripts.evidence.tests._helpers import (
    FIXED_COMMIT,
    FIXTURE_REPO,
    REPO_ROOT,
    assert_provenance,
    assert_valid,
)


class TestPrdParser(unittest.TestCase):
    def test_fixture_rows_valid_and_provenanced(self):
        rows = parse_prd(FIXTURE_REPO / "docs" / "PRD.md", source_commit=FIXED_COMMIT)
        self.assertEqual([r["id"] for r in rows], ["FR-DATA-001", "FR-OM-001", "FR-OM-002", "NFR-COMP-001"])
        assert_valid(rows, "requirements")
        assert_provenance(rows, keys=("sourcePath", "sourceCommit", "sourceLine"))

    def test_family_and_kind_captured(self):
        rows = parse_prd(FIXTURE_REPO / "docs" / "PRD.md", source_commit=FIXED_COMMIT)
        by_id = {r["id"]: r for r in rows}
        self.assertEqual(by_id["FR-OM-001"]["family"], "Operating Model And Product Scope")
        self.assertEqual(by_id["FR-OM-001"]["kind"], "FR")
        self.assertEqual(by_id["NFR-COMP-001"]["kind"], "NFR")

    def test_mvp_flag_detected_from_title(self):
        rows = parse_prd(FIXTURE_REPO / "docs" / "PRD.md", source_commit=FIXED_COMMIT)
        by_id = {r["id"]: r for r in rows}
        self.assertTrue(by_id["FR-OM-002"]["mvp"])
        self.assertFalse(by_id["FR-OM-001"]["mvp"])

    def test_byte_stable(self):
        prd = FIXTURE_REPO / "docs" / "PRD.md"
        self.assertEqual(
            parse_prd(prd, source_commit=FIXED_COMMIT),
            parse_prd(prd, source_commit=FIXED_COMMIT),
        )

    def test_real_prd_parses(self):
        rows = parse_prd(REPO_ROOT / "docs" / "PRD.md", source_commit=FIXED_COMMIT)
        assert_valid(rows, "requirements")
        self.assertGreater(len(rows), 50)
        self.assertTrue(any(r["kind"] == "NFR" for r in rows))


if __name__ == "__main__":
    unittest.main()
