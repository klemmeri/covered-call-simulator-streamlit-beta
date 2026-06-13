# Phase 2F Model-Decision Pipeline Check

This add-only package adds a pipeline checker for the Phase 2F model-decision workflow.

## Added files

```text
app\run_paid_simulator_phase2f_model_decision_pipeline_check.py
docs\paid_simulator_phase2f_model_decision_pipeline_check.md
```

## Purpose

The checker runs the Phase 2F model-decision workflow and verifies that the consolidated model-decision outputs are present and non-empty.

It runs:

```text
Phase 2E checkpoint check, if present
Phase 2F model-decision summary check
Phase 2F model-decision viewer check
```

It verifies:

```text
outputs\tables\paid_simulator\model_decision_summary.csv
outputs\reports\paid_simulator\model_decision_summary.html
outputs\reports\paid_simulator\model_decision_summary.txt
outputs\reports\paid_simulator\phase2f_model_decision_summary_check_report.txt
outputs\reports\paid_simulator\phase2f_model_decision_viewer_check_report.txt
```

It also checks the major context files from earlier Phase 2B through Phase 2E work.

## Output report

The checker writes:

```text
outputs\reports\paid_simulator\phase2f_model_decision_pipeline_report.txt
```

## Expected result

```text
Overall Phase 2F model-decision pipeline status: PASS
```

## Notes

This checker does not change the customer-facing dashboard. It is another safety gate before integrating the Phase 2F model-decision layer into the Developer view of the main dashboard.
