# Paid Simulator Phase 2 Scaffold Viewer

## Purpose

This add-on creates a standalone Streamlit viewer for the Phase 2 modeling scaffold outputs.
It does not replace or modify the v0.1 paid simulator dashboard.

## Added files

```text
app\paid_simulator\phase2_scaffold_viewer.py
app\run_paid_simulator_phase2_viewer.py
app\run_paid_simulator_phase2_viewer_check.py
docs\paid_simulator_phase2_scaffold_viewer.md
```

## Viewer tabs

```text
Overview
Scenario payoffs
Phase 2 vs v0
Price paths
```

## Expected inputs

```text
outputs\tables\paid_simulator\scenario_price_paths_scaffold.csv
outputs\tables\paid_simulator\option_payoff_scaffold.csv
outputs\tables\paid_simulator\scenario_payoff_scaffold.csv
outputs\tables\paid_simulator\scenario_payoff_report_scaffold.csv
outputs\reports\paid_simulator\scenario_payoff_report_scaffold.html
outputs\tables\paid_simulator\phase2_v0_comparison_scaffold.csv
outputs\reports\paid_simulator\phase2_v0_comparison_scaffold.html
```

## How to run

Run this from PyCharm:

```text
app\run_paid_simulator_phase2_viewer.py
```

Run this checker from PyCharm:

```text
app\run_paid_simulator_phase2_viewer_check.py
```

## Notes

This viewer is a development bridge. Once the Phase 2 scaffold outputs are stable,
the same summary panels can be integrated into the main paid simulator dashboard,
probably as a Developer-view-only Phase 2 tab first.
