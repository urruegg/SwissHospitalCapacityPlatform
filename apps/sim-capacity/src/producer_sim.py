"""Streaming producer entrypoint for sim-capacity.

Loops over simulated time in 1-hour chunks, runs all 6 generators for each of
the 3 hospital presets (USZ / LUKS / SZB by default), and publishes envelopes
to Azure Event Hubs via Managed Identity auth.

Runs both locally (auth via `az login`) and in ACA (auth via user-assigned MI
selected by `AZURE_CLIENT_ID` env var).

Env vars:
- `EVENT_HUB_NAMESPACE` — namespace name (short name; `.servicebus.windows.net` is appended)
- `EVENT_HUB_NAME` — hub entity name
- `AZURE_CLIENT_ID` — optional; selects a specific UAMI when present
- `DEMO_SCOPE` — 'true' | 'false' (informational; tagged on the run summary)

CLI:
- `--hospitals USZ,LUKS,SZB`  hospitals to simulate (default: all three)
- `--rate 60`                  wall-clock seconds per simulated hour (default 60 = 60x accel)
- `--seed 42`                  RNG seed (deterministic per hospital)
- `--duration-hours 24`        simulated hours to emit; 0 = loop forever until Ctrl-C
- `--start-utc 2027-01-15T00:00:00`  simulated start time (default: now UTC)
- `--dry-run`                  print envelope counts instead of sending
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

_REPO_SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(_REPO_SRC))

from calibration.acuity_distribution import build_acuity_sampler
from calibration.hospital_presets import load_preset
from calibration.seasonal_profile import SeasonalProfile
from calibration.ward_topology import load_ward_topology
from emitters.eventhub_emitter import EventHubEmitter
from generators.bed_state_generator import generate_bed_states
from generators.discharge_recommender import generate_discharge_recommendations
from generators.discharge_scorer import generate_discharge_scores
from generators.encounter_generator import generate_encounters
from generators.forecast_generator import generate_forecasts
from generators.matching_engine import generate_bed_assignments

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("producer_sim")


def _hospital_state(hospital_short: str, seed: int) -> dict:
    """Load per-hospital calibration and helpers."""
    preset = load_preset(hospital_short)
    return {
        "short": hospital_short,
        "preset": preset,
        "profile": SeasonalProfile.from_preset(preset, seed=seed),
        "sampler": build_acuity_sampler(hospital_short, seed=seed),
        "wards": load_ward_topology(hospital_short),
    }


def _emit_hour(
    hospital: dict,
    sim_run_id: str,
    seed: int,
    hour_start: datetime,
    emitter: EventHubEmitter | None,
    dry_run: bool,
) -> int:
    preset = hospital["preset"]
    profile = hospital["profile"]
    sampler = hospital["sampler"]
    wards = hospital["wards"]

    encounters = list(generate_encounters(
        preset=preset, profile=profile, sampler=sampler,
        sim_run_id=sim_run_id, seed=seed,
        start_time=hour_start, duration_hours=1,
    ))
    bed_states = list(generate_bed_states(
        preset=preset, sim_run_id=sim_run_id, seed=seed,
        start_time=hour_start, duration_hours=1, ward_topology=wards,
    ))
    bed_assignments = list(generate_bed_assignments(
        preset=preset, encounter_events=encounters,
        sim_run_id=sim_run_id, seed=seed, ward_topology=wards,
    ))
    forecasts = list(generate_forecasts(
        preset=preset, profile=profile,
        sim_run_id=sim_run_id, seed=seed,
        start_time=hour_start, duration_hours=1, ward_topology=wards,
    ))
    scored = list(generate_discharge_scores(
        preset=preset, encounter_events=encounters,
        sim_run_id=sim_run_id, seed=seed,
        start_time=hour_start, duration_hours=1,
    ))
    recommendations = list(generate_discharge_recommendations(
        preset=preset, scored_events=scored,
        sim_run_id=sim_run_id, seed=seed,
    ))

    envelopes: List[dict] = [
        *encounters,
        *bed_states,
        *bed_assignments,
        *forecasts,
        *scored,
        *recommendations,
    ]

    logger.info(
        "%s @ %s — %d envelopes (E=%d BS=%d BA=%d F=%d SC=%d R=%d)",
        hospital["short"],
        hour_start.isoformat(timespec="minutes"),
        len(envelopes),
        len(encounters), len(bed_states), len(bed_assignments),
        len(forecasts), len(scored), len(recommendations),
    )

    if dry_run or emitter is None:
        return len(envelopes)

    return emitter.send_many(envelopes)


def _build_emitter(fqns: str, hub_name: str) -> EventHubEmitter:
    from azure.identity import DefaultAzureCredential
    from azure.eventhub import EventHubProducerClient

    client_id = os.environ.get("AZURE_CLIENT_ID")
    credential = DefaultAzureCredential(managed_identity_client_id=client_id) if client_id \
        else DefaultAzureCredential()

    def _factory() -> EventHubProducerClient:
        return EventHubProducerClient(
            fully_qualified_namespace=fqns,
            eventhub_name=hub_name,
            credential=credential,
        )

    return EventHubEmitter(
        fully_qualified_namespace=fqns,
        eventhub_name=hub_name,
        credential=credential,
        producer_client_factory=_factory,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Sim-capacity streaming producer")
    parser.add_argument("--hospitals", default="USZ,LUKS,SZB",
                        help="Comma-separated short names (default: USZ,LUKS,SZB).")
    parser.add_argument("--rate", type=float, default=60.0,
                        help="Wall-clock seconds per simulated hour (default 60).")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed.")
    parser.add_argument("--duration-hours", type=int, default=0,
                        help="Simulated hours to run; 0 = forever until Ctrl-C.")
    parser.add_argument("--start-utc", default=None,
                        help="Sim start (ISO 8601 UTC). Default: now.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print envelope counts; do not send.")
    args = parser.parse_args()

    hospitals_short = [h.strip() for h in args.hospitals.split(",") if h.strip()]
    hospitals = [_hospital_state(h, args.seed) for h in hospitals_short]
    sim_run_id = f"run-{uuid.uuid4().hex[:12]}"

    start_utc = (
        datetime.fromisoformat(args.start_utc.replace("Z", "").replace("+00:00", ""))
        if args.start_utc
        else datetime.now(timezone.utc).replace(tzinfo=None)
    )

    ns_env = os.environ.get("EVENT_HUB_NAMESPACE", "")
    fqns = ns_env if ns_env.endswith(".servicebus.windows.net") else f"{ns_env}.servicebus.windows.net"
    hub_name = os.environ.get("EVENT_HUB_NAME", "")
    demo_scope = os.environ.get("DEMO_SCOPE", "false")

    if not args.dry_run and (not ns_env or not hub_name):
        logger.error("EVENT_HUB_NAMESPACE and EVENT_HUB_NAME must be set (or use --dry-run).")
        return 2

    emitter = None if args.dry_run else _build_emitter(fqns, hub_name)

    logger.info(
        "sim_run_id=%s hospitals=%s start=%s rate=%s s/hr duration_hours=%d dry_run=%s demo_scope=%s",
        sim_run_id, hospitals_short, start_utc.isoformat(), args.rate,
        args.duration_hours, args.dry_run, demo_scope,
    )
    if not args.dry_run:
        logger.info("Emitting to EventHubs: fqns=%s hub=%s", fqns, hub_name)

    hour_index = 0
    total_envelopes = 0
    try:
        while args.duration_hours == 0 or hour_index < args.duration_hours:
            hour_start = start_utc.replace(minute=0, second=0, microsecond=0)
            from datetime import timedelta
            hour_start = hour_start + timedelta(hours=hour_index)

            for hospital in hospitals:
                total_envelopes += _emit_hour(
                    hospital=hospital,
                    sim_run_id=sim_run_id,
                    seed=args.seed + hour_index,
                    hour_start=hour_start,
                    emitter=emitter,
                    dry_run=args.dry_run,
                )

            hour_index += 1
            if args.duration_hours == 0 or hour_index < args.duration_hours:
                if args.rate > 0:
                    logger.debug("Sleeping %.1fs before next sim-hour...", args.rate)
                    time.sleep(args.rate)
    except KeyboardInterrupt:
        logger.info("Interrupted after %d sim-hours, %d envelopes total.", hour_index, total_envelopes)
        return 0

    logger.info("Completed %d sim-hours, %d envelopes total.", hour_index, total_envelopes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
