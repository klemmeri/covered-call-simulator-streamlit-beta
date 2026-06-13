# Paid Simulator Phase 2B Option-Premium Model Scaffold

## Purpose

This package adds a standalone option-premium model scaffold for the Covered Call Strategy Stress Test project.

The goal is to begin replacing very simple covered-call premium assumptions with a more realistic, inspectable pricing layer.

## Added files

```text
app/paid_simulator/option_premium_model.py
app/run_paid_simulator_option_premium_check.py
docs/paid_simulator_phase2_option_premium_model_scaffold.md
```

## Output

The checker writes:

```text
outputs/tables/paid_simulator/option_premium_scaffold.csv
```

## What the model currently does

The scaffold estimates a call premium using a dependency-free Black-Scholes-style model.

It includes:

- Standard normal CDF approximation using Python's built-in math library
- Black-Scholes call price
- Black-Scholes call delta
- Scenario-level implied-volatility estimates
- Simple call-wing skew adjustment
- Estimated strike for a target call delta
- Scenario-by-scenario CSV output

## Important limitation

This is still a scaffold. It is not a production option-pricing engine.

It does not yet include:

- Live option-chain data
- Full volatility-surface calibration
- Bid/ask spread modeling
- Early assignment modeling
- Dividend-driven exercise risk
- American option pricing
- Real broker execution constraints

## Why this comes next

The project already has a stable v0.1 dashboard and a passing Phase 2 scenario/payoff scaffold. The next modeling improvement is to make the option premium assumptions more defensible before adding the interactive graphical ticker and commercial website layers.
