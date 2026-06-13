# Phase 3B scenario-overlay viewer

This package adds a standalone Streamlit viewer for the Phase 3B scenario-overlay results.

## Added files

```text
app\paid_simulator\phase3_scenario_overlay_viewer.py
app\run_paid_simulator_phase3_scenario_overlay_viewer.py
app\run_paid_simulator_phase3_scenario_overlay_viewer_check.py
docs\paid_simulator_phase3_scenario_overlay_viewer.md
```

## Purpose

The viewer lets the developer inspect how the current interactive covered-call setup behaves across simple price scenarios. It is separate from the main dashboard and is not customer-facing.

## Inputs

```text
outputs\tables\paid_simulator\phase3_scenario_overlay.csv
outputs\reports\paid_simulator\phase3_scenario_overlay_summary.txt
outputs\tables\paid_simulator\phase3_interactive_payoff_snapshot.csv
```

The payoff snapshot is optional. If no setup has been saved from the Phase 3 interactive payoff viewer, the scenario-overlay model can still use its default SPY demo setup.

## Outputs

The viewer check writes:

```text
outputs\reports\paid_simulator\phase3_scenario_overlay_viewer_check_report.txt
```

## Test

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3_scenario_overlay_viewer_check.py
```

Expected:

```text
Overall Phase 3B scenario-overlay viewer status: PASS
```

## Open viewer

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3_scenario_overlay_viewer.py
```

## Notes

This is a developer inspection layer. It does not promote the scenario overlay to the customer dashboard and it does not use live market data.
