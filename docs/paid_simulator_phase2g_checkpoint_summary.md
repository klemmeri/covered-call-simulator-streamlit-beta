# Phase 2G Checkpoint Summary

## Purpose

Phase 2G is the controlled model-promotion planning milestone for the paid covered-call simulator.

The goal of this phase is not to expose a new model to customers. The goal is to decide, internally and cautiously, whether the adjusted premium model should remain a research model or become a candidate for a promoted internal model layer.

## Files added by this package

```text
app\run_paid_simulator_phase2g_checkpoint_check.py
docs\paid_simulator_phase2g_checkpoint_summary.md
```

## What the checkpoint verifies

The checkpoint verifies that the Phase 2B through Phase 2G modeling chain is present and connected:

```text
Option-premium model
Premium-aware payoff runner
Premium-vs-scaffold comparison
Premium-model validation module
Premium-model tuning module
Premium-model adjustment module
Adjusted-premium payoff comparison module
Model-decision summary module
Model-promotion planning module
Phase 2G model-promotion viewer
Phase 2G model-promotion pipeline check
Phase 2G dashboard tab
Phase 2G integration-readiness check
Phase 2B through Phase 2F context outputs
Phase 2G CSV/HTML/text outputs
Phase 2G documentation
Main dashboard Phase 2G tab markers
```

## Expected output

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2g_checkpoint_check.py
```

Expected final line:

```text
Overall Phase 2G checkpoint status: PASS
```

The checker writes:

```text
outputs\reports\paid_simulator\phase2g_checkpoint_report.txt
```

## Interpretation

A PASS means the Phase 2G model-promotion planning layer is installed, the generated outputs exist, the tables have rows, and the main dashboard contains the Developer-view Phase 2G tab markers.

This does not mean the adjusted premium model has been promoted to customer-facing status. It only means the internal promotion-planning framework is ready.

## Next phase

After Phase 2G passes, the next major project block is Phase 3: the interactive Pro graphical dashboard.

Planned Phase 3 features include:

```text
Visual running ticker interface
User-selected covered-call details
Dynamic payoff graph
Strike marker
Break-even marker
Assignment-zone display
Buy-and-hold comparison line
Covered-call payoff line
Scenario stress-test overlays
Trade-management recommendation panel
```
