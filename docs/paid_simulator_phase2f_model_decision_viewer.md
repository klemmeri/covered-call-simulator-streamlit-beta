# Phase 2F Model-Decision Viewer

This package adds a standalone Streamlit viewer for the Phase 2F model-decision summary.

## Purpose

The viewer lets the developer inspect the consolidated model-decision evidence in the browser before adding it to the main dashboard.

It is intentionally separate from the customer-facing dashboard.

## Files added

```text
app\paid_simulator\phase2f_model_decision_viewer.py
app\run_paid_simulator_phase2f_model_decision_viewer.py
app\run_paid_simulator_phase2f_model_decision_viewer_check.py
docs\paid_simulator_phase2f_model_decision_viewer.md
```

## Inputs read

```text
outputs\tables\paid_simulator\model_decision_summary.csv
outputs\reports\paid_simulator\model_decision_summary.html
outputs\reports\paid_simulator\model_decision_summary.txt
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
outputs\tables\paid_simulator\premium_model_tuning_recommendations.csv
outputs\tables\paid_simulator\premium_model_adjusted_premiums.csv
outputs\tables\paid_simulator\adjusted_premium_payoff_comparison.csv
```

## Viewer tabs

```text
Overview
Model decisions
Promotion candidates
Evidence context
Files and reports
Notes
```

## How to check installation

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2f_model_decision_viewer_check.py
```

Expected result:

```text
Overall Phase 2F model-decision viewer status: PASS
```

## How to open the viewer

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2f_model_decision_viewer.py
```

## Notes

This package is add-only. It does not replace the main dashboard and does not promote any model automatically.

The next step after this passes is a Phase 2F model-decision pipeline checker.
