from __future__ import annotations

import random
from typing import Dict, List, Mapping


def _random_walk(
    start: float,
    steps: int,
    drift: float,
    volatility: float,
    rng: random.Random,
) -> List[float]:
    series = [start]
    for _ in range(steps - 1):
        shock = rng.gauss(drift, volatility)
        series.append(series[-1] * (1 + shock))
    return series


def generate_pseudo_indicators(
    steps: int = 24,
    seed: int | None = None,
) -> Mapping[str, List[float]]:
    """Generate synthetic indicator series for sandbox visualization."""

    rng = random.Random(seed)
    return {
        "dollar_index": _random_walk(100.0, steps, drift=0.001, volatility=0.01, rng=rng),
        "commodity_index": _random_walk(95.0, steps, drift=0.0005, volatility=0.02, rng=rng),
        "inflation_proxy": _random_walk(3.0, steps, drift=0.0, volatility=0.005, rng=rng),
    }
