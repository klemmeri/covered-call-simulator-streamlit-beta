# Phase 2 vs v0 Comparison Adapter

This add-only scaffold compares the existing v0.1 paid-simulator scenario output with the new Phase 2 scenario-payoff report scaffold.

## Files added

```text
app\paid_simulator\phase2_v0_comparison_adapter.py
app\run_paid_simulator_phase2_v0_comparison_check.py
docs\paid_simulator_phase2_v0_comparison_adapter.md
```

## Inputs

```text
outputs\tables\paid_simulator\scenario_comparison.csv
outputs\tables\paid_simulator\scenario_payoff_report_scaffold.csv
```

## Outputs

```text
outputs\tables\paid_simulator\phase2_v0_comparison_scaffold.csv
outputs\reports\paid_simulator\phase2_v0_comparison_scaffold.html
```

## Purpose

The adapter shows whether the Phase 2 scaffold is broadly consistent with the current v0.1 simulator output, scenario by scenario. It is not yet customer-facing. It is a development bridge for deciding how to replace or supplement the v0.1 scenario logic later.

## How to test

Run this from PyCharm:

```text
app\run_paid_simulator_phase2_v0_comparison_check.py
```

Expected result:

```text
Overall Phase 2 vs v0 comparison status: PASS
```

## Notes

This scaffold does not modify the dashboard, the v0.1 simulator engine, or the paid simulator config.
