# Phase 3D Integrated Overlay Integration-Readiness Check

This add-only package verifies that the Phase 3D integrated payoff-overlay layer is installed and connected.

## Added file

```text
app\run_paid_simulator_phase3d_integration_readiness_check.py
```

## Purpose

Phase 3D combines the richer graphical payoff interface with the scenario-overlay stress-test layer. The integration-readiness checker confirms that the standalone viewer, pipeline checker, Developer-view dashboard tab, context outputs, and documentation are connected before the project moves to the next interactive dashboard step.

## What it checks

```text
Phase 3D integrated payoff-overlay viewer
Phase 3D viewer launcher
Phase 3D viewer check
Phase 3D integrated overlay pipeline check
Phase 3D dashboard-tab check
Main dashboard app
Phase 3D documentation
Phase 3B scenario-overlay context outputs
Phase 3B and Phase 3C checkpoint context
Main dashboard Phase 3 / 3B / 3C / 3D markers
Optional Phase 3D saved snapshot outputs
```

## Output report

The checker writes:

```text
outputs\reports\paid_simulator\phase3d_integration_readiness_report.txt
```

## Expected status

A clean run should report one of these:

```text
Overall Phase 3D integration-readiness status: PASS
```

or:

```text
Overall Phase 3D integration-readiness status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```

The optional snapshot review is acceptable until a setup has been saved from the Phase 3D integrated payoff-overlay viewer.

## Run from PyCharm

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3d_integration_readiness_check.py
```

## Design note

The Phase 3D integrated overlay remains Developer-view only at this stage. It is not yet promoted into the customer-facing dashboard.
