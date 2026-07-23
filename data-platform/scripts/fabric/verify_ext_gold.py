#!/usr/bin/env python3
"""Verify that the gold ``ext_*`` tables in a Fabric lakehouse are populated
and contain only allowed ``ext_data_mode`` literals.

Usage (SIT)::

    python verify_ext_gold.py --environment SIT

The script connects to the Fabric SQL analytics endpoint via token auth (no
password). Obtain a token with::

    az account get-access-token --resource "https://database.windows.net/" \\
        --query accessToken -o tsv

Manual PowerShell snippet (operator runbook)::

    $token = az account get-access-token --resource "https://database.windows.net/" `
        --query accessToken -o tsv
    $conn = New-Object System.Data.SqlClient.SqlConnection
    $conn.ConnectionString = "Server=pimdoe2bjsuu3d6komn3u6sdfe-gol274ydswje5ghzvea5s3y4q4.datawarehouse.fabric.microsoft.com;Database=lh_ihzhhpf_sit;Encrypt=True;"
    $conn.AccessToken = $token
    $conn.Open()
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "SELECT COUNT(*) FROM gold.ext_fact_signal"
    $cmd.ExecuteScalar()
    $conn.Close()

Notes:
- SIT server:   ``pimdoe2bjsuu3d6komn3u6sdfe-gol274ydswje5ghzvea5s3y4q4.datawarehouse.fabric.microsoft.com``
- SIT database: ``lh_ihzhhpf_sit``
- The SQL-endpoint connection string for any environment is discoverable via
  the Fabric REST API:
  ``GET /v1/workspaces/{workspace_id}/lakehouses/{lakehouse_id}``
  → ``properties.sqlEndpointProperties.connectionString``
  (so PROD is not hard-coded here; load it from environments.yml at runtime).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / "data-platform" / "fabric" / "environments.yml"

EXPECTED_TABLES = (
    "ext_fact_signal",
    "ext_dim_source",
    "ext_dim_hazard_type",
    "ext_dim_region",
)

ALLOWED_MODES = ("Live", "Simulated", "Internal")


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested offline)
# ---------------------------------------------------------------------------

def assert_evidence(counts: dict[str, int], modes: list[str]) -> list[str]:
    """Return a list of findings; empty list means all checks passed."""
    findings: list[str] = []
    for t in EXPECTED_TABLES:
        if t not in counts:
            findings.append(f"missing gold table: gold.{t}")
        elif counts[t] <= 0:
            findings.append(f"empty gold table: gold.{t}")
    for m in modes:
        if m not in ALLOWED_MODES:
            findings.append(f"illegal ext_data_mode literal: {m!r}")
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


def _run_sql(server: str, database: str, token: str, query: str) -> list:  # pragma: no cover
    """Execute *query* via PowerShell + System.Data.SqlClient; return rows."""
    ps_script = f"""
$conn = New-Object System.Data.SqlClient.SqlConnection
$conn.ConnectionString = "Server={server};Database={database};Encrypt=True;"
$conn.AccessToken = '{token}'
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = @'{query}'@
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
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
        capture_output=True, text=True, check=True,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return lines


def query_counts(server: str, database: str, token: str) -> dict[str, int]:  # pragma: no cover
    """Return row counts for each expected ext_* table in gold schema."""
    counts: dict[str, int] = {}
    for table in EXPECTED_TABLES:
        rows = _run_sql(server, database, token, f"SELECT COUNT(*) FROM gold.{table}")
        counts[table] = int(rows[0].strip()) if rows else 0
    return counts


def query_modes(server: str, database: str, token: str) -> list[str]:  # pragma: no cover
    """Return distinct ext_data_mode values from gold.ext_dim_source."""
    rows = _run_sql(
        server, database, token,
        "SELECT DISTINCT ext_data_mode FROM gold.ext_dim_source",
    )
    return [r.strip() for r in rows if r.strip()]


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--environment", default="SIT", choices=["SIT", "PROD"])
    return p.parse_args(argv)


def main(argv=None) -> int:  # pragma: no cover
    ns = parse_args(argv)
    env = load_env(ns.environment)

    server = env.get("sql_endpoint_server") or (
        f"{env['lakehouse_name']}.datawarehouse.fabric.microsoft.com"
    )
    database = env.get("sql_endpoint_database", env["lakehouse_name"])

    print(f"[verify_ext_gold] environment={ns.environment}")
    print(f"[verify_ext_gold] server={server}  database={database}")

    token = get_token()

    counts = query_counts(server, database, token)
    modes = query_modes(server, database, token)

    print("\n--- gold ext_* row counts ---")
    for table, count in counts.items():
        print(f"  gold.{table}: {count} rows")

    print("\n--- distinct ext_data_mode values ---")
    for m in modes:
        print(f"  {m!r}")

    findings = assert_evidence(counts, modes)

    if findings:
        print("\n[FAIL] Evidence findings:")
        for f in findings:
            print(f"  • {f}")
        return 1

    print(f"\n[OK] All {len(EXPECTED_TABLES)} expected tables populated; "
          f"all {len(modes)} mode(s) allowed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
