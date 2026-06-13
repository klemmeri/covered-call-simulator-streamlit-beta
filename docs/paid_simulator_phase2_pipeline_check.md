# Paid Simulator Phase 2 Pipeline Check

This document describes the add-only Phase 2 scaffold pipeline checker.

## Purpose

The v0.1 paid simulator dashboard is stable. Phase 2 adds a separate modeling scaffold before any dashboard integration. The pipeline checker verifies that the scaffold modules and their report adapters run in sequence.

## New file

```text
app\run_paid_simulator_phase2_pipeline_check.py
```

## What the checker runs

1. Phase 2 readiness check
2. Scenario model check
3. Scenario price-path check
4. Option-payoff check
5. Scenario-payoff check
6. Scenario-payoff report check
7. Phase 2 vs v0 comparison check

## Expected outputs

```text
outputs\tables\paid_simulator\scenario_price_paths_scaffold.csv
outputs\tables\paid_simulator\option_payoff_scaffold.csv
outputs\tables\paid_simulator\scenario_payoff_scaffold.csv
outputs\tables\paid_simulator\scenario_payoff_report_scaffold.csv
outputs\reports\paid_simulator\scenario_payoff_report_scaffold.html
outputs\tables\paid_simulator\phase2_v0_comparison_scaffold.csv
outputs\reports\paid_simulator\phase2_v0_comparison_scaffold.html
```

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2_pipeline_check.py
```

Expected result:

```text
Overall Phase 2 pipeline status: PASS
```

## Design rule

This checker is add-only and does not modify the dashboard. It is a validation step before deciding whether to integrate Phase 2 scaffold outputs into the Streamlit interface.
