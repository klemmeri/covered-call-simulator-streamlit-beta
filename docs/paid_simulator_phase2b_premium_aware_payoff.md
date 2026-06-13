# Phase 2B Premium-Aware Payoff Scaffold

This add-only scaffold connects the Phase 2B option-premium output to a more realistic scenario-level covered-call payoff calculation.

## New files

```text
app\paid_simulator\premium_aware_payoff_runner.py
app\run_paid_simulator_premium_aware_payoff_check.py
docs\paid_simulator_phase2b_premium_aware_payoff.md
```

## Inputs

```text
outputs\tables\paid_simulator\scenario_price_paths_scaffold.csv
outputs\tables\paid_simulator\option_premium_scaffold.csv
```

## Outputs

```text
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
outputs\reports\paid_simulator\premium_aware_payoff_scaffold.html
```

## Purpose

The earlier payoff scaffold used simple heuristics. This adapter uses the option-premium scaffold's estimated call strike and premium, then calculates:

- buy-and-hold P/L
- covered-call P/L
- covered-call minus buy-and-hold
- premium income
- intrinsic call loss
- assignment flag
- scenario interpretation

## Important limitation

This is still a scaffold. It does not yet include live option-chain data, bid/ask spreads, dividends, taxes, early assignment probabilities, or full volatility-surface modeling.
