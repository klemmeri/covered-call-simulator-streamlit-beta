# Phase 5-18 — Historical-Mode Engine Regression Test

This checkpoint verifies that the controlled historical-import runner path remains operational after Phase 5-17.

It does not patch the dashboard and does not replace any additional live core engine files.

## Purpose

The regression verifies:

- synthetic mode remains the default;
- historical-import mode remains explicit only;
- the historical path artifact can still be read;
- start and end prices are positive;
- the runner path has enough rows to support downstream integration;
- no additional live core engine replacement is performed by this checkpoint.

## Files added

- `app/paid_simulator/phase5_historical_mode_engine_regression.py`
- `app/run_paid_simulator_phase5_18_historical_mode_engine_regression_check.py`
- `docs/phase5_18_historical_mode_engine_regression.md`

## Outputs

- `outputs/tables/paid_simulator/phase5_18_historical_mode_engine_regression_rows.csv`
- `outputs/tables/paid_simulator/phase5_18_historical_mode_engine_regression_summary.csv`
- `outputs/reports/paid_simulator/phase5_18_historical_mode_engine_regression.json`
- `outputs/reports/paid_simulator/phase5_18_historical_mode_engine_regression_report.txt`

## Expected checkpoint result

`Overall Phase 5-18 checkpoint status: PASS`
