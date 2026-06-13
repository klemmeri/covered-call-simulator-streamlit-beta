# Phase 2D Premium-Model Tuning Pipeline Check

This package adds a pipeline checker for the Phase 2D premium-model tuning layer.

## Added files

```text
app\run_paid_simulator_phase2d_tuning_pipeline_check.py
docs\paid_simulator_phase2d_tuning_pipeline_check.md
```

## Purpose

The checker verifies that the Phase 2D tuning workflow can run end-to-end before the tuning results are connected to the main dashboard.

It runs:

```text
Phase 2C checkpoint check, if present
Phase 2D premium-model tuning check
Phase 2D premium-tuning viewer check
```

It verifies these outputs:

```text
config\premium_model_tuning_config.json
outputs\tables\paid_simulator\premium_model_tuning_recommendations.csv
outputs\reports\paid_simulator\premium_model_tuning_recommendations.html
outputs\reports\paid_simulator\premium_model_tuning_summary.txt
outputs\reports\paid_simulator\phase2d_premium_model_tuning_check_report.txt
```

It also confirms that the upstream premium, validation, and payoff CSV files are still present.

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2d_tuning_pipeline_check.py
```

Expected result:

```text
Overall Phase 2D tuning pipeline status: PASS
```

## Note

A tuning recommendation marked `REVIEW` or `TUNE` is not necessarily a software failure. It means the model has identified an assumption that should be inspected before the premium model is promoted further.
