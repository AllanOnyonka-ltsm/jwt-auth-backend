import unittest

from policy_sim.models import PolicyInput, SimulationConfig
from policy_sim.simulate import run_monte_carlo


class SimulationTests(unittest.TestCase):
    def test_run_monte_carlo_shapes(self) -> None:
        policy = PolicyInput(
            name="Test",
            tax_change=0.0,
            subsidy_change=0.0,
            transfer_change=0.0,
        )
        config = SimulationConfig()
        result = run_monte_carlo(policy, config, simulations=50, seed=1)

        self.assertEqual(set(result.samples.keys()), {"gdp_growth", "inflation", "poverty_rate"})
        for series in result.samples.values():
            self.assertEqual(len(series), 50)

        for metric in ("gdp_growth", "inflation", "poverty_rate"):
            stats = result.summary[metric]
            for key in ("mean", "p05", "p50", "p95", "min", "max"):
                self.assertIn(key, stats)


if __name__ == "__main__":
    unittest.main()
