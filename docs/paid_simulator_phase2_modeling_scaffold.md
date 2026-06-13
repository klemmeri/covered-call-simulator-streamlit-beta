# Phase 2 Modeling Scaffold

## Purpose

This document defines the next technical phase for the paid simulator: improve the scenario and option-modeling layer without disturbing the working Streamlit dashboard.

## Initial modeling scaffold goals

The initial scaffold should provide a place to define market paths and option assumptions independently from the user interface.

The scaffold should support:

- Named scenarios
- Scenario descriptions
- Underlying price path assumptions
- Implied-volatility assumptions
- Option-premium assumptions
- Covered-call behavior notes
- Buy-and-hold comparison notes

## Initial scenario set

The current five-path scenario set should be preserved:

1. Downtrend
2. Sideways / choppy
3. Volatile range
4. Moderate uptrend
5. Strong rally

## Modeling caution

Scenario names are not forecasts. They are controlled stress-test paths used to help the user understand covered-call tradeoffs.

## Next implementation target

Create an add-only Python module:

app/paid_simulator/scenario_model.py

The module should expose:

- get_default_scenarios()
- validate_scenarios()
- summarize_scenarios()

The checker script should verify that all scenarios have required fields and that at least five scenarios are available.
