# Phase 3B Scenario-Overlay Integration Readiness

This package adds an integration-readiness check for the Phase 3B scenario-overlay layer of the Covered Call Simulator.

## Added files

```text
app\run_paid_simulator_phase3b_integration_readiness_check.py
docs\paid_simulator_phase3b_integration_readiness.md
```

## Purpose

Phase 3B adds a scenario-overlay layer to the interactive covered-call payoff prototype. The overlay stress-tests the entered covered-call setup across simple price scenarios such as pullback, flat/pin, strike test, and strong rally.

The integration-readiness checker verifies that the Phase 3B pieces are installed and connected before more interactive graphics are added.

## What the checker verifies

```text
Phase 3B scenario-overlay model
Phase 3B scenario-overlay viewer
Phase 3B scenario-overlay pipeline checker
Phase 3B dashboard tab
Phase 3B output CSV/HTML/text report
Phase 3B documentation
Main dashboard tab markers
Optional interactive payoff snapshot outputs
```

## Expected outputs

The checker writes:

```text
outputs\reports\paid_simulator\phase3b_integration_readiness_report.txt
```

## Expected status

The preferred final status is:

```text
Overall Phase 3B integration-readiness status: PASS
```

This status is also acceptable:

```text
Overall Phase 3B integration-readiness status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```

The optional snapshot review simply means that no Phase 3 interactive payoff setup has been saved/exported yet. That is not a blocking issue.

## Installation

Extract this package directly into the project root:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Allow Windows to merge folders.

## Test command

Run this file in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3b_integration_readiness_check.py
```
