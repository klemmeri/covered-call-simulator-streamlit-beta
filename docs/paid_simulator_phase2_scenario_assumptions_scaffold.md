# Phase 2 Scenario-Assumptions Scaffold

This document describes the add-only scenario-assumption layer for the Covered Call Strategy Stress Test paid simulator.

## Purpose

The v0.1 simulator is stable as a local prototype. Phase 2 begins separating model assumptions from the user interface and report layer. The scenario-assumption scaffold provides an explicit, readable table of the assumptions behind each modeled market path.

## Added files

```text
app\paid_simulator\scenario_assumptions.py
app\run_paid_simulator_scenario_assumptions_check.py
docs\paid_simulator_phase2_scenario_assumptions_scaffold.md
```

## Generated output

```text
outputs\tables\paid_simulator\scenario_assumptions_scaffold.csv
```

## Current scenarios

- Downtrend
- Sideways Choppy
- Moderate Uptrend
- Strong Rally
- Volatile Whipsaw

## Fields

Each scenario assumption includes:

- Scenario name
- Display name
- Modeled total return
- Realized-volatility label
- Implied-volatility bias
- Skew bias
- Path shape
- Covered-call profile
- Plain-English interpretation

## Design note

These assumptions are not forecasts. They are scenario inputs used to explore how covered calls behave under different modeled paths.
