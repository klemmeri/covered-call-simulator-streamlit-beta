# Phase 2D Premium-Model Tuning Integration Readiness

This checkpoint verifies that the Phase 2D premium-model tuning layer is installed and connected.

## Purpose

Phase 2D adds a tuning layer above the premium-model validation system. Its purpose is not to change the customer-facing simulator yet. Its purpose is to inspect the premium-model outputs and produce recommendations for improving the option-premium assumptions before they become central to the product.

The integration-readiness check confirms that the tuning layer, viewer, dashboard tab, reports, outputs, and documentation are present.

## Added file

```text
app\run_paid_simulator_phase2d_integration_readiness_check.py
```

## Expected existing Phase 2D files

```text
app\paid_simulator\premium_model_tuning.py
app\paid_simulator\phase2d_premium_tuning_viewer.py
app\run_paid_simulator_premium_model_tuning_check.py
app\run_paid_simulator_phase2d_premium_tuning_viewer.py
app\run_paid_simulator_phase2d_premium_tuning_viewer_check.py
app\run_paid_simulator_phase2d_tuning_pipeline_check.py
app\run_paid_simulator_phase2d_dashboard_tab_check.py
```

## Expected generated outputs

```text
config\premium_model_tuning_config.json
outputs\tables\paid_simulator\premium_model_tuning_recommendations.csv
outputs\reports\paid_simulator\premium_model_tuning_recommendations.html
outputs\reports\paid_simulator\premium_model_tuning_summary.txt
outputs\reports\paid_simulator\phase2d_premium_model_tuning_check_report.txt
outputs\reports\paid_simulator\phase2d_tuning_pipeline_report.txt
```

## Dashboard check

The script checks that the main dashboard contains markers for the Developer-view-only Phase 2D tuning tab. The tab should remain hidden from Customer view.

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2d_integration_readiness_check.py
```

Expected final line:

```text
Overall Phase 2D integration-readiness status: PASS
```

## Output report

The check writes:

```text
outputs\reports\paid_simulator\phase2d_integration_readiness_report.txt
```

## Meaning of PASS

A PASS means the Phase 2D tuning layer is structurally connected. It does not mean the premium model has been fully calibrated to market option chains. Calibration is a later modeling step.
