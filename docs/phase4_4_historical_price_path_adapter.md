# Phase 4-4 — Historical Price Path Input Adapter

## Purpose

Phase 4-4 adds the first safe adapter that converts imported underlying-price CSV data into a historical price-path table that can later be connected to the Covered Call Simulator engine.

This is not yet full production data integration. It is a controlled bridge between the Phase 4 market-data scaffold and future simulator execution using imported market history.

## Files added

```text
app\paid_simulator\phase4_historical_price_path_adapter.py
app\run_paid_simulator_phase4_4_historical_price_path_adapter_check.py
docs\phase4_4_historical_price_path_adapter.md
```

## Dashboard impact

No dashboard change is made in this phase.

```text
DASHBOARD_CHANGE_REQUIRED = False
```

## Input used

The adapter uses:

```text
inputs\market_data\sample_underlying_prices.csv
```

This file was created by Phase 4-2. If it is missing, the adapter creates a small deterministic fallback sample so the checkpoint can still run. In normal project use, the Phase 4-2 sample should already exist.

## Main output files

The adapter writes:

```text
outputs\tables\paid_simulator\phase4_4_historical_price_path.csv
outputs\tables\paid_simulator\phase4_4_normalized_underlying_prices.csv
outputs\tables\paid_simulator\phase4_4_historical_price_path_summary.csv
outputs\reports\paid_simulator\phase4_4_historical_price_path_adapter.json
outputs\reports\paid_simulator\phase4_4_historical_price_path_adapter_report.txt
```

The path CSV contains:

```text
path_id
source_mode
ticker
step
date
price
open
high
low
close
daily_return
cumulative_return
```

## Design intent

Phase 4-4 keeps synthetic simulation untouched. The goal is simply to create a clean historical path representation that a later phase can use as an alternative price-path source.

Later phases can extend this by:

1. Adding a simulator input switch between synthetic and historical paths.
2. Creating rolling historical windows.
3. Feeding historical paths into strategy comparison reports.
4. Combining historical prices with option-chain premium lookup.

## Release decision

```text
PHASE4_4_HISTORICAL_PRICE_PATH_ADAPTER_CREATED_NO_DASHBOARD_CHANGE
```

## Check script

Run:

```text
app\run_paid_simulator_phase4_4_historical_price_path_adapter_check.py
```

Expected final line:

```text
Overall Phase 4-4 checkpoint status: PASS
```
