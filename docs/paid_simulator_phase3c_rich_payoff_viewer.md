# Phase 3C Rich Payoff Viewer

This package adds a standalone richer graphical covered-call payoff viewer.

## Purpose

Phase 3C improves the interactive graphical prototype before integrating it into the main dashboard. The viewer lets the user enter a covered-call setup and inspect a richer payoff chart, scenario overlay, payoff grid, and exportable snapshot.

## Added files

```text
app\paid_simulator\phase3c_rich_payoff_viewer.py
app\run_paid_simulator_phase3c_rich_payoff_viewer.py
app\run_paid_simulator_phase3c_rich_payoff_viewer_check.py
docs\paid_simulator_phase3c_rich_payoff_viewer.md
```

## Outputs created after saving a setup

```text
outputs\tables\paid_simulator\phase3c_rich_payoff_snapshot.csv
outputs\reports\paid_simulator\phase3c_rich_payoff_snapshot.html
outputs\reports\paid_simulator\phase3c_rich_payoff_viewer_check_report.txt
```

The snapshot files are optional until the viewer is opened and a setup is saved.

## Test

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3c_rich_payoff_viewer_check.py
```

Expected:

```text
Overall Phase 3C rich payoff viewer status: PASS
```

or:

```text
Overall Phase 3C rich payoff viewer status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```

The optional snapshot review is acceptable before saving a setup.

## Open viewer

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3c_rich_payoff_viewer.py
```

## Notes

This is still a prototype. It uses manual inputs and does not yet use live market data, option-chain imports, dividends, taxes, or assignment-probability modeling.
