# Paid Simulator Phase 2 Scenario Model Scaffold

## Purpose

This scaffold introduces a separate scenario-model layer for Phase 2 development of the Covered Call Strategy Stress Test.

The current v0.1 dashboard is stable and should not be disturbed while Phase 2 modeling work begins. The new module is therefore add-only:

```text
app\paid_simulator\scenario_model.py
app\run_paid_simulator_scenario_model_check.py
```

## Why this matters

The paid simulator should eventually separate three concerns:

1. User interface and reporting.
2. Covered-call simulation mechanics.
3. Scenario definition and analytics.

The v0.1 dashboard already handles the first concern well. The Phase 2 scenario-model scaffold begins the third concern by centralizing the modeled market paths.

## Initial scenario set

The scaffold defines these paths:

```text
Downtrend
Sideways Choppy
Moderate Uptrend
Strong Rally
Volatile Whipsaw
```

Each scenario has:

```text
scenario_name
display_name
total_return_percent
volatility_label
path_shape
interpretation
```

## Important framing

These are modeled stress-test paths, not forecasts. They are intended to help users understand covered-call tradeoffs:

- Premium can cushion flat, choppy, or declining markets.
- Short calls can create large opportunity cost during strong rallies.
- Volatile paths depend strongly on timing, management rule, and option pricing assumptions.

## Test command

Run this in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_scenario_model_check.py
```

Expected result:

```text
Overall scenario-model status: PASS
```

## Next Phase 2 development step

After the scaffold passes, the next step is to add a controlled path generator that converts scenario definitions into monthly or daily price paths. That should remain separate from the dashboard until it is tested.
