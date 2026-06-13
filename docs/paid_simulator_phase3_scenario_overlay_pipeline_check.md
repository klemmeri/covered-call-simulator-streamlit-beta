# Phase 3B Scenario-Overlay Pipeline Check

This package adds a pipeline checker for the Phase 3B scenario-overlay layer.

## Added file

```text
app\run_paid_simulator_phase3_scenario_overlay_pipeline_check.py
docs\paid_simulator_phase3_scenario_overlay_pipeline_check.md
```

## Purpose

The Phase 3B scenario-overlay model extends the interactive payoff prototype by stress-testing the user-entered covered-call setup across several simple price scenarios.

This checker confirms that the Phase 3B model, viewer, documentation, and generated outputs are present and connected.

## What the checker runs

```text
app\run_paid_simulator_phase3_scenario_overlay_check.py
app\run_paid_simulator_phase3_scenario_overlay_viewer_check.py
```

## Outputs verified

```text
outputs\tables\paid_simulator\phase3_scenario_overlay.csv
outputs\reports\paid_simulator\phase3_scenario_overlay.html
outputs\reports\paid_simulator\phase3_scenario_overlay_summary.txt
```

The following files are optional because they are created only after a user saves or exports an interactive payoff setup from the Phase 3 viewer:

```text
outputs\tables\paid_simulator\phase3_interactive_payoff_snapshot.csv
outputs\reports\paid_simulator\phase3_interactive_payoff_snapshot.html
```

## Report written

```text
outputs\reports\paid_simulator\phase3b_scenario_overlay_pipeline_report.txt
```

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3_scenario_overlay_pipeline_check.py
```

Expected result:

```text
Overall Phase 3B scenario-overlay pipeline status: PASS
```

or:

```text
Overall Phase 3B scenario-overlay pipeline status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```

The optional snapshot review is acceptable if no interactive payoff setup has been saved yet.
