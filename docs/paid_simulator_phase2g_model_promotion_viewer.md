# Phase 2G Model-Promotion Viewer

This add-only package adds a standalone Streamlit viewer for the Phase 2G controlled model-promotion planning layer.

## Added files

```text
app\paid_simulator\phase2g_model_promotion_viewer.py
app\run_paid_simulator_phase2g_model_promotion_viewer.py
app\run_paid_simulator_phase2g_model_promotion_viewer_check.py
docs\paid_simulator_phase2g_model_promotion_viewer.md
```

## Purpose

The viewer lets the developer inspect the Phase 2G promotion plan before any model is promoted into a customer-facing workflow.

It is intentionally separate from the main dashboard and does not change customer behavior.

## Main inputs

```text
outputs\tables\paid_simulator\model_promotion_plan.csv
outputs\reports\paid_simulator\model_promotion_plan.html
outputs\reports\paid_simulator\model_promotion_plan.txt
outputs\tables\paid_simulator\model_decision_summary.csv
outputs\tables\paid_simulator\adjusted_premium_payoff_comparison.csv
outputs\tables\paid_simulator\premium_model_tuning_recommendations.csv
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
outputs\tables\paid_simulator\option_premium_scaffold.csv
```

## Viewer tabs

```text
Overview
Promotion plan
Promotion candidates
Evidence context
Files and reports
Notes
```

## Check script

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2g_model_promotion_viewer_check.py
```

Expected result:

```text
Overall Phase 2G model-promotion viewer status: PASS
```

## Launch script

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2g_model_promotion_viewer.py
```

## Notes

Phase 2G remains internal-only. A promotion candidate is not automatically promoted. Customer-facing promotion should require a separate checkpoint and explicit decision.
