# Phase 2F Viewer Marker Fix

This package fixes a strict marker check in the Phase 2F model-decision viewer checker.

## Issue

The previous checker required this exact phrase to appear in the viewer source file:

```text
CANDIDATE FOR CONTROLLED PROMOTION
```

That was too strict because the viewer can display decision labels from the model-decision CSV rather than hard-coding every possible label in the source code.

## Fix

The replacement checker still verifies the important viewer structure:

- Phase 2F viewer app exists
- Phase 2F viewer launcher exists
- Phase 2F viewer documentation exists
- model-decision outputs exist
- context CSV files exist
- `model_decision_summary.csv` has rows
- the viewer contains key structural markers such as `Model decisions`, `Promotion candidates`, and `model_decision_summary.csv`

The exact label `CANDIDATE FOR CONTROLLED PROMOTION` is now treated as optional/data-driven.

## Replaced file

```text
app\run_paid_simulator_phase2f_model_decision_viewer_check.py
```

## Run

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2f_model_decision_viewer_check.py
```

Expected result:

```text
Overall Phase 2F model-decision viewer status: PASS
```
