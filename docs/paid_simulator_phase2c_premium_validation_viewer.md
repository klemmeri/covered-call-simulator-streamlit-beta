# Phase 2C Premium Validation Viewer

Date: 2026-06-11  
Project: Covered Call Strategy Stress Test  
Milestone: Phase 2C premium-model validation

## Purpose

This package adds a standalone Streamlit viewer for the Phase 2C premium-model validation outputs.

The viewer is intentionally separate from the main paid simulator dashboard. It gives the developer a safe place to inspect validation results before the premium model is promoted into the customer-facing workflow.

## Files added

```text
app\paid_simulator\phase2c_premium_validation_viewer.py
app\run_paid_simulator_phase2c_premium_validation_viewer.py
app\run_paid_simulator_phase2c_premium_validation_viewer_check.py
docs\paid_simulator_phase2c_premium_validation_viewer.md
```

## Inputs read

```text
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
outputs\reports\paid_simulator\premium_model_validation_scaffold.html
outputs\reports\paid_simulator\premium_model_validation_summary.txt
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
outputs\tables\paid_simulator\premium_vs_scaffold_comparison.csv
```

## Viewer tabs

```text
Overview
Validation checks
Option premiums
Premium-aware payoffs
Notes
```

## Installation

Extract this package directly into:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Allow Windows to merge folders.

## Test

Run this file in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2c_premium_validation_viewer_check.py
```

Expected result:

```text
Overall Phase 2C premium-validation viewer status: PASS
```

## Open the viewer

Run this file in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2c_premium_validation_viewer.py
```

## Interpretation

A PASS result means the viewer is installed and the expected Phase 2C validation outputs are available.

A WATCH or REVIEW inside the validation report does not necessarily mean the app is broken. It means the premium model has an assumption that should be inspected before the model is treated as customer-ready.

## Next step after this passes

After this viewer passes, the next safe step is to add a Phase 2C validation pipeline checker, then optionally add a Developer-view-only Phase 2C validation tab to the main dashboard.
