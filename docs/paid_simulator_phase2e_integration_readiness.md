# Phase 2E Controlled Premium-Adjustment Integration Readiness

This checkpoint verifies that the Phase 2E controlled premium-adjustment layer is installed and connected.

## Purpose

Phase 2E applies a conservative, separate premium adjustment rather than replacing the original premium model. This keeps the original Phase 2B/2C/2D outputs intact while letting us compare adjusted premiums and adjusted payoff results before promoting any model change.

The integration-readiness check confirms that the adjustment module, adjusted payoff comparison, viewer, dashboard tab, reports, outputs, and documentation are present.

## Added file

```text
app\run_paid_simulator_phase2e_integration_readiness_check.py
```

## Expected existing Phase 2E files

```text
app\paid_simulator\premium_model_adjustment.py
app\paid_simulator\adjusted_premium_payoff_comparison.py
app\paid_simulator\phase2e_adjustment_viewer.py
app\run_paid_simulator_premium_model_adjustment_check.py
app\run_paid_simulator_adjusted_premium_payoff_comparison_check.py
app\run_paid_simulator_phase2e_adjustment_viewer.py
app\run_paid_simulator_phase2e_adjustment_viewer_check.py
app\run_paid_simulator_phase2e_adjustment_pipeline_check.py
app\run_paid_simulator_phase2e_dashboard_tab_check.py
```

## Expected generated outputs

```text
config\premium_model_adjustment_config.json
outputs\tables\paid_simulator\premium_model_adjusted_premiums.csv
outputs\reports\paid_simulator\premium_model_adjustment_comparison.html
outputs\reports\paid_simulator\premium_model_adjustment_summary.txt
outputs\tables\paid_simulator\adjusted_premium_payoff_comparison.csv
outputs\reports\paid_simulator\adjusted_premium_payoff_comparison.html
outputs\reports\paid_simulator\adjusted_premium_payoff_summary.txt
outputs\reports\paid_simulator\phase2e_adjustment_pipeline_report.txt
```

## Dashboard check

The script checks that the main dashboard contains markers for the Developer-view-only Phase 2E adjustment tab. The tab should remain hidden from Customer view.

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2e_integration_readiness_check.py
```

Expected final line:

```text
Overall Phase 2E integration-readiness status: PASS
```

## Output report

The check writes:

```text
outputs\reports\paid_simulator\phase2e_integration_readiness_report.txt
```

## Meaning of PASS

A PASS means the Phase 2E controlled adjustment layer is structurally connected. It does not mean the premium model is final or calibrated to live option-chain data. It means the adjustment workflow is safe to inspect and ready for the Phase 2E checkpoint.
