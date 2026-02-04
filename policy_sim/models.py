from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Sequence


@dataclass(frozen=True)
class PolicyInput:
    """Policy inputs expressed as shares of GDP or percentage points."""

    name: str
    tax_change: float
    subsidy_change: float
    transfer_change: float
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class HistoricalPolicy:
    """Historical policy episode with observed outcomes."""

    name: str
    policy: PolicyInput
    outcomes: Mapping[str, float]
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SimulationConfig:
    """Configurable structural parameters for the toy model."""

    baseline_gdp_growth: float = 0.02
    baseline_inflation: float = 0.03
    baseline_poverty_rate: float = 0.15
    fiscal_multiplier: float = 0.9
    inflation_sensitivity: float = 0.4
    poverty_elasticity: float = -0.6
    transfer_poverty_effect: float = -0.3
    shock_std_gdp: float = 0.01
    shock_std_inflation: float = 0.008
    shock_correlation: float = 0.35


@dataclass(frozen=True)
class SimulationResult:
    """Outputs of a Monte Carlo simulation."""

    samples: Mapping[str, Sequence[float]]
    summary: Mapping[str, Dict[str, float]]
    config: SimulationConfig
    policy: PolicyInput
    notes: List[str] = field(default_factory=list)
