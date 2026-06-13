# Phase 2G Model-Promotion Pipeline Check

## Purpose

This add-only package adds an end-to-end pipeline checker for Phase 2G controlled model-promotion planning.

The checker confirms that the Phase 2G planning layer can run after the Phase 2F checkpoint and that the Phase 2G viewer can read the resulting outputs.

This does not promote any model into the customer dashboard. It remains an internal Developer-view workflow.

## Added file

```text
app\run_paid_simulator_phase2g_model_promotion_pipeline_check.py
```

## Documentation file

```text
docs\paid_simulator_phase2g_model_promotion_pipeline_check.md
```

## What the checker runs

```text
Phase 2F checkpoint check
Phase 2G model-promotion planning check
Phase 2G model-promotion viewer check
```

## Expected output files

```text
outputs\tables\paid_simulator\model_promotion_plan.csv
outputs\reports\paid_simulator\model_promotion_plan.html
outputs\reports\paid_simulator\model_promotion_plan.txt
outputs\reports\paid_simulator\phase2g_model_promotion_planning_check_report.txt
outputs\reports\paid_simulator\phase2g_model_promotion_viewer_check_report.txt
outputs\reports\paid_simulator\phase2g_model_promotion_pipeline_report.txt
```

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2g_model_promotion_pipeline_check.py
```

Expected result:

```text
Overall Phase 2G model-promotion pipeline status: PASS
```

## Notes

A REVIEW result usually means one of the prerequisite checks returned a non-zero exit code or an expected output file was missing. The pipeline report prints the tail of stdout/stderr from any failed prerequisite script to help identify the source.
