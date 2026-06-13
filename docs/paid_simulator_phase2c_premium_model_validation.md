# Phase 2C Premium-Model Validation Scaffold

Date: 2026-06-12

## Purpose

This package adds a validation layer for the Phase 2B premium model.

The Phase 2B model estimates covered-call premiums using a simplified Black-Scholes-style approach. Phase 2C begins the process of checking whether those premium estimates are internally reasonable before they are moved closer to the customer-facing workflow.

This is still a scaffold. It is not live option-chain pricing.

## Files added

```text
app\paid_simulator\premium_model_validation.py
app\run_paid_simulator_premium_model_validation_check.py
docs\paid_simulator_phase2c_premium_model_validation.md
```

The first time the checker runs, it also creates this editable validation config if it does not already exist:

```text
config\premium_model_validation_config.json
```

## Inputs

```text
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
```

The second file is not deeply analyzed yet, but it is part of the Phase 2B premium-aware modeling chain and will be used more heavily in later validation steps.

## Outputs

```text
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
outputs\reports\paid_simulator\premium_model_validation_scaffold.html
outputs\reports\paid_simulator\premium_model_validation_summary.txt
```

## What it checks

The validation layer checks:

```text
Premium is positive
Premium as percent of underlying is inside a broad reasonableness band
Estimated implied volatility is inside a broad reasonableness band
Estimated call delta is close to the target delta
Estimated strike is above the current underlying price
Strike moneyness is not extreme for the current scaffold
Basic scenario relationships make sense
```

Examples of scenario relationship checks:

```text
Volatile Whipsaw IV should exceed Strong Rally IV
Downtrend IV should exceed Sideways Choppy IV
Sideways premium should not be implausibly low relative to Strong Rally premium
```

## How to run

In PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_premium_model_validation_check.py
```

Expected installation result:

```text
Overall Phase 2C premium-model validation status: PASS
```

Important: The checker can pass even if the validation report contains WATCH or REVIEW rows. That means the validation machinery works and has found a modeling assumption worth inspecting. It is not necessarily an installation failure.

## Why this matters

Before replacing the old simple payoff scaffold with the premium-aware model, the premium model needs a diagnostic layer. This package provides that layer.

The workflow becomes:

```text
Option-premium model
   ↓
Premium-aware payoff
   ↓
Premium-vs-old comparison
   ↓
Premium-model validation
   ↓
Assumption tuning
```

## Next likely step

After this passes, the next step is to add a Phase 2C assumption-tuning report that makes specific recommendations for adjusting the validation config, volatility mapping, skew mapping, and target-delta behavior.
