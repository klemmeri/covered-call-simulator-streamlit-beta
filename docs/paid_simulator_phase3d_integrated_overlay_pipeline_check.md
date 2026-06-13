# Phase 3D Integrated Payoff-Overlay Pipeline Check

This add-only package verifies that the Phase 3D integrated payoff-overlay viewer is installed and connected to the existing Phase 3B and Phase 3C context.

## Added files

```text
app\run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py
docs\paid_simulator_phase3d_integrated_overlay_pipeline_check.md
```

## Purpose

Phase 3D combines the richer covered-call payoff graph with the scenario-overlay stress-test layer. This checker confirms that the standalone viewer and its dependencies are present before the feature is later connected to the main dashboard.

## What it checks

```text
Phase 3D integrated viewer app
Phase 3D integrated viewer launcher
Phase 3D integrated viewer check
Phase 3D documentation
Phase 3B scenario-overlay outputs
Phase 3B checkpoint context
Phase 3C checkpoint context
Phase 3D viewer-check execution
Optional saved Phase 3D snapshot outputs
Viewer source markers
```

## Output report

The checker writes:

```text
outputs\reports\paid_simulator\phase3d_integrated_overlay_pipeline_report.txt
```

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py
```

Expected status:

```text
Overall Phase 3D integrated overlay pipeline status: PASS
```

or:

```text
Overall Phase 3D integrated overlay pipeline status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```

The optional snapshot review is acceptable until a setup has been saved from the Phase 3D integrated viewer.
