# Phase 5-5 Historical-Mode Smoke Test Strategy Row-Count Repair

This repair keeps the Phase 5-5 price-column fix and explicitly reports the strategy comparison row count expected by the checkpoint script.

## Replaced file

- `app\paid_simulator\phase5_historical_mode_simulation_smoke_test.py`

## Purpose

The previous repair correctly restored positive `start_price` and `end_price` values, but the checkpoint still failed because the summary dictionary did not expose the expected strategy-comparison row-count field.

This repair writes the comparison rows CSV and includes these row-count fields in the summary payload:

- `strategy_comparison_rows`
- `comparison_rows`
- `smoke_test_rows`
- `row_count`

## Scope

- No dashboard change.
- Synthetic mode remains the default.
- Historical import remains explicit-only.
- This is still a smoke test, not a full production engine replacement.
