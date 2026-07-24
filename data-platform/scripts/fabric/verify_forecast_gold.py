#!/usr/bin/env python3
"""Verify that the WS-A Foresight gold tables in a Fabric lakehouse are
populated and internally consistent.

Usage (SIT)::

    python verify_forecast_gold.py --environment SIT

Connects to the Fabric SQL analytics endpoint via token auth (no password),
mirroring ``verify_ext_gold.py``. Obtain a token with::

    az account get-access-token --resource "https://database.windows.net/" \\
        --query accessToken -o tsv

Checks (Sprint 26 WS-A, issue #335):

- ``gold.fact_occupancy_forecast`` — populated; one row per ward x horizon
  (0..72h) so a single-ward synthetic seed yields 73 rows.
- ``gold.fact_forecast_driver`` — populated; four driver factors per
  forecast-point, i.e. 4x the forecast row count.
- ``gold.fact_signal`` — populated; deny-by-default Trust-A projection, so every
  row must carry ``trust_tier = 'A'``.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / "data-platform" / "fabric" / "environments.yml"

EXPECTED_TABLES = (
    "fact_occupancy_forecast",
    "fact_forecast_driver",
    "fact_signal",
)


# ---------------------------------------------------------------------------
# Pure helpers (unit-testable offline)
# ---------------------------------------------------------------------------

def assert_evidence(counts: dict[str, int], trust_tiers: list[str],
                    driver_factor_count: int) -> list[str]:
    """Return a list of findings; empty list means all checks passed."""
    findings: list[str] = []
    for t in EXPECTED_TABLES:
        if t not in counts:
            findings.append(f"missing gold table: gold.{t}")
        elif counts[t] <= 0:
            findings.append(f"empty gold table: gold.{t}")

    fc = counts.get("fact_occupancy_forecast", 0)
    dc = counts.get("fact_forecast_driver", 0)
    if fc and dc and dc != fc * 4:
        findings.append(
            f"driver rows ({dc}) != 4x forecast rows ({fc}); "
            "decomposition is not one factor-quad per forecast point")
    if fc and driver_factor_count and driver_factor_count != 4:
        findings.append(
            f"expected 4 distinct driver factors, found {driver_factor_count}")

    for tier in trust_tiers:
        if tier != "A":
            findings.append(f"non-Trust-A signal leaked into gold.fact_signal: {tier!r}")
    return findings


# ---------------------------------------------------------------------------
# Live path (subprocess / SQL; all pragma: no cover)
# ---------------------------------------------------------------------------

def load_env(environment: str) -> dict:  # pragma: no cover
    import yaml
    envs = yaml.safe_load(ENV_FILE.read_text(encoding="utf-8"))["environments"]
    if environment not in envs:
        raise SystemExit(f"unknown environment '{environment}'")
    return envs[environment]


def get_token() -> str:  # pragma: no cover
    out = subprocess.run(
        ["az", "account", "get-access-token", "--resource",
         "https://database.windows.net/", "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, check=True, shell=True,
    )
    return out.stdout.strip()


def get_fabric_token() -> str:  # pragma: no cover
    out = subprocess.run(
        ["az", "account", "get-access-token", "--resource",
         "https://api.fabric.microsoft.com", "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, check=True, shell=True,
    )
    return out.stdout.strip()


def resolve_sql_endpoint(env: dict) -> tuple[str, str]:  # pragma: no cover
    if env.get("sql_endpoint_server"):
        return (env["sql_endpoint_server"],
                env.get("sql_endpoint_database", env["lakehouse_name"]))
    import requests
    fabric_token = get_fabric_token()
    url = (f"https://api.fabric.microsoft.com/v1/workspaces/{env['workspace_id']}"
           f"/lakehouses/{env['lakehouse_id']}")
    resp = requests.get(url, headers={"Authorization": f"Bearer {fabric_token}"}, timeout=30)
    resp.raise_for_status()
    server = resp.json()["properties"]["sqlEndpointProperties"]["connectionString"]
    return server, env["lakehouse_name"]


def _run_sql(server: str, database: str, token: str, query: str) -> list:  # pragma: no cover
    ps_script = f"""
$conn = New-Object System.Data.SqlClient.SqlConnection
$conn.ConnectionString = "Server={server};Database={database};Encrypt=True;"
$conn.AccessToken = $env:VERIFY_SQL_TOKEN
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = '{query}'
$reader = $cmd.ExecuteReader()
$rows = @()
while ($reader.Read()) {{
    $row = @()
    for ($i = 0; $i -lt $reader.FieldCount; $i++) {{ $row += $reader.GetValue($i) }}
    $rows += ,$row
}}
$reader.Close()
$conn.Close()
$rows | ForEach-Object {{ $_ -join "`t" }}
"""
    child_env = dict(os.environ)
    child_env["VERIFY_SQL_TOKEN"] = token
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True, text=True, check=True, env=child_env,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"SQL query failed (exit {e.returncode}); check the Fabric SQL endpoint and token."
        ) from None
    return [line for line in result.stdout.splitlines() if line.strip()]


def query_counts(server: str, database: str, token: str) -> dict[str, int]:  # pragma: no cover
    counts: dict[str, int] = {}
    for table in EXPECTED_TABLES:
        rows = _run_sql(server, database, token, f"SELECT COUNT(*) FROM gold.{table}")
        counts[table] = int(rows[0].strip()) if rows else 0
    return counts


def query_trust_tiers(server: str, database: str, token: str) -> list[str]:  # pragma: no cover
    rows = _run_sql(server, database, token,
                    "SELECT DISTINCT trust_tier FROM gold.fact_signal")
    return [r.strip() for r in rows if r.strip()]


def query_driver_factor_count(server: str, database: str, token: str) -> int:  # pragma: no cover
    rows = _run_sql(server, database, token,
                    "SELECT COUNT(DISTINCT factor) FROM gold.fact_forecast_driver")
    return int(rows[0].strip()) if rows else 0


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--environment", default="SIT", choices=["SIT", "PROD"])
    return p.parse_args(argv)


def main(argv=None) -> int:  # pragma: no cover
    ns = parse_args(argv)
    env = load_env(ns.environment)
    server, database = resolve_sql_endpoint(env)

    print(f"[verify_forecast_gold] environment={ns.environment}")
    print(f"[verify_forecast_gold] server={server}  database={database}")

    token = get_token()
    counts = query_counts(server, database, token)
    trust_tiers = query_trust_tiers(server, database, token)
    factor_count = query_driver_factor_count(server, database, token)

    print("\n--- WS-A gold row counts ---")
    for table, count in counts.items():
        print(f"  gold.{table}: {count} rows")
    print("\n--- distinct fact_signal trust_tier values ---")
    for t in trust_tiers:
        print(f"  {t!r}")
    print(f"\n--- distinct driver factors: {factor_count} ---")

    findings = assert_evidence(counts, trust_tiers, factor_count)
    if findings:
        print("\n[FAIL] Evidence findings:")
        for f in findings:
            print(f"  - {f}")
        return 1

    print(f"\n[OK] All {len(EXPECTED_TABLES)} WS-A gold tables populated; "
          "driver decomposition 4x forecast; signal projection Trust-A only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
