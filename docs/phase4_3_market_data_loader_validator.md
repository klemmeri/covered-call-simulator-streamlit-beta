# Phase 4-3 — Market-Data Loader and Schema Validator

## Purpose

Phase 4-3 adds the first real market-data loading and validation layer for the Covered Call Simulator paid-version modeling path.

This phase does **not** modify the Streamlit dashboard. It is an add-only checkpoint that prepares the project to safely consume imported market data in later Phase 4 steps.

## Files added

```text
app\paid_simulator\phase4_market_data_loader_validator.py
app\run_paid_simulator_phase4_3_market_data_loader_validator_check.py
docs\phase4_3_market_data_loader_validator.md
```

## Inputs consumed

The validator reads the sample data files created by Phase 4-2:

```text
inputs\market_data\sample_underlying_prices.csv
inputs\market_data\sample_option_chain.csv
```

## Outputs created

```text
outputs\reports\paid_simulator\phase4_3_market_data_validation.json
outputs\reports\paid_simulator\phase4_3_market_data_validation_report.txt
outputs\tables\paid_simulator\phase4_3_market_data_validation_summary.csv
outputs\tables\paid_simulator\phase4_3_market_data_validation_issues.csv
outputs\reports\paid_simulator\phase4_3_market_data_loader_validator_checkpoint_report.txt
outputs\reports\paid_simulator\phase4_3_market_data_loader_validator_checkpoint.json
```

## Validation rules

### Underlying price file

Required columns:

```text
date
ticker
open
high
low
close
volume
```

Core checks:

- File exists.
- Required columns are present.
- Date column is parseable.
- Open, high, low, close, and volume are numeric.
- Open, high, low, close, and volume are non-negative.
- High is not below open, close, or low.
- Low is not above open, close, or high.

### Option-chain file

Required columns:

```text
quote_date
ticker
expiration_date
option_type
strike
bid
ask
mid
delta
iv
volume
open_interest
```

Core checks:

- File exists.
- Required columns are present.
- Quote and expiration dates are parseable.
- Strike, bid, ask, mid, delta, IV, volume, and open interest are numeric.
- Strike, bid, ask, mid, IV, volume, and open interest are non-negative.
- Option type is C, P, CALL, or PUT.
- Bid is not greater than ask.
- Mid is inside the bid/ask range, with violations reported as warnings.
- Delta is between -1 and +1.
- IV is non-negative.

## Release markers

```text
PHASE4_3_MARKET_DATA_LOADER_VALIDATOR_READY
PHASE4_3_MARKET_DATA_LOADER_VALIDATOR_CREATED_NO_DASHBOARD_CHANGE
```

## Interpretation

This phase is a data-quality gate. It verifies that imported market-data CSVs are structurally usable before future Phase 4 modules use them for historical-path input, option-chain premium lookup, calibration reports, or imported-data strategy comparison.

This phase is not a regime detector and should not be presented as market guidance. Regime detection remains a probabilistic scenario input, not an oracle.

## How to run the checkpoint

In PyCharm, run:

```text
app\run_paid_simulator_phase4_3_market_data_loader_validator_check.py
```

Expected final line:

```text
Overall Phase 4-3 checkpoint status: PASS
```

## Next recommended checkpoint

After Phase 4-3 passes, the next logical checkpoint is:

```text
Phase 4-4 — Historical price path input adapter
```

That checkpoint should allow the simulator to use imported historical price paths while preserving synthetic-path mode as the fallback.
