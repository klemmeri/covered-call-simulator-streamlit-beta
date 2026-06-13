# Phase 2D Premium-Model Tuning Viewer

Date: 2026-06-12  
Project: Covered Call Strategy Stress Test  
Phase: 2D — Premium-model assumption tuning

## Purpose

This package adds a standalone Streamlit viewer for the Phase 2D premium-model tuning recommendations.

The viewer is separate from the main paid simulator dashboard. This keeps the stable v0.1 dashboard safe while the premium-model assumptions are still being inspected and tuned.

## Files added

```text
app\paid_simulator\phase2d_premium_tuning_viewer.py
app\run_paid_simulator_phase2d_premium_tuning_viewer.py
app\run_paid_simulator_phase2d_premium_tuning_viewer_check.py
docs\paid_simulator_phase2d_premium_tuning_viewer.md
```

## Inputs read by the viewer

```text
outputs\tables\paid_simulator\premium_model_tuning_recommendations.csv
outputs\reports\paid_simulator\premium_model_tuning_summary.txt
outputs\reports\paid_simulator\premium_model_tuning_recommendations.html
outputs\reports\paid_simulator\phase2d_premium_model_tuning_check_report.txt
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
```

## Viewer tabs

```text
Overview
Tuning recommendations
Validation context
Premium inputs
Payoff context
Files
```

## Installation

Extract the package directly into:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Allow Windows to merge folders.

## Check command

Run this in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2d_premium_tuning_viewer_check.py
```

Expected result:

```text
Overall Phase 2D premium-tuning viewer status: PASS
```

## Open the viewer

Run this in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2d_premium_tuning_viewer.py
```

This opens a standalone browser viewer for the tuning recommendations.

## Notes

A recommendation marked REVIEW, WATCH, or TUNE is not necessarily a software failure. It means the model has flagged an assumption that should be inspected before the premium model becomes more central in the customer-facing workflow.
