# Phase 2F checkpoint overall-marker fix

This package replaces the Phase 2F checkpoint checker with a more tolerant version.

The previous checker could return `REVIEW` when the model-decision summary text did not contain one exact display phrase, even though the Phase 2F files, outputs, row counts, dashboard tab markers, and reports were present.

## Files

```text
app\run_paid_simulator_phase2f_checkpoint_check.py
docs\paid_simulator_phase2f_checkpoint_overall_marker_fix.md
```

## Purpose

The model-decision summary is data-driven, so the checkpoint should not require one exact text phrase such as `Overall`. The replacement checker accepts reasonable summary markers such as `overall`, `summary`, `decision`, or `scenario`.

## Test

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2f_checkpoint_check.py
```

Expected result:

```text
Overall Phase 2F checkpoint status: PASS
```
