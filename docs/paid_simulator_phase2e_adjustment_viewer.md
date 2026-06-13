# Phase 2E Premium Adjustment Viewer

## Purpose

This package adds a standalone browser viewer for the Phase 2E controlled premium-model adjustment outputs.

The viewer is intentionally separate from the main paid simulator dashboard. It allows developer-side inspection of adjusted premium estimates and adjusted payoff comparisons before any adjusted model is promoted into the customer-facing workflow.

## Added files

```text
app\paid_simulator\phase2e_adjustment_viewer.py
app\run_paid_simulator_phase2e_adjustment_viewer.py
app\run_paid_simulator_phase2e_adjustment_viewer_check.py
docs\paid_simulator_phase2e_adjustment_viewer.md
```

## Inputs read by the viewer

```text
outputs\tables\paid_simulator\premium_model_adjusted_premiums.csv
outputs\reports\paid_simulator\premium_model_adjustment_summary.txt
outputs\tables\paid_simulator\adjusted_premium_payoff_comparison.csv
outputs\reports\paid_simulator\adjusted_premium_payoff_summary.txt
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
outputs\tables\paid_simulator\premium_model_tuning_recommendations.csv
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
```

## Related HTML reports

```text
outputs\reports\paid_simulator\premium_model_adjustment_comparison.html
outputs\reports\paid_simulator\adjusted_premium_payoff_comparison.html
```

## Viewer tabs

```text
Overview
Adjusted premiums
Adjusted payoff comparison
Original context
Files and reports
Notes
```

## How to test

Run this script in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2e_adjustment_viewer_check.py
```

Expected result:

```text
Overall Phase 2E adjustment-viewer status: PASS
```

## How to open the viewer

Run this script in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2e_adjustment_viewer.py
```

## Design note

This viewer is read-only. It does not overwrite the original premium model, the adjusted premium output, or the main dashboard. It exists to inspect whether the Phase 2E tuning adjustment materially changes premium estimates and payoff results.
