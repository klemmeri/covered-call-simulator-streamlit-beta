# Phase 2B Premium-Model Pipeline Check

This document describes the Phase 2B premium-model pipeline checker.

## Purpose

The Phase 2B pipeline checker validates the new premium-aware modeling layer before it is integrated into the main paid simulator dashboard.

It is intentionally separate from the working v0.1 dashboard.

## Checker script

Run from PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2b_pipeline_check.py
```

Expected result:

```text
Overall Phase 2B pipeline status: PASS
```

## Checks performed

The script runs these checks in sequence:

1. `run_paid_simulator_option_premium_check.py`
2. `run_paid_simulator_premium_aware_payoff_check.py`
3. `run_paid_simulator_premium_vs_scaffold_check.py`
4. `run_paid_simulator_phase2b_premium_viewer_check.py`

It then verifies that the expected Phase 2B output files exist and contain data rows.

## Expected output files

```text
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
outputs\reports\paid_simulator\premium_aware_payoff_scaffold.html
outputs\tables\paid_simulator\premium_vs_scaffold_comparison.csv
outputs\reports\paid_simulator\premium_vs_scaffold_comparison.html
```

## Why this matters

This establishes a clean checkpoint for the premium-aware model layer. The v0.1 dashboard remains stable while Phase 2B modeling realism is developed and tested separately.

## Recommended next step after PASS

After the Phase 2B pipeline check passes, the next safe step is to add a Developer-view-only Phase 2B premium-model tab to the main dashboard.
