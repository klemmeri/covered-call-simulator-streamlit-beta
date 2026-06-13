# Phase 2C Validation Pipeline Check

## Purpose

This package adds a conservative end-to-end checker for the Phase 2C premium-model validation layer.

It does not replace the main dashboard and does not change the customer-facing workflow.

## Added files

```text
app\run_paid_simulator_phase2c_validation_pipeline_check.py
docs\paid_simulator_phase2c_validation_pipeline_check.md
```

## What the checker runs

The checker runs these scripts when they are available:

```text
app\run_paid_simulator_phase2b_pipeline_check.py
app\run_paid_simulator_premium_model_validation_check.py
app\run_paid_simulator_phase2c_premium_validation_viewer_check.py
```

The Phase 2B pipeline check is treated as optional because some development checkpoints may already have generated the Phase 2B outputs before the Phase 2C check is run. The Phase 2C validation and viewer checks are required.

## Expected outputs

The checker verifies that these files exist and contain data:

```text
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
outputs\reports\paid_simulator\premium_model_validation_scaffold.html
outputs\reports\paid_simulator\premium_model_validation_summary.txt
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
```

It also writes a checkpoint report:

```text
outputs\reports\paid_simulator\phase2c_validation_pipeline_report.txt
```

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2c_validation_pipeline_check.py
```

Expected final line:

```text
Overall Phase 2C validation pipeline status: PASS
```

## Interpretation

A PASS means the Phase 2C validation workflow is installed, runnable, and producing the expected validation files.

A PASS does not mean the premium model assumptions are final. It means the framework is ready for model tuning.
