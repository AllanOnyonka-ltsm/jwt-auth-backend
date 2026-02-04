from __future__ import annotations

import math
import random
from typing import Dict, List

from .models import PolicyInput, SimulationConfig, SimulationResult


def _correlated_shocks(
    rng: random.Random,
    std_x: float,
    std_y: float,
    rho: float,
) -> tuple[float, float]:
    """Generate two correlated Gaussian shocks using Cholesky decomposition."""

    z1 = rng.gauss(0.0, 1.0)
    z2 = rng.gauss(0.0, 1.0)
    x = std_x * z1
    y = std_y * (rho * z1 + math.sqrt(max(0.0, 1 - rho**2)) * z2)
    return x, y


def _summarize(samples: List[float]) -> Dict[str, float]:
    ordered = sorted(samples)
    n = len(ordered)
    mean = sum(ordered) / n
    return {
        "mean": mean,
        "p05": ordered[int(0.05 * (n - 1))],
        "p50": ordered[int(0.50 * (n - 1))],
        "p95": ordered[int(0.95 * (n - 1))],
        "min": ordered[0],
        "max": ordered[-1],
    }


def run_monte_carlo(
    policy: PolicyInput,
    config: SimulationConfig,
    simulations: int = 5_000,
    seed: int | None = None,
) -> SimulationResult:
    rng = random.Random(seed)

    gdp_growth_samples: List[float] = []
    inflation_samples: List[float] = []
    poverty_samples: List[float] = []

    net_fiscal = policy.transfer_change + policy.subsidy_change - policy.tax_change

    for _ in range(simulations):
        gdp_shock, inflation_shock = _correlated_shocks(
            rng,
            std_x=config.shock_std_gdp,
            std_y=config.shock_std_inflation,
            rho=config.shock_correlation,
        )

        gdp_growth = (
            config.baseline_gdp_growth
            + config.fiscal_multiplier * net_fiscal
            + gdp_shock
        )
        inflation = (
            config.baseline_inflation
            + config.inflation_sensitivity * gdp_growth
            + inflation_shock
        )
        poverty_rate = (
            config.baseline_poverty_rate
            + config.poverty_elasticity * gdp_growth
            + config.transfer_poverty_effect * policy.transfer_change
        )

        gdp_growth_samples.append(gdp_growth)
        inflation_samples.append(inflation)
        poverty_samples.append(poverty_rate)

    summary = {
        "gdp_growth": _summarize(gdp_growth_samples),
        "inflation": _summarize(inflation_samples),
        "poverty_rate": _summarize(poverty_samples),
    }

    notes = [
        "Toy structural model; results depend on explicit multipliers.",
        "Shocks are Gaussian with fixed correlation; tail risks are understated.",
    ]

    return SimulationResult(
        samples={
            "gdp_growth": gdp_growth_samples,
            "inflation": inflation_samples,
            "poverty_rate": poverty_samples,
        },
        summary=summary,
        config=config,
        policy=policy,
        notes=notes,
    )
