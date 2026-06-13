# Phase 3D Integrated Payoff Overlay Viewer

## Purpose

This package introduces the first Phase 3D prototype: an integrated covered-call payoff and scenario-overlay viewer.

It combines two prior Phase 3 workstreams:

1. The richer covered-call payoff interface from Phase 3C.
2. The scenario-overlay stress-test table from Phase 3B.

The goal is to let the user enter one covered-call setup and inspect both the graphical payoff behavior and scenario stress-test behavior in one place.

## Added files

```text
app\paid_simulator\phase3d_integrated_payoff_overlay_viewer.py
app\run_paid_simulator_phase3d_integrated_overlay_viewer.py
app\run_paid_simulator_phase3d_integrated_overlay_viewer_check.py
docs\paid_simulator_phase3d_integrated_payoff_overlay_viewer.md
```

## Outputs

After the user opens the viewer and clicks **Save Phase 3D snapshot**, the viewer writes:

```text
outputs\tables\paid_simulator\phase3d_integrated_payoff_overlay_snapshot.csv
outputs\reports\paid_simulator\phase3d_integrated_payoff_overlay_snapshot.html
```

These outputs are optional during installation checks because they do not exist until the user saves a setup.

## How to test

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3d_integrated_overlay_viewer_check.py
```

Expected status:

```text
Overall Phase 3D integrated viewer status: PASS
```

or:

```text
Overall Phase 3D integrated viewer status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```

The optional snapshot review is acceptable until a setup is saved from the viewer.

## How to open the viewer

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3d_integrated_overlay_viewer.py
```

## Notes

This is a Developer-view prototype. It does not use live market data, does not connect to an option chain, and does not issue trade recommendations. It is intended to validate the interaction pattern before a customer-facing implementation is considered.
