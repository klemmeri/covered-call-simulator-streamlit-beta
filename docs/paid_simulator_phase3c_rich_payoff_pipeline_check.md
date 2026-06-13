# Phase 3C Rich Payoff Pipeline Check

This document describes the Phase 3C rich payoff-viewer pipeline checker.

## Purpose

Phase 3C introduces a richer graphical covered-call payoff viewer. The pipeline checker verifies that the viewer is installed, that its own check script can run, and that optional saved snapshot outputs are handled safely.

This phase remains a developer-facing prototype. It does not replace the customer dashboard workflow.

## Files added

```text
app\run_paid_simulator_phase3c_rich_payoff_pipeline_check.py
docs\paid_simulator_phase3c_rich_payoff_pipeline_check.md
```

## What the checker verifies

The checker looks for:

```text
app\paid_simulator\phase3c_rich_payoff_viewer.py
app\run_paid_simulator_phase3c_rich_payoff_viewer.py
app\run_paid_simulator_phase3c_rich_payoff_viewer_check.py
docs\paid_simulator_phase3c_rich_payoff_viewer.md
```

It also checks Phase 3B context files when available and runs:

```text
app\run_paid_simulator_phase3c_rich_payoff_viewer_check.py
```

## Optional snapshot files

The following files are optional because they are created only after a user opens the Phase 3C viewer and saves/exports a setup:

```text
outputs\tables\paid_simulator\phase3c_rich_payoff_snapshot.csv
outputs\reports\paid_simulator\phase3c_rich_payoff_snapshot.html
```

A missing snapshot should not block the pipeline.

## Output

The checker writes:

```text
outputs\reports\paid_simulator\phase3c_rich_payoff_pipeline_report.txt
```

## Expected result

If no setup has been saved yet, either of these is acceptable:

```text
Overall Phase 3C rich payoff pipeline status: PASS
Overall Phase 3C rich payoff pipeline status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```

The optional snapshot review simply means no interactive setup has been saved yet.
