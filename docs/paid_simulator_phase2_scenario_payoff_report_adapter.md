# Phase 2 Scenario-Payoff Report Adapter Scaffold

This add-only scaffold converts the Phase 2 scenario-payoff output into a cleaner report table and a simple HTML report.

## Added files

```text
app\paid_simulator\scenario_payoff_report_adapter.py
app\run_paid_simulator_scenario_payoff_report_check.py
docs\paid_simulator_phase2_scenario_payoff_report_adapter.md
```

## Input

```text
outputs\tables\paid_simulator\scenario_payoff_scaffold.csv
```

This file should be created by:

```text
app\run_paid_simulator_scenario_payoff_check.py
```

## Outputs

```text
outputs\tables\paid_simulator\scenario_payoff_report_scaffold.csv
outputs\reports\paid_simulator\scenario_payoff_report_scaffold.html
```

## Purpose

The adapter is a bridge between raw Phase 2 modeling scaffolds and a more customer/developer-readable scenario comparison table.
It does not replace the v0.1 paid simulator dashboard.

## Test

Run in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_scenario_payoff_report_check.py
```

Expected result:

```text
Overall scenario-payoff report status: PASS
```
