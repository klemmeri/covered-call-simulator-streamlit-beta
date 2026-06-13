# Phase 2F Model-Decision Integration Readiness

This checkpoint verifies that the Phase 2F model-decision layer is installed and connected.

## Purpose

Phase 2F consolidates the evidence from the original premium-aware model, adjusted-premium model, validation checks, tuning recommendations, and adjusted-payoff comparison into one internal model-decision report.

The integration-readiness check confirms that the model-decision module, viewer, pipeline, dashboard tab, reports, outputs, and documentation are present.

## Added file

```text
app\run_paid_simulator_phase2f_integration_readiness_check.py
```

## Expected existing Phase 2F files

```text
app\paid_simulator\model_decision_summary.py
app\paid_simulator\phase2f_model_decision_viewer.py
app\run_paid_simulator_model_decision_summary_check.py
app\run_paid_simulator_phase2f_model_decision_viewer.py
app\run_paid_simulator_phase2f_model_decision_viewer_check.py
app\run_paid_simulator_phase2f_model_decision_pipeline_check.py
app\run_paid_simulator_phase2f_dashboard_tab_check.py
```

## Expected generated outputs

```text
outputs\tables\paid_simulator\model_decision_summary.csv
outputs\reports\paid_simulator\model_decision_summary.html
outputs\reports\paid_simulator\model_decision_summary.txt
outputs\reports\paid_simulator\phase2f_model_decision_summary_check_report.txt
outputs\reports\paid_simulator\phase2f_model_decision_viewer_check_report.txt
outputs\reports\paid_simulator\phase2f_model_decision_pipeline_report.txt
```

The checker also verifies the context outputs from Phase 2B through Phase 2E, including option premiums, premium-aware payoff results, validation results, tuning recommendations, adjusted premiums, and adjusted-payoff comparison.

## Dashboard check

The script checks that the main dashboard contains markers for the Developer-view-only Phase 2F model-decision tab. The tab should remain hidden from Customer view.

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2f_integration_readiness_check.py
```

Expected final line:

```text
Overall Phase 2F integration-readiness status: PASS
```

## Output report

The check writes:

```text
outputs\reports\paid_simulator\phase2f_integration_readiness_report.txt
```

## Meaning of PASS

A PASS means the Phase 2F model-decision layer is structurally connected. It does not mean the premium model is final, calibrated to live option-chain data, or ready for customer-facing promotion. It means the internal decision summary is installed and ready for the Phase 2F checkpoint.
