# Phase 5-5 — Historical-Mode Simulation Smoke Test

## Purpose

Phase 5-5 verifies that the controlled historical-path integration artifacts can feed a small deterministic covered-call comparison.

This is not the final production simulator integration. It is a smoke test proving that the imported historical path and best available option-chain candidate can be read, normalized, and used in a buy-and-hold versus covered-call comparison.

## Scope

This checkpoint is add-only.

It does not change the dashboard.
It does not make historical mode the default.
It does not expose historical mode to public/customer workflow yet.

## Files added

```text
app\paid_simulator\phase5_historical_mode_simulation_smoke_test.py
app\run_paid_simulator_phase5_5_historical_mode_smoke_test_check.py
docs\phase5_5_historical_mode_simulation_smoke_test.md
```

## Outputs created

```text
outputs\tables\paid_simulator\phase5_5_historical_mode_smoke_test_rows.csv
outputs\tables\paid_simulator\phase5_5_historical_mode_smoke_test_summary.csv
outputs\reports\paid_simulator\phase5_5_historical_mode_smoke_test.json
outputs\reports\paid_simulator\phase5_5_historical_mode_smoke_test_report.txt
```

## Design notes

The smoke test uses 100 shares, the first and last available historical prices, and the best available covered-call candidate from the Phase 4-5 option-chain scaffold.

It computes a simple buy-and-hold terminal value and a simple covered-call terminal value. Assignment is represented by capping the stock terminal value at the option strike and adding option premium income.

This provides a deterministic integration check before patching the main simulator engine.

## Release decision

```text
PHASE5_5_HISTORICAL_MODE_SMOKE_TEST_CREATED_NO_DASHBOARD_CHANGE
```
