# Policy Simulation Sandbox (Prototype)

This repository contains an early-stage prototype for simulating the directional impact of manifesto-style policy inputs (tax changes, subsidies, transfers) on macro outcomes. The system is intended as a learning sandbox, not a policy engine.

## Goals
- Accept policy inputs via Python objects (or JSON equivalents).
- Run simple Monte Carlo simulations under explicit model assumptions.
- Generate pseudo-real-time indicator series for scenario visualization.
- Compare proposed policies to historical references and emit MEAL-style context warnings.
- Offer a lightweight local UI for exploring scenarios.

## Quick Start
### CLI demo
```bash
PYTHONPATH=. python examples/demo.py
```

### Local UI
```bash
python -m policy_sim.server
```
Then open <http://127.0.0.1:8000> in your browser.

## Disclaimer
This prototype uses simplified structural relationships and synthetic shocks. Outputs are illustrative and not suitable for policy decisions.
