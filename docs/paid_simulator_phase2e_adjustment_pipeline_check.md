# Phase 2E Adjustment Pipeline Check

This package adds an end-to-end checker for the Phase 2E controlled premium-model adjustment workflow.

## Added file

```text
app\run_paid_simulator_phase2e_adjustment_pipeline_check.py
```

## Purpose

The checker runs the Phase 2E workflow in sequence and verifies that the adjusted-premium and adjusted-payoff outputs exist and contain data.

It does not modify the customer dashboard and does not overwrite the original premium-model scaffold output.

## Script steps

The checker runs:

```text
app\run_paid_simulator_phase2d_checkpoint_check.py        optional context check
app\run_paid_simulator_premium_model_adjustment_check.py
app\run_paid_simulator_adjusted_premium_payoff_comparison_check.py
app\run_paid_simulator_phase2e_adjustment_viewer_check.py
```

## Expected outputs

The checker verifies:

```text
config\premium_model_adjustment_config.json
outputs\tables\paid_simulator\premium_model_adjusted_premiums.csv
outputs\reports\paid_simulator\premium_model_adjustment_comparison.html
outputs\reports\paid_simulator\premium_model_adjustment_summary.txt
outputs\tables\paid_simulator\adjusted_premium_payoff_comparison.csv
outputs\reports\paid_simulator\adjusted_premium_payoff_comparison.html
outputs\reports\paid_simulator\adjusted_premium_payoff_summary.txt
outputs\reports\paid_simulator\phase2e_premium_model_adjustment_check_report.txt
outputs\reports\paid_simulator\phase2e_adjusted_premium_payoff_comparison_check_report.txt
outputs\reports\paid_simulator\phase2e_adjustment_viewer_check_report.txt
```

The checker writes:

```text
outputs\reports\paid_simulator\phase2e_adjustment_pipeline_report.txt
```

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2e_adjustment_pipeline_check.py
```

Expected final line:

```text
Overall Phase 2E adjustment pipeline status: PASS
```

## Notes

This is a pipeline-safety layer. It confirms that the Phase 2E adjustment workflow is connected before the adjustment output is added to the main Developer-view dashboard.
