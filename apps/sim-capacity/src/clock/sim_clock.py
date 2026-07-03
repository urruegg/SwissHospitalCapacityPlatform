"""Accelerated, deterministic simulator clock.

Design spec: §4.4 — sim time advances at a configurable rate relative to real
time. Randomness is drawn from a seeded ``random.Random`` instance so runs are
reproducible.

Default rate is 60x: 1 real minute = 1 sim hour.
"""

from __future__ import annotations

import random
import time
from datetime import datetime, timedelta
from typing import Optional


class SimClock:
    def __init__(
        self,
        start: datetime,
        rate: float = 60.0,
        seed: Optional[int] = None,
    ) -> None:
        self._start = start
        self._rate = float(rate)
        self._real_start = time.monotonic()
        self._rng = random.Random(seed)

    def now(self) -> datetime:
        """Return current sim time = ``start + (real_elapsed * rate)``."""
        real_elapsed = time.monotonic() - self._real_start
        return self._start + timedelta(seconds=real_elapsed * self._rate)

    def random_uniform(self) -> float:
        """Return a deterministic float in ``[0.0, 1.0)`` from the seeded RNG."""
        return self._rng.random()

    def random_int(self, low: int, high: int) -> int:
        """Return a deterministic integer in ``[low, high]`` (inclusive)."""
        return self._rng.randint(low, high)
