# Phase 2C Integration-Readiness Checker

## Purpose

This checker confirms that the Phase 2C premium-model validation layer is installed, runnable, and connected to the Developer-view dashboard path.

It is a safety checkpoint before moving from **validation scaffolding** to **premium-model assumption tuning**.

## Files added

```text
app\run_paid_simulator_phase2c_integration_readiness_check.py
docs\paid_simulator_phase2c_integration_readiness.md
```

## What the checker does

The script runs these checks:

```text
app\run_paid_simulator_phase2c_validation_pipeline_check.py
app\run_paid_simulator_phase2c_dashboard_tab_check.py
```

Then it verifies the key Phase 2C files:

```text
app\paid_simulator\premium_model_validation.py
app\paid_simulator\phase2c_premium_validation_viewer.py
app\run_paid_simulator_phase2c_validation_pipeline_check.py
app\run_paid_simulator_phase2c_dashboard_tab_check.py
config\premium_model_validation_config.json
```

It also verifies Phase 2C outputs:

```text
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
outputs\reports\paid_simulator\premium_model_validation_scaffold.html
outputs\reports\paid_simulator\premium_model_validation_summary.txt
outputs\reports\paid_simulator\phase2c_validation_pipeline_report.txt
```

Finally, it checks that the main dashboard contains the Developer-view tab label:

```text
Phase 2C validation
```

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2c_integration_readiness_check.py
```

Expected final line:

```text
Overall Phase 2C integration-readiness status: PASS
```

## Report output

The checker writes:

```text
outputs\reports\paid_simulator\phase2c_integration_readiness_report.txt
```

## Interpretation

A **PASS** means the Phase 2C validation layer is connected and ready for the next modeling step:

```text
Phase 2C premium-model assumption tuning
```

A **REVIEW** means one or more files, outputs, or dashboard connections need attention before moving on.
