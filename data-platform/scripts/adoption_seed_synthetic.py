"""Generate synthetic Entra sign-in events for the adoption-telemetry pipeline.

Sprint 12 T5 (docs/superpowers/plans/2026-07-09-sprint-12-org-plan.md §5.3).
Produces a 30-day backfill of synthetic sign-in events for the 23 personas so the
Sprint 15 BVA dashboard has data to render before real telemetry accumulates.

The output matches the Bronze adoption contract (design spec §7): one JSON file
per day under ``<output_dir>/adoption/YYYY-MM-DD/signins.json`` with rows shaped
like the Entra ``SignInLogs`` projection. **No PHI** — sign-in metadata carries
UPN + IP only; IPs are synthetic and redacted to a /24.

Deterministic: a fixed seed makes the backfill reproducible for demo evidence.

Usage:
    python3 data-platform/scripts/adoption_seed_synthetic.py \
        --output-dir /tmp/bronze --days 30

Exit 0 on success, 1 on failure.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PERSONAS_CSV = Path("data/synthetic/personas.csv")
APP_DISPLAY_NAME = "ihzhhpf-app"
APP_ID = "11111111-1111-1111-1111-111111111111"  # placeholder; real appId supplied post-deploy
CLIENT_APPS = ["Browser", "Mobile Apps and Desktop clients"]
TRUST_TYPES = ["AzureAD", "ServerAd", "Workplace"]
# Env split follows the shared-user model (design spec §4): the same identity can
# hit either the SIT or PROD slot; SIT dominates during the demo phase.
ENV_WEIGHTS = [("sit", 0.8), ("prod", 0.2)]


def load_personas(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def pick_env(rng: random.Random) -> str:
    roll = rng.random()
    cumulative = 0.0
    for env, weight in ENV_WEIGHTS:
        cumulative += weight
        if roll <= cumulative:
            return env
    return ENV_WEIGHTS[-1][0]


def synth_ip(rng: random.Random) -> str:
    # RFC 5737 documentation range, redacted to a /24 (last octet zeroed).
    return f"203.0.{rng.randint(0, 255)}.0"


def build_events(personas: list[dict[str, str]], days: int, seed: int) -> dict[str, list[dict]]:
    rng = random.Random(seed)
    today = datetime.now(timezone.utc).date()
    by_day: dict[str, list[dict]] = {}
    for day_offset in range(days):
        day = today - timedelta(days=day_offset)
        day_key = day.isoformat()
        rows: list[dict] = []
        for persona in personas:
            # ~2 sign-ins/day per persona (1-3), deterministic per seed.
            for _ in range(rng.randint(1, 3)):
                hour = rng.randint(6, 20)
                minute = rng.randint(0, 59)
                ts = datetime(day.year, day.month, day.day, hour, minute, tzinfo=timezone.utc)
                rows.append(
                    {
                        "userId": f"user-{persona['mail_nickname']}",
                        "upn": persona["upn"],
                        "appDisplayName": APP_DISPLAY_NAME,
                        "appId": APP_ID,
                        "signInTimestamp": ts.isoformat().replace("+00:00", "Z"),
                        "env": pick_env(rng),
                        "resultType": "0" if rng.random() > 0.05 else "50126",
                        "ipAddress": synth_ip(rng),
                        "clientAppUsed": rng.choice(CLIENT_APPS),
                        "deviceDetailTrustType": rng.choice(TRUST_TYPES),
                        "locationCountryOrRegion": "CH",
                        "appRole": persona["app_role"],
                    }
                )
        by_day[day_key] = rows
    return by_day


def write_events(by_day: dict[str, list[dict]], output_dir: Path) -> int:
    total = 0
    for day_key, rows in by_day.items():
        day_dir = output_dir / "adoption" / day_key
        day_dir.mkdir(parents=True, exist_ok=True)
        (day_dir / "signins.json").write_text(
            json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        total += len(rows)
    return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthetic Entra sign-in backfill for adoption telemetry.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Bronze root; files land under <dir>/adoption/YYYY-MM-DD/.")
    parser.add_argument("--personas", type=Path, default=PERSONAS_CSV)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--seed", type=int, default=1712)
    args = parser.parse_args(argv)

    if not args.personas.exists():
        print(f"FAIL: {args.personas} not found")
        return 1
    if args.days < 1:
        print("FAIL: --days must be >= 1")
        return 1

    personas = load_personas(args.personas)
    if not personas:
        print("FAIL: no personas loaded")
        return 1

    by_day = build_events(personas, args.days, args.seed)
    total = write_events(by_day, args.output_dir)
    print(
        f"PASS: wrote {total} synthetic sign-in rows across {len(by_day)} days "
        f"for {len(personas)} personas under {args.output_dir / 'adoption'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
