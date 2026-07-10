#!/usr/bin/env python3
"""Unit tests for the adoption-telemetry Bronze transforms (Sprint 12 · T5).

Dependency-free. Validates that the raw ``SigninLogs`` projection maps to the
Bronze adoption contract that the synthetic backfill emits and the Sprint 15 BVA
medallion consumes. Also asserts the produced rows are accepted by the real
downstream consumer ``bva_transforms.adoption_index_from_signins``.

Run with::

    python3 -m unittest discover -s data-platform/notebooks/adoption/tests
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(HERE)
BVA_DIR = os.path.abspath(os.path.join(MODULE_DIR, "..", "bva"))
sys.path.insert(0, MODULE_DIR)
sys.path.insert(0, BVA_DIR)

import adoption_transforms as A  # noqa: E402
import bva_transforms as T  # noqa: E402


def _raw(**overrides):
    row = {
        "TimeGenerated": "2026-06-15T08:12:00Z",
        "UserId": "user-markus.frei",
        "UserPrincipalName": "markus.frei@x",
        "AppDisplayName": "ihzhhpf-app",
        "AppId": "1",
        "ResultType": "0",
        "IPAddress": "203.0.1.37",
        "ClientAppUsed": "Browser",
        "DeviceDetail_TrustType": "AzureAD",
        "Location_CountryOrRegion": "CH",
    }
    row.update(overrides)
    return row


PERSONA_ROLE = {
    "markus.frei@x": "HCC.BedManager",
    "tom.roth@x": "HCC.DischargeCoordinator",
}


class ContractShapeTests(unittest.TestCase):
    def test_row_has_exactly_the_contract_fields(self):
        row = A.signin_to_bronze_row(_raw(), PERSONA_ROLE)
        self.assertEqual(tuple(row.keys()), A.BRONZE_CONTRACT_FIELDS)

    def test_contract_matches_synthetic_backfill_keys(self):
        # The synthetic backfill fixture is the authoritative Bronze shape.
        fixture_keys = {
            "userId", "upn", "appDisplayName", "appId", "signInTimestamp",
            "env", "resultType", "ipAddress", "clientAppUsed",
            "deviceDetailTrustType", "locationCountryOrRegion", "appRole",
        }
        self.assertEqual(set(A.BRONZE_CONTRACT_FIELDS), fixture_keys)


class FieldMappingTests(unittest.TestCase):
    def test_ip_redacted_to_24(self):
        row = A.signin_to_bronze_row(_raw(IPAddress="203.0.1.37"), PERSONA_ROLE)
        self.assertEqual(row["ipAddress"], "203.0.1.0")

    def test_ipv6_passthrough(self):
        row = A.signin_to_bronze_row(_raw(IPAddress="2001:db8::1"), PERSONA_ROLE)
        self.assertEqual(row["ipAddress"], "2001:db8::1")

    def test_timestamp_offset_normalised_to_z(self):
        row = A.signin_to_bronze_row(_raw(TimeGenerated="2026-06-15T08:12:00+00:00"))
        self.assertEqual(row["signInTimestamp"], "2026-06-15T08:12:00Z")

    def test_app_role_joined_from_persona_map(self):
        row = A.signin_to_bronze_row(_raw(), PERSONA_ROLE)
        self.assertEqual(row["appRole"], "HCC.BedManager")

    def test_unknown_user_gets_null_role(self):
        row = A.signin_to_bronze_row(_raw(UserPrincipalName="stranger@x"), PERSONA_ROLE)
        self.assertIsNone(row["appRole"])

    def test_env_defaults_to_sit(self):
        self.assertEqual(A.signin_to_bronze_row(_raw())["env"], "sit")

    def test_env_prod_from_suffix(self):
        row = A.signin_to_bronze_row(_raw(AppDisplayName="ihzhhpf-app-prod"))
        self.assertEqual(row["env"], "prod")

    def test_result_type_stringified(self):
        row = A.signin_to_bronze_row(_raw(ResultType=50126))
        self.assertEqual(row["resultType"], "50126")


class GroupingTests(unittest.TestCase):
    def test_group_by_signin_day(self):
        rows = A.to_bronze_rows(
            [
                _raw(TimeGenerated="2026-06-15T08:12:00Z"),
                _raw(TimeGenerated="2026-06-15T22:00:00Z"),
                _raw(TimeGenerated="2026-06-16T09:00:00Z"),
            ],
            PERSONA_ROLE,
        )
        by_day = A.group_by_signin_day(rows)
        self.assertEqual(sorted(by_day), ["2026-06-15", "2026-06-16"])
        self.assertEqual(len(by_day["2026-06-15"]), 2)


class DownstreamConsumerTests(unittest.TestCase):
    """The Bronze rows must be directly consumable by the BVA adoption join."""

    def test_rows_feed_adoption_index(self):
        rows = A.to_bronze_rows(
            [
                _raw(UserPrincipalName="markus.frei@x"),
                _raw(UserPrincipalName="tom.roth@x"),
                _raw(UserPrincipalName="markus.frei@x", ResultType="50126"),
            ],
            PERSONA_ROLE,
        )
        index = T.adoption_index_from_signins(
            rows, persona_hospital={"markus.frei@x": "USZ", "tom.roth@x": "LUKS"}
        )
        # markus (BMCA/USZ) counted once; failed sign-in ignored; tom -> DCA/LUKS.
        self.assertEqual(index[("BMCA", "2026-06", "USZ")], 1)
        self.assertEqual(index[("DCA", "2026-06", "LUKS")], 1)


if __name__ == "__main__":
    unittest.main()
