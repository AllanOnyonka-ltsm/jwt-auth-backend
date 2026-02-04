from policy_sim import (
    HistoricalPolicy,
    PolicyInput,
    SimulationConfig,
    generate_context_warnings,
    generate_pseudo_indicators,
    run_monte_carlo,
)


def main() -> None:
    proposed = PolicyInput(
        name="Growth Package",
        tax_change=-0.01,
        subsidy_change=0.005,
        transfer_change=0.003,
        metadata={"country": "X", "regime": "inflation-targeting", "year": "2024"},
    )

    historical = [
        HistoricalPolicy(
            name="Tax Reform 2012",
            policy=PolicyInput(
                name="Tax Reform 2012",
                tax_change=-0.015,
                subsidy_change=0.0,
                transfer_change=0.001,
                metadata={"country": "X", "regime": "fixed-peg", "year": "2012"},
            ),
            outcomes={"gdp_growth": 0.028, "inflation": 0.045, "poverty_rate": 0.14},
            metadata={"country": "X", "regime": "fixed-peg", "year": "2012"},
        )
    ]

    config = SimulationConfig()
    result = run_monte_carlo(proposed, config, simulations=2000, seed=42)

    print("Summary")
    for key, stats in result.summary.items():
        print(key, stats)

    print("\nMEAL warnings")
    for warning in generate_context_warnings(proposed, historical):
        print("-", warning)

    print("\nPseudo indicators")
    indicators = generate_pseudo_indicators(seed=7)
    for name, series in indicators.items():
        print(name, "->", [round(value, 2) for value in series[:5]], "...")


if __name__ == "__main__":
    main()
