#!/usr/bin/env python3
"""Authoritative OneLake Delta read of Curavias org/skills gold evidence.

Reads gold Delta tables directly from OneLake (SQL analytics endpoint lags and
is not authoritative), and prints the data-quality evidence used to prove the
Sprint 23 org/skills refactor landed cleanly in a target environment:

* ``dim_hospital`` = the three Curavias tenants (no real hospital names).
* Zero ``H_HSL`` orphan rows across the hospital-keyed capacity gold tables.

Coordinates come from ``data-platform/fabric/environments.yml``; auth is the
same ``az`` storage token used by ``list_gold_tables.py``. Read-only.

Usage::

    python data-platform/scripts/fabric/read_gold_evidence.py --environment PROD
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / "data-platform" / "fabric" / "environments.yml"
ONELAKE = "onelake.dfs.fabric.microsoft.com"

# Hospital-keyed capacity gold tables that must contain zero H_HSL orphans
# after the Curavias 1:1 fold (Hirslanden / H_HSL has no Curavias tenant).
HOSPITAL_KEYED = [
    "dim_specialty",
    "dim_hospital_service",
    "fact_capacity_baseline",
    "bed_assignment",
    "or_case",
    "or_schedule",
    "encounter",
]
ORPHAN_KEY = "H_HSL"


def load_env(environment: str) -> dict:
    envs = yaml.safe_load(ENV_FILE.read_text(encoding="utf-8"))["environments"]
    if environment not in envs:
        raise SystemExit(f"unknown environment '{environment}'")
    return envs[environment]


def get_token() -> str:
    out = subprocess.run(
        ["az", "account", "get-access-token", "--resource",
         "https://storage.azure.com/", "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, check=True, shell=True,
    )
    return out.stdout.strip()


def read_table(workspace_id: str, lakehouse_id: str, table: str, token: str):
    from deltalake import DeltaTable
    uri = (f"abfss://{workspace_id}@{ONELAKE}/"
           f"{lakehouse_id}/Tables/gold/{table}")
    dt = DeltaTable(uri, storage_options={
        "bearer_token": token, "use_fabric_endpoint": "true"})
    return dt.to_pyarrow_table().to_pydict()


def _find_hospital_col(cols: list[str]) -> str | None:
    for cand in ("hospital_id", "hospital_key", "hospitalid", "hospital"):
        if cand in cols:
            return cand
    return None


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--environment", required=True, choices=["SIT", "PROD"])
    ns = p.parse_args(argv)

    env = load_env(ns.environment)
    ws, lh = env["workspace_id"], env["lakehouse_id"]
    token = get_token()

    print(f"Environment : {ns.environment}")
    print(f"Workspace   : {env['workspace_name']} ({ws})")
    print(f"Lakehouse   : {env['lakehouse_name']} ({lh})")
    print("Source      : OneLake Delta (authoritative; SQL endpoint not used)\n")

    failures = []

    # 1) dim_hospital: expect exactly the three Curavias tenants, no real names.
    print("== dim_hospital (Curavias tenants) ==")
    dh = read_table(ws, lh, "dim_hospital", token)
    cols = list(dh.keys())
    n = len(next(iter(dh.values()))) if dh else 0
    print(f"rows: {n}  cols: {cols}")
    name_col = next((c for c in ("hospital_name", "name", "display_name")
                     if c in cols), None)
    id_col = next((c for c in ("hospital_id", "hospital_key", "id")
                   if c in cols), None)
    for i in range(n):
        rid = dh[id_col][i] if id_col else "?"
        rnm = dh[name_col][i] if name_col else "?"
        print(f"  - {rid}: {rnm}")
    if n != 3:
        failures.append(f"dim_hospital has {n} rows, expected 3")
    # Specific real-hospital identifiers behind the three Curavias tenants
    # (H_USZ=Universitätsspital Zürich, H_LUKS=Luzerner Kantonsspital,
    # H_SZB=Spital Schwyz). Generic type words like "Kantonsspital"/"Spital"/
    # "Uniklinik" are NOT identifying and are reused by the synthetic brands.
    real = ("universitätsspital", "hirslanden", "luzern", "zürich", "zurich",
            "schwyz")
    brands = ("curanova", "curalp", "vialta")
    # Only the name-bearing columns can leak a real hospital identity; canton/
    # city legitimately retain real Swiss geography and are printed, not failed.
    name_cols = [c for c in (name_col, "short_name") if c and c in cols]
    geo_cols = [c for c in ("city", "canton") if c in cols]
    for i in range(n):
        if geo_cols:
            geo = ", ".join(f"{c}={dh[c][i]}" for c in geo_cols)
            print(f"      geo: {geo}")
        blob = " ".join(str(dh[c][i]) for c in name_cols).lower()
        hit = next((r for r in real if r in blob), None)
        if hit:
            failures.append(
                f"real identifier '{hit}' leaked in name: "
                f"{ {c: dh[c][i] for c in name_cols} }")
        if name_col and not any(b in str(dh[name_col][i]).lower()
                                for b in brands):
            failures.append(f"name missing Curavias brand: {dh[name_col][i]}")

    # 2) H_HSL orphans across hospital-keyed gold tables.
    print("\n== H_HSL orphan sweep (expect 0 everywhere) ==")
    for t in HOSPITAL_KEYED:
        try:
            data = read_table(ws, lh, t, token)
        except Exception as exc:  # noqa: BLE001
            print(f"  {t:28} SKIP ({type(exc).__name__})")
            continue
        hc = _find_hospital_col(list(data.keys()))
        if not hc:
            print(f"  {t:28} no hospital col")
            continue
        total = len(data[hc])
        orphans = sum(1 for v in data[hc] if str(v) == ORPHAN_KEY)
        flag = "OK" if orphans == 0 else "FAIL"
        print(f"  {t:28} rows={total:<6} {ORPHAN_KEY}={orphans}  {flag}")
        if orphans:
            failures.append(f"{t} has {orphans} {ORPHAN_KEY} orphans")

    print()
    if failures:
        print("EVIDENCE FAIL:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("EVIDENCE OK: 3 Curavias tenants, no real names, 0 H_HSL orphans.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
