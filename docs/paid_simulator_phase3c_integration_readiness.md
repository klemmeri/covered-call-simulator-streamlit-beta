# Phase 3C Rich Payoff Integration-Readiness Check

This document describes the Phase 3C integration-readiness checker for the Covered Call Strategy Stress Test paid simulator.

## Purpose

Phase 3C adds a richer graphical covered-call payoff prototype. The integration-readiness checker verifies that the standalone viewer, pipeline checker, Developer-view dashboard tab, and documentation are all connected before the project moves to the next graphical interface step.

## Added file

```text
app\run_paid_simulator_phase3c_integration_readiness_check.py
```

## Checker output

The checker writes:

```text
outputs\reports\paid_simulator\phase3c_integration_readiness_report.txt
```

## What it checks

The checker verifies:

```text
Phase 3C rich payoff viewer
Phase 3C viewer launcher
Phase 3C viewer check
Phase 3C pipeline check
Phase 3C dashboard-tab check
Main dashboard app
Phase 3C documentation
Main dashboard Phase 3 / 3B / 3C markers
Optional saved Phase 3C payoff snapshot outputs
```

## Expected status

A clean run should report one of the following:

```text
Overall Phase 3C integration-readiness status: PASS
```

or:

```text
Overall Phase 3C integration-readiness status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```

The optional snapshot review is acceptable if the Phase 3C viewer has not yet been opened and a setup has not yet been saved/exported.

## Run from PyCharm

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3c_integration_readiness_check.py
```

## Design note

The Phase 3C rich payoff interface remains Developer-view only at this stage. It is not yet promoted into the customer-facing dashboard.
